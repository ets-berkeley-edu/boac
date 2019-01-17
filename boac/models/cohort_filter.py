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

import json

from boac import db, std_commit
from boac.api.errors import InternalServerError
from boac.lib import util
from boac.lib.berkeley import convert_inactive_arg
from boac.merged import athletics
from boac.merged.student import query_students
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user import cohort_filter_owners
from boac.models.base import Base
from flask_login import current_user, UserMixin
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB


class CohortFilter(Base, UserMixin):
    __tablename__ = 'cohort_filters'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    name = db.Column(db.String(255), nullable=False)
    filter_criteria = db.Column(JSONB, nullable=False)
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
            student_count={self.student_count},
            alert_count={self.alert_count},
            updated_at={self.updated_at},
            created_at={self.created_at}>"""

    @classmethod
    def create(cls, uid, name, filter_criteria, student_count=None):
        if all(not isinstance(value, bool) and not value for value in filter_criteria.values()):
            raise InternalServerError('Cohort creation requires at least one filter specification.')
        cohort = CohortFilter(name=name, filter_criteria=filter_criteria)
        cohort.student_count = student_count
        user = AuthorizedUser.find_by_uid(uid)
        user.cohort_filters.append(cohort)
        db.session.flush()
        std_commit()
        return cohort

    @classmethod
    def update(cls, cohort_id, name=None, filter_criteria=None, student_count=None, alert_count=None):
        cohort = CohortFilter.query.filter_by(id=cohort_id).first()
        cohort.name = name
        cohort.filter_criteria = filter_criteria
        if student_count is not None:
            cohort.student_count = student_count
        if alert_count is not None:
            cohort.alert_count = alert_count
        std_commit()
        return cohort

    def update_student_count(self, count):
        self.student_count = count
        std_commit()
        return self

    def update_alert_count(self, count):
        self.alert_count = count
        std_commit()
        return self

    @classmethod
    def share(cls, cohort_id, user_id):
        cohort = CohortFilter.query.filter_by(id=cohort_id).first()
        user = AuthorizedUser.find_by_uid(user_id)
        user.cohort_filters.append(cohort)
        std_commit()
        return cohort

    @classmethod
    def all_cohorts(cls):
        return CohortFilter.query.all()

    @classmethod
    def all_owned_by(cls, uid):
        return CohortFilter.query.filter(CohortFilter.owners.any(uid=uid)).order_by(CohortFilter.name).all()

    @classmethod
    def find_by_id(cls, cohort_id):
        return CohortFilter.query.filter_by(id=cohort_id).first()

    @classmethod
    def delete(cls, cohort_id):
        cohort_filter = CohortFilter.query.filter_by(id=cohort_id).first()
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
                'filterCriteria': row['filter_criteria'],
                'alertCount': row['alert_count'],
                'totalStudentCount': row['student_count'],
            }
        return [transform(row) for row in results]

    def to_api_json(
        self,
        order_by=None,
        offset=0,
        limit=50,
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
            'owners': [user.uid for user in self.owners],
        }
        coe_prep_statuses = c.get('coePrepStatuses')
        coe_probation = util.to_bool_or_none(c.get('coeProbation'))
        ethnicities = c.get('ethnicities')
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
        underrepresented = util.to_bool_or_none(c.get('underrepresented'))
        unit_ranges = c.get('unitRanges')
        cohort_json.update({
            'filterCriteria': {
                'advisorLdapUids': advisor_ldap_uids,
                'coePrepStatuses': coe_prep_statuses,
                'coeProbation': coe_probation,
                'ethnicities': ethnicities,
                'genders': genders,
                'gpaRanges': gpa_ranges,
                'groupCodes': group_codes,
                'inIntensiveCohort': in_intensive_cohort,
                'isInactiveAsc': is_inactive_asc,
                'isInactiveCoe': is_inactive_coe,
                'lastNameRange': last_name_range,
                'levels': levels,
                'majors': majors,
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

        # Unsaved cohorts will have no owner defined and should translate department-specific criteria against the current
        # logged-in user.
        owner = self.owners[0] if len(self.owners) else current_user
        is_active_asc = convert_inactive_arg(is_inactive_asc, 'UWASC', owner)
        is_active_coe = convert_inactive_arg(is_inactive_coe, 'COENG', owner)

        sids_only = not include_students
        results = query_students(
            advisor_ldap_uids=advisor_ldap_uids,
            coe_prep_statuses=coe_prep_statuses,
            coe_probation=coe_probation,
            ethnicities=ethnicities,
            genders=genders,
            gpa_ranges=gpa_ranges,
            group_codes=group_codes,
            in_intensive_cohort=in_intensive_cohort,
            include_profiles=(include_students and include_profiles),
            is_active_asc=is_active_asc,
            is_active_coe=is_active_coe,
            last_name_range=last_name_range,
            levels=levels,
            limit=limit,
            majors=majors,
            offset=offset,
            order_by=order_by,
            sids_only=sids_only,
            underrepresented=underrepresented,
            unit_ranges=unit_ranges,
        )
        if results:
            # If the cohort is newly created or a cache refresh is underway, store the student count in the database
            # to save future queries.
            if self.student_count is None:
                self.update_student_count(results['totalStudentCount'])
            cohort_json.update({
                'totalStudentCount': results['totalStudentCount'],
            })
            if include_students:
                cohort_json.update({
                    'students': results['students'],
                })
            if include_alerts_for_user_id:
                alert_count_per_sid = Alert.include_alert_counts_for_students(viewer_user_id=include_alerts_for_user_id, cohort=results)
                cohort_json.update({
                    'alerts': alert_count_per_sid,
                })
                if self.alert_count is None:
                    self.update_alert_count(sum(student['alertCount'] for student in alert_count_per_sid))
        return cohort_json
