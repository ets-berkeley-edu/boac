"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import json

from boac import db, std_commit
from boac.api.errors import InternalServerError
from boac.lib import util
from boac.lib.util import get_benchmarker
from boac.merged import athletics
from boac.merged.admitted_student import query_admitted_students
from boac.merged.calnet import get_csid_for_uid
from boac.merged.cohort_filter_options import CohortFilterOptions
from boac.merged.sis_terms import current_term_id
from boac.merged.student import query_students, scope_for_criteria
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.base import Base
from boac.models.cohort_filter_event import CohortFilterEvent
from boac.models.db_relationships import cohort_domain_type
from flask import current_app as app
from flask_login import current_user
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import deferred, undefer


class CohortFilter(Base):

    __tablename__ = 'cohort_filters'
    __transient_sids = []

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    domain = db.Column(cohort_domain_type, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    filter_criteria = db.Column(JSONB, nullable=False)
    # Fetching a large array literal from Postgres can be expensive. We defer until invoking code demands it.
    sids = deferred(db.Column(ARRAY(db.String(80))))
    student_count = db.Column(db.Integer)
    alert_count = db.Column(db.Integer)

    owner = db.relationship('AuthorizedUser', back_populates='cohort_filters')

    def __init__(self, domain, name, filter_criteria):
        self.domain = domain
        self.name = name
        self.filter_criteria = filter_criteria

    def __repr__(self):
        return f"""<CohortFilter {self.id},
            domain={self.domain},
            name={self.name},
            owner_id={self.owner_id},
            filter_criteria={self.filter_criteria},
            sids={self.sids},
            student_count={self.student_count},
            alert_count={self.alert_count},
            updated_at={self.updated_at},
            created_at={self.created_at}>"""

    @classmethod
    def create(cls, uid, name, filter_criteria, domain='default', **kwargs):
        if all(not isinstance(value, bool) and not value for value in filter_criteria.values()):
            raise InternalServerError('Cohort creation requires at least one filter specification.')
        cohort = cls(domain=domain, name=name, filter_criteria=filter_criteria)
        user = AuthorizedUser.find_by_uid(uid)
        user.cohort_filters.append(cohort)
        db.session.flush()
        std_commit()
        return cohort.to_api_json(**kwargs)

    @classmethod
    def update(cls, cohort_id, name=None, filter_criteria=None, alert_count=None, **kwargs):
        cohort = cls.query.filter_by(id=cohort_id).first()
        if name:
            cohort.name = name
        if filter_criteria:
            cohort.filter_criteria = filter_criteria
        cohort.clear_sids_and_student_count()
        if alert_count is not None:
            cohort.alert_count = alert_count
        else:
            # Alert count will be refreshed
            cohort.update_alert_count(None)
        std_commit()
        return cohort.to_api_json(**kwargs)

    @classmethod
    def get_sids(cls, cohort_id):
        query = db.session.query(cls).options(undefer('sids'))
        cohort = query.filter_by(id=cohort_id).first()
        return cohort and cohort.sids

    @classmethod
    def get_domain_of_cohort(cls, cohort_id):
        query = text('SELECT domain FROM cohort_filters WHERE id = :id')
        result = db.session.execute(query, {'id': cohort_id}).first()
        return result and result['domain']

    def clear_sids_and_student_count(self):
        self.__transient_sids = self.sids
        self.update_sids_and_student_count(None, None)

    def update_sids_and_student_count(self, sids, student_count):
        self.sids = sids
        self.student_count = student_count
        std_commit()
        return self

    def update_alert_count(self, count):
        self.alert_count = count
        std_commit()
        return self

    def track_membership_changes(self):
        # Track membership changes only if the cohort has been saved and has an id.
        if self.id:
            old_sids = set(self.__transient_sids)
            new_sids = set(self.sids)
            removed_sids = old_sids - new_sids
            added_sids = new_sids - old_sids
            CohortFilterEvent.create_bulk(self.id, added_sids, removed_sids)
        self.__transient_sids = []

    @classmethod
    def get_cohorts(cls, user_id):
        domain_clause = '' if app.config['FEATURE_FLAG_ADMITTED_STUDENTS'] else " AND c.domain = 'default'"
        query = text(f"""
            SELECT id, domain, name, filter_criteria, alert_count, student_count
            FROM cohort_filters c
            WHERE c.owner_id = :user_id {domain_clause}
            ORDER BY c.domain, c.name
        """)
        results = db.session.execute(query, {'user_id': user_id})

        def transform(row):
            return {
                'id': row['id'],
                'domain': row['domain'],
                'name': row['name'],
                'criteria': row['filter_criteria'],
                'alertCount': row['alert_count'],
                'totalStudentCount': row['student_count'],
            }
        return [transform(row) for row in results]

    @classmethod
    def get_cohorts_owned_by_uids(cls, uids):
        domain_clause = 'true' if app.config['FEATURE_FLAG_ADMITTED_STUDENTS'] else "c.domain = 'default'"
        query = text(f"""
            SELECT
            c.id, c.domain, c.name, c.filter_criteria, c.alert_count, c.student_count, u.uid
            FROM cohort_filters c
            INNER JOIN authorized_users u ON c.owner_id = u.id
            WHERE u.uid = ANY(:uids) AND {domain_clause}
            GROUP BY c.id, c.name, c.filter_criteria, c.alert_count, c.student_count, u.uid
        """)
        results = db.session.execute(query, {'uids': uids})

        def transform(row):
            return {
                'id': row['id'],
                'domain': row['domain'],
                'name': row['name'],
                'criteria': row['filter_criteria'],
                'ownerUid': row['uid'],
                'alertCount': row['alert_count'],
                'totalStudentCount': row['student_count'],
            }
        return [transform(row) for row in results]

    @classmethod
    def is_cohort_owned_by(cls, cohort_id, user_id):
        query = text("""
            SELECT count(*) FROM cohort_filters c
            WHERE c.owner_id = :user_id AND c.id = :cohort_id
        """)
        results = db.session.execute(
            query, {
                'cohort_id': cohort_id,
                'user_id': user_id,
            },
        )
        return results.first()['count']

    @classmethod
    def refresh_alert_counts_for_owner(cls, owner_id):
        query = text("""
            UPDATE cohort_filters
            SET alert_count = updated_cohort_counts.alert_count
            FROM
            (
                SELECT cohort_filters.id AS cohort_filter_id, count(*) AS alert_count
                FROM alerts
                JOIN cohort_filters
                    ON alerts.sid = ANY(cohort_filters.sids)
                    AND alerts.key LIKE :key
                    AND alerts.deleted_at IS NULL
                    AND cohort_filters.owner_id = :owner_id
                LEFT JOIN alert_views
                    ON alert_views.alert_id = alerts.id
                    AND alert_views.viewer_id = :owner_id
                WHERE alert_views.dismissed_at IS NULL
                GROUP BY cohort_filters.id
            ) updated_cohort_counts
            WHERE cohort_filters.id = updated_cohort_counts.cohort_filter_id
        """)
        result = db.session.execute(query, {'owner_id': owner_id, 'key': current_term_id() + '_%'})
        std_commit()
        return result

    @classmethod
    def find_by_id(cls, cohort_id, **kwargs):
        cohort = cls.query.filter_by(id=cohort_id).first()
        return cohort and cohort.to_api_json(**kwargs)

    @classmethod
    def delete(cls, cohort_id):
        cohort_filter = cls.query.filter_by(id=cohort_id).first()
        db.session.delete(cohort_filter)
        std_commit()

    def to_base_json(self):
        c = self.filter_criteria
        c = c if isinstance(c, dict) else json.loads(c)
        user_uid = self.owner.uid if self.owner else None
        option_groups = CohortFilterOptions(user_uid, scope_for_criteria()).get_filter_option_groups()
        for label, option_group in option_groups.items():
            for option in option_group:
                key = option['key']
                if key in c:
                    value = c.get(key)
                    if option['type']['db'] == 'boolean':
                        c[key] = util.to_bool_or_none(value)
                    else:
                        c[key] = value

        def _owner_to_json(owner):
            if not owner:
                return None
            return {
                'uid': owner.uid,
                'deptCodes': [m.university_dept.dept_code for m in owner.department_memberships],
            }
        return {
            'id': self.id,
            'domain': self.domain,
            'name': self.name,
            'code': self.id,
            'criteria': c,
            'owner': _owner_to_json(self.owner),
            'teamGroups': athletics.get_team_groups(c.get('groupCodes')) if c.get('groupCodes') else [],
            'alertCount': self.alert_count,
        }

    def to_api_json(
        self,
        order_by=None,
        offset=0,
        limit=50,
        term_id=None,
        alert_offset=None,
        alert_limit=None,
        include_sids=False,
        include_students=True,
        include_profiles=False,
        include_alerts_for_user_id=None,
    ):
        benchmark = get_benchmarker(f'CohortFilter {self.id} to_api_json')
        benchmark('begin')
        cohort_json = self.to_base_json()
        if not include_students and not include_alerts_for_user_id and self.student_count is not None:
            # No need for a students query; return the database-stashed student count.
            cohort_json.update({
                'totalStudentCount': self.student_count,
            })
            benchmark('end')
            return cohort_json

        sids_only = not include_students

        if self.domain == 'admitted_students':
            results = _query_admitted_students(
                benchmark=benchmark,
                criteria=cohort_json['criteria'],
                limit=limit,
                offset=offset,
                order_by=order_by,
                sids_only=sids_only,
            )
        else:
            results = _query_students(
                benchmark=benchmark,
                criteria=cohort_json['criteria'],
                include_profiles=include_profiles,
                limit=limit,
                offset=offset,
                order_by=order_by,
                owner=self.owner,
                term_id=term_id,
                sids_only=sids_only,
            )

        # If the cohort is new or cache refresh is underway then store student_count and sids in the db.
        if self.student_count is None:
            self.update_sids_and_student_count(
                sids=results['sids'] if results else [],
                student_count=results['totalStudentCount'] if results else 0,
            )
            if self.domain == 'default':
                self.track_membership_changes()

        if results:
            # Cohort might have tens of thousands of SIDs.
            if include_sids:
                cohort_json['sids'] = results['sids']
            cohort_json.update({
                'totalStudentCount': results['totalStudentCount'],
            })
            if include_students:
                cohort_json.update({
                    'students': results['students'],
                })
            if include_alerts_for_user_id and self.domain == 'default':
                alert_count_per_sid = Alert.include_alert_counts_for_students(
                    benchmark=benchmark,
                    viewer_user_id=include_alerts_for_user_id,
                    group=results,
                    offset=alert_offset,
                    limit=alert_limit,
                )
                cohort_json.update({
                    'alerts': alert_count_per_sid,
                })
                if self.alert_count is None:
                    alert_count = sum(student['alertCount'] for student in alert_count_per_sid)
                    self.update_alert_count(alert_count)
                    cohort_json.update({
                        'alertCount': alert_count,
                    })
        benchmark('end')
        return cohort_json


def _query_students(
        benchmark,
        criteria,
        include_profiles,
        limit,
        offset,
        order_by,
        owner,
        sids_only,
        term_id,
):
    # Translate the "My Students" filter, if present, into queryable criteria.
    plans = criteria.get('cohortOwnerAcademicPlans')
    if plans:
        if owner:
            owner_sid = get_csid_for_uid(app, owner.uid)
        else:
            owner_sid = current_user.get_csid()
        advisor_plan_mappings = [{'advisor_sid': owner_sid, 'academic_plan_code': plan} for plan in plans]
    else:
        advisor_plan_mappings = None
    coe_advisor_ldap_uids = util.get(criteria, 'coeAdvisorLdapUids')
    if not isinstance(coe_advisor_ldap_uids, list):
        coe_advisor_ldap_uids = [coe_advisor_ldap_uids] if coe_advisor_ldap_uids else None
    benchmark('begin students query')

    results = query_students(
        academic_career_status=criteria.get('academicCareerStatus'),
        academic_standings=criteria.get('academicStandings'),
        advisor_plan_mappings=advisor_plan_mappings,
        coe_advisor_ldap_uids=coe_advisor_ldap_uids,
        coe_ethnicities=criteria.get('coeEthnicities'),
        coe_genders=criteria.get('coeGenders'),
        coe_prep_statuses=criteria.get('coePrepStatuses'),
        coe_probation=criteria.get('coeProbation'),
        coe_underrepresented=criteria.get('coeUnderrepresented'),
        colleges=criteria.get('colleges'),
        curated_group_ids=criteria.get('curatedGroupIds'),
        degrees=criteria.get('degrees'),
        degree_terms=criteria.get('degreeTerms'),
        entering_terms=criteria.get('enteringTerms'),
        epn_cpn_grading_terms=criteria.get('epnCpnGradingTerms'),
        ethnicities=criteria.get('ethnicities'),
        expected_grad_terms=criteria.get('expectedGradTerms'),
        genders=criteria.get('genders'),
        gpa_ranges=criteria.get('gpaRanges'),
        group_codes=criteria.get('groupCodes'),
        in_intensive_cohort=criteria.get('inIntensiveCohort'),
        include_profiles=include_profiles,
        intended_majors=criteria.get('intendedMajors'),
        is_active_asc=None if criteria.get('isInactiveAsc') is None else not criteria.get('isInactiveAsc'),
        is_active_coe=None if criteria.get('isInactiveCoe') is None else not criteria.get('isInactiveCoe'),
        last_name_ranges=criteria.get('lastNameRanges'),
        last_term_gpa_ranges=criteria.get('lastTermGpaRanges'),
        levels=criteria.get('levels'),
        limit=limit,
        majors=criteria.get('majors'),
        midpoint_deficient_grade=criteria.get('midpointDeficient'),
        minors=criteria.get('minors'),
        offset=offset,
        order_by=order_by,
        sids_only=sids_only,
        term_id=term_id,
        transfer=criteria.get('transfer'),
        underrepresented=criteria.get('underrepresented'),
        unit_ranges=criteria.get('unitRanges'),
        visa_types=criteria.get('visaTypes'),
        student_holds=criteria.get('studentHolds'),
    )
    benchmark('end students query')
    return results


def _query_admitted_students(
        benchmark,
        criteria,
        limit,
        offset,
        order_by,
        sids_only,
):
    benchmark('begin admitted_students query')
    app.logger.info(f"""query_admitted_students:
        criteria={criteria}
        limit={limit}
        offset={offset}
        order_by={order_by}
        sids_only={sids_only}
    """)
    results = query_admitted_students(
        colleges=criteria.get('admitColleges'),
        family_dependent_ranges=criteria.get('familyDependentRanges'),
        freshman_or_transfer=criteria.get('freshmanOrTransfer'),
        has_fee_waiver=criteria.get('hasFeeWaiver'),
        in_foster_care=criteria.get('inFosterCare'),
        is_family_single_parent=criteria.get('isFamilySingleParent'),
        is_first_generation_college=criteria.get('isFirstGenerationCollege'),
        is_hispanic=criteria.get('isHispanic'),
        is_last_school_lcff=criteria.get('isLastSchoolLCFF'),
        is_reentry=criteria.get('isReentry'),
        is_student_single_parent=criteria.get('isStudentSingleParent'),
        is_urem=criteria.get('isUrem'),
        limit=limit,
        offset=offset,
        order_by=order_by,
        residency_categories=criteria.get('residencyCategories'),
        sids_only=sids_only,
        sir=criteria.get('sir'),
        special_program_cep=criteria.get('specialProgramCep'),
        student_dependent_ranges=criteria.get('studentDependentRanges'),
        x_ethnicities=criteria.get('xEthnicities'),
    )
    benchmark('end admitted_students query')
    return results
