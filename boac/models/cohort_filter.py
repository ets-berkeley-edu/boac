"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

from datetime import datetime
import json

from boac import db, std_commit
from boac.api.errors import InternalServerError
from boac.lib import util
from boac.lib.util import to_bool_or_none as to_bool
from boac.merged import athletics
from boac.merged.student import query_students
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user import cohort_filter_owners
from boac.models.base import Base
from flask_login import UserMixin
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import deferred, undefer


class CohortFilter(Base, UserMixin):
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
        cohort.name = name
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
    def all_cohorts(cls):
        return [c.to_api_json(include_students=False) for c in cls.query.all()]

    @classmethod
    def all_owned_by(cls, uid):
        cohorts = []
        for cohort in cls.query.filter(cls.owners.any(uid=uid)).order_by(cls.name).all():
            cohorts.append(cohort.to_api_json())
        return cohorts

    @classmethod
    def find_by_id(cls, cohort_id, **kwargs):
        cohort = cls.query.filter_by(id=cohort_id).first()
        return cohort and cohort.to_api_json(**kwargs)

    @classmethod
    def delete(cls, cohort_id):
        cohort_filter = cls.query.filter_by(id=cohort_id).first()
        db.session.delete(cohort_filter)
        std_commit()

    @classmethod
    def summarize_alert_counts_in_all_owned_by(cls, uid):
        user_id = AuthorizedUser.find_by_uid(str(uid)).id
        query = text(f"""SELECT * FROM cohort_filters c
            LEFT JOIN cohort_filter_owners o ON o.cohort_filter_id = c.id
            WHERE o.user_id = :user_id
            ORDER BY c.name""")
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
    def construct_phantom_cohort(cls, filters, **kwargs):
        # A "phantom" cohort is one that we do not save to the db.
        # On the front-end, a "phantom" cohort is an unsaved search.
        cohort = cls(
            name=f'phantom_cohort_{datetime.now().timestamp()}',
            filter_criteria=cls.translate_filters_to_cohort_criteria(filters),
        )
        return cohort.to_api_json(**kwargs)

    @classmethod
    def translate_filters_to_cohort_criteria(cls, filters):
        criteria = {}
        for filter_ in filters:
            key = filter_['key']
            type_ = filter_['type']
            value = filter_['value']
            if type_ == 'boolean':
                criteria[key] = to_bool(value)
            elif type_ == 'array':
                criteria[key] = criteria.get(key) or []
                criteria[key].append(value)
            elif type_ == 'range':
                criteria[key] = value
        return criteria

    def to_api_json(
        self,
        order_by=None,
        offset=0,
        limit=50,
        alert_offset=None,
        alert_limit=None,
        include_students=True,
        include_profiles=False,
        include_alerts_for_user_id=None,
    ):
        c = self.filter_criteria
        c = c if isinstance(c, dict) else json.loads(c)
        advisor_ldap_uids = util.get(c, 'advisorLdapUids')
        if not isinstance(advisor_ldap_uids, list):
            advisor_ldap_uids = [advisor_ldap_uids] if advisor_ldap_uids else None
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
        coe_prep_statuses = c.get('coePrepStatuses')
        coe_probation = util.to_bool_or_none(c.get('coeProbation'))
        ethnicities = c.get('ethnicities')
        expected_grad_terms = c.get('expectedGradTerms')
        genders = c.get('genders')
        gpa_ranges = c.get('gpaRanges')
        group_codes = c.get('groupCodes')
        in_intensive_cohort = util.to_bool_or_none(c.get('inIntensiveCohort'))
        is_inactive_asc = util.to_bool_or_none(c.get('isInactiveAsc'))
        is_inactive_coe = util.to_bool_or_none(c.get('isInactiveCoe'))
        last_name_range = c.get('lastNameRange')
        levels = c.get('levels')
        majors = c.get('majors')
        team_groups = athletics.get_team_groups(group_codes) if group_codes else []
        transfer = util.to_bool_or_none(c.get('transfer'))
        underrepresented = util.to_bool_or_none(c.get('underrepresented'))
        unit_ranges = c.get('unitRanges')
        cohort_json.update({
            'criteria': {
                'advisorLdapUids': advisor_ldap_uids,
                'coePrepStatuses': coe_prep_statuses,
                'coeProbation': coe_probation,
                'ethnicities': ethnicities,
                'expectedGradTerms': expected_grad_terms,
                'genders': genders,
                'gpaRanges': gpa_ranges,
                'groupCodes': group_codes,
                'inIntensiveCohort': in_intensive_cohort,
                'isInactiveAsc': is_inactive_asc,
                'isInactiveCoe': is_inactive_coe,
                'lastNameRange': last_name_range,
                'levels': levels,
                'majors': majors,
                'transfer': transfer,
                'unitRanges': unit_ranges,
                'underrepresented': underrepresented,
            },
            'teamGroups': team_groups,
        })
        if not include_students and not include_alerts_for_user_id and self.student_count is not None:
            # No need for a students query; return the database-stashed student count.
            cohort_json.update({
                'totalStudentCount': self.student_count,
            })
            return cohort_json

        # Until we remove per-department siloing, cohort membership queries are constrained by the cohort owner, which
        # is a single user per present UX.
        cohort_owner = self.owners[0] if len(self.owners) else None

        sids_only = not include_students
        results = query_students(
            advisor_ldap_uids=advisor_ldap_uids,
            coe_prep_statuses=coe_prep_statuses,
            coe_probation=coe_probation,
            cohort_owner=cohort_owner,
            ethnicities=ethnicities,
            expected_grad_terms=expected_grad_terms,
            genders=genders,
            gpa_ranges=gpa_ranges,
            group_codes=group_codes,
            in_intensive_cohort=in_intensive_cohort,
            include_profiles=(include_students and include_profiles),
            is_active_asc=None if is_inactive_asc is None else not is_inactive_asc,
            is_active_coe=None if is_inactive_coe is None else not is_inactive_coe,
            last_name_range=last_name_range,
            levels=levels,
            limit=limit,
            majors=majors,
            offset=offset,
            order_by=order_by,
            sids_only=sids_only,
            transfer=transfer,
            underrepresented=underrepresented,
            unit_ranges=unit_ranges,
        )
        if results:
            # We deliberately keep SIDs out of the feed. For now, it is only used server-side in bulk note creation.
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
                alert_count_per_sid = Alert.include_alert_counts_for_students(
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
        return cohort_json
