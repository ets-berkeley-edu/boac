"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.merged.calnet import get_csid_for_uid
from boac.merged.sis_terms import current_term_id
from boac.merged.student import query_students
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user import cohort_filter_owners
from boac.models.base import Base
from flask import current_app as app
from flask_login import current_user
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import deferred, undefer


class CohortFilter(Base):
    __tablename__ = 'cohort_filters'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    name = db.Column(db.String(255), nullable=False)
    filter_criteria = db.Column(JSONB, nullable=False)
    # Fetching a large array literal from Postgres can be expensive. We defer until invoking code demands it.
    sids = deferred(db.Column(ARRAY(db.String(80))))
    student_count = db.Column(db.Integer)
    alert_count = db.Column(db.Integer)
    owners = db.relationship('AuthorizedUser', secondary=cohort_filter_owners, back_populates='cohort_filters')

    def __init__(self, name, filter_criteria):
        self.name = name
        self.filter_criteria = filter_criteria

    def __repr__(self):
        return f"""<CohortFilter {self.id},
            name={self.name},
            owners={self.owners},
            filter_criteria={self.filter_criteria},
            sids={self.sids},
            student_count={self.student_count},
            alert_count={self.alert_count},
            updated_at={self.updated_at},
            created_at={self.created_at}>"""

    @classmethod
    def create(cls, uid, name, filter_criteria, **kwargs):
        if all(not isinstance(value, bool) and not value for value in filter_criteria.values()):
            raise InternalServerError('Cohort creation requires at least one filter specification.')
        cohort = cls(name=name, filter_criteria=filter_criteria)
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
        cohort.sids = None
        cohort.student_count = None
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

    def update_sids_and_student_count(self, sids, student_count):
        self.sids = sids
        self.student_count = student_count
        std_commit()
        return self

    def update_alert_count(self, count):
        self.alert_count = count
        std_commit()
        return self

    @classmethod
    def share(cls, cohort_id, user_id):
        cohort = cls.query.filter_by(id=cohort_id).first()
        user = AuthorizedUser.find_by_uid(user_id)
        user.cohort_filters.append(cohort)
        std_commit()

    @classmethod
    def get_cohorts_of_user_id(cls, user_id):
        query = text(f"""
            SELECT id, name, filter_criteria, alert_count, student_count FROM cohort_filters c
            LEFT JOIN cohort_filter_owners o ON o.cohort_filter_id = c.id
            WHERE o.user_id = :user_id
            ORDER BY c.name
        """)
        results = db.session.execute(query, {'user_id': user_id})

        def transform(row):
            return {
                'id': row['id'],
                'name': row['name'],
                'criteria': row['filter_criteria'],
                'alertCount': row['alert_count'],
                'totalStudentCount': row['student_count'],
            }
        return [transform(row) for row in results]

    @classmethod
    def get_cohorts_owned_by_uids(cls, uids):
        query = text(f"""
            SELECT c.id, c.name, c.filter_criteria, c.alert_count, c.student_count, ARRAY_AGG(uid) authorized_users
            FROM cohort_filters c
            INNER JOIN cohort_filter_owners o ON c.id = o.cohort_filter_id
            INNER JOIN authorized_users u ON o.user_id = u.id
            WHERE u.uid = ANY(:uids)
            GROUP BY c.id, c.name, c.filter_criteria, c.alert_count, c.student_count
        """)
        results = db.session.execute(query, {'uids': uids})

        def transform(row):
            return {
                'id': row['id'],
                'name': row['name'],
                'criteria': row['filter_criteria'],
                'owners': row['authorized_users'],
                'alertCount': row['alert_count'],
                'totalStudentCount': row['student_count'],
            }
        return [transform(row) for row in results]

    @classmethod
    def is_cohort_owned_by(cls, cohort_id, user_id):
        query = text(f"""
            SELECT count(*) FROM cohort_filters c
            LEFT JOIN cohort_filter_owners o ON o.cohort_filter_id = c.id
            WHERE o.user_id = :user_id AND c.id = :cohort_id
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
        query = text(f"""
            UPDATE cohort_filters
            SET alert_count = updated_cohort_counts.alert_count
            FROM
            (
                SELECT cohort_filters.id AS cohort_filter_id, count(*) AS alert_count
                FROM alerts
                JOIN cohort_filters
                    ON alerts.sid = ANY(cohort_filters.sids)
                    AND alerts.key LIKE :key
                    AND alerts.active IS TRUE
                JOIN cohort_filter_owners
                    ON cohort_filters.id = cohort_filter_owners.cohort_filter_id
                    AND cohort_filter_owners.user_id = :owner_id
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

    def to_api_json(
        self,
        order_by=None,
        offset=0,
        limit=50,
        alert_offset=None,
        alert_limit=None,
        include_sids=False,
        include_students=True,
        include_profiles=False,
        include_alerts_for_user_id=None,
    ):
        benchmark = get_benchmarker(f'CohortFilter {self.id} to_api_json')
        benchmark('begin')
        c = self.filter_criteria
        c = c if isinstance(c, dict) else json.loads(c)
        coe_advisor_ldap_uids = util.get(c, 'coeAdvisorLdapUids')
        if not isinstance(coe_advisor_ldap_uids, list):
            coe_advisor_ldap_uids = [coe_advisor_ldap_uids] if coe_advisor_ldap_uids else None
        cohort_name = self.name
        cohort_json = {
            'id': self.id,
            'code': self.id,
            'name': cohort_name,
            'owners': [],
            'alertCount': self.alert_count,
        }
        for owner in self.owners:
            cohort_json['owners'].append({
                'uid': owner.uid,
                'deptCodes': [m.university_dept.dept_code for m in owner.department_memberships],
            })
        coe_ethnicities = c.get('coeEthnicities')
        coe_genders = c.get('coeGenders')
        coe_prep_statuses = c.get('coePrepStatuses')
        coe_probation = util.to_bool_or_none(c.get('coeProbation'))
        coe_underrepresented = util.to_bool_or_none(c.get('coeUnderrepresented'))
        cohort_owner_academic_plans = util.get(c, 'cohortOwnerAcademicPlans')
        curated_group_ids = util.get(c, 'curatedGroupIds')
        entering_terms = c.get('enteringTerms')
        ethnicities = c.get('ethnicities')
        expected_grad_terms = c.get('expectedGradTerms')
        genders = c.get('genders')
        gpa_ranges = c.get('gpaRanges')
        group_codes = c.get('groupCodes')
        in_intensive_cohort = util.to_bool_or_none(c.get('inIntensiveCohort'))
        is_inactive_asc = util.to_bool_or_none(c.get('isInactiveAsc'))
        is_inactive_coe = util.to_bool_or_none(c.get('isInactiveCoe'))
        last_name_ranges = c.get('lastNameRanges')
        last_term_gpa_ranges = c.get('lastTermGpaRanges')
        levels = c.get('levels')
        majors = c.get('majors')
        midpoint_deficient_grade = util.to_bool_or_none(c.get('midpointDeficient'))
        team_groups = athletics.get_team_groups(group_codes) if group_codes else []
        transfer = util.to_bool_or_none(c.get('transfer'))
        underrepresented = util.to_bool_or_none(c.get('underrepresented'))
        unit_ranges = c.get('unitRanges')
        visa_types = c.get('visaTypes')
        cohort_json.update({
            'criteria': {
                'coeAdvisorLdapUids': coe_advisor_ldap_uids,
                'coeEthnicities': coe_ethnicities,
                'coeGenders': coe_genders,
                'coePrepStatuses': coe_prep_statuses,
                'coeProbation': coe_probation,
                'coeUnderrepresented': coe_underrepresented,
                'cohortOwnerAcademicPlans': cohort_owner_academic_plans,
                'curatedGroupIds': curated_group_ids,
                'enteringTerms': entering_terms,
                'ethnicities': ethnicities,
                'expectedGradTerms': expected_grad_terms,
                'genders': genders,
                'gpaRanges': gpa_ranges,
                'groupCodes': group_codes,
                'inIntensiveCohort': in_intensive_cohort,
                'isInactiveAsc': is_inactive_asc,
                'isInactiveCoe': is_inactive_coe,
                'lastNameRanges': last_name_ranges,
                'lastTermGpaRanges': last_term_gpa_ranges,
                'levels': levels,
                'majors': majors,
                'midpointDeficient': midpoint_deficient_grade,
                'transfer': transfer,
                'unitRanges': unit_ranges,
                'underrepresented': underrepresented,
                'visaTypes': visa_types,
            },
            'teamGroups': team_groups,
        })
        if not include_students and not include_alerts_for_user_id and self.student_count is not None:
            # No need for a students query; return the database-stashed student count.
            cohort_json.update({
                'totalStudentCount': self.student_count,
            })
            benchmark('end')
            return cohort_json

        benchmark('begin students query')
        sids_only = not include_students

        # Translate the "My Students" filter, if present, into queryable criteria. Although our database relationships allow
        # for multiple cohort owners, we assume a single owner here since the "My Students" filter makes no sense
        # in any other scenario.
        if cohort_owner_academic_plans:
            if self.owners:
                owner_sid = get_csid_for_uid(app, self.owners[0].uid)
            else:
                owner_sid = current_user.get_csid()
            advisor_plan_mappings = [{'advisor_sid': owner_sid, 'academic_plan_code': plan} for plan in cohort_owner_academic_plans]
        else:
            advisor_plan_mappings = None

        results = query_students(
            advisor_plan_mappings=advisor_plan_mappings,
            coe_advisor_ldap_uids=coe_advisor_ldap_uids,
            coe_ethnicities=coe_ethnicities,
            coe_genders=coe_genders,
            coe_prep_statuses=coe_prep_statuses,
            coe_probation=coe_probation,
            coe_underrepresented=coe_underrepresented,
            curated_group_ids=curated_group_ids,
            entering_terms=entering_terms,
            ethnicities=ethnicities,
            expected_grad_terms=expected_grad_terms,
            genders=genders,
            gpa_ranges=gpa_ranges,
            group_codes=group_codes,
            in_intensive_cohort=in_intensive_cohort,
            include_profiles=(include_students and include_profiles),
            is_active_asc=None if is_inactive_asc is None else not is_inactive_asc,
            is_active_coe=None if is_inactive_coe is None else not is_inactive_coe,
            last_name_ranges=last_name_ranges,
            last_term_gpa_ranges=last_term_gpa_ranges,
            levels=levels,
            limit=limit,
            majors=majors,
            midpoint_deficient_grade=midpoint_deficient_grade,
            offset=offset,
            order_by=order_by,
            sids_only=sids_only,
            transfer=transfer,
            underrepresented=underrepresented,
            unit_ranges=unit_ranges,
            visa_types=visa_types,
        )
        benchmark('end students query')

        if results:
            # Cohort might have tens of thousands of SIDs.
            if include_sids:
                cohort_json['sids'] = results['sids']
            cohort_json.update({
                'totalStudentCount': results['totalStudentCount'],
            })
            # If the cohort is new or cache refresh is underway then store student_count and sids in the db.
            if self.student_count is None:
                self.update_sids_and_student_count(results['sids'], results['totalStudentCount'])
            if include_students:
                cohort_json.update({
                    'students': results['students'],
                })
            if include_alerts_for_user_id:
                benchmark('begin alerts query')
                alert_count_per_sid = Alert.include_alert_counts_for_students(
                    viewer_user_id=include_alerts_for_user_id,
                    group=results,
                    offset=alert_offset,
                    limit=alert_limit,
                )
                benchmark('end alerts query')
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
