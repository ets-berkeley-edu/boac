"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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
import re
from boac import db, std_commit
from boac.api.errors import InternalServerError
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user import cohort_filter_owners
from boac.models.base import Base
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB


class CohortFilter(Base, UserMixin):
    __tablename__ = 'cohort_filters'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    label = db.Column(db.String(255), nullable=False)
    filter_criteria = db.Column(JSONB, nullable=False)
    student_count = db.Column(db.Integer)
    owners = db.relationship('AuthorizedUser', secondary=cohort_filter_owners, back_populates='cohort_filters')

    def __init__(self, label, filter_criteria):
        self.label = label
        self.filter_criteria = filter_criteria

    def __repr__(self):
        return f"""<CohortFilter {self.id},
            label={self.label},
            owners={self.owners},
            filter_criteria={self.filter_criteria},
            updated_at={self.updated_at},
            created_at={self.created_at}>"""

    @classmethod
    def create(
            cls,
            uid,
            label,
            advisor_ldap_uids=None,
            gpa_ranges=None,
            group_codes=None,
            levels=None,
            majors=None,
            unit_ranges=None,
            in_intensive_cohort=None,
            is_inactive_asc=None,
    ):
        # If in_intensive_cohort is True then search intensive cohort; if equals False then search
        # non-intensive students; if equals None then search all students.
        criteria = cls.compose_filter_criteria(
            gpa_ranges=gpa_ranges,
            group_codes=group_codes,
            advisor_ldap_uids=advisor_ldap_uids,
            in_intensive_cohort=in_intensive_cohort,
            is_inactive_asc=is_inactive_asc,
            levels=levels,
            majors=majors,
            unit_ranges=unit_ranges,
        )
        cohort = CohortFilter(label=label, filter_criteria=json.dumps(criteria))
        user = AuthorizedUser.find_by_uid(uid)
        user.cohort_filters.append(cohort)
        # The new Cohort Filter's primary ID column is not generated until the DB session is flushed.
        db.session.flush()
        std_commit()
        return cohort

    @classmethod
    def rename(cls, cohort_id, label):
        cohort = CohortFilter.query.filter_by(id=cohort_id).first()
        cohort.label = label
        std_commit()
        return cohort

    def update_student_count(self, count):
        self.student_count = count
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
        return CohortFilter.query.filter(CohortFilter.owners.any(uid=uid)).order_by(CohortFilter.label).all()

    @classmethod
    def find_by_id(cls, cohort_id):
        return CohortFilter.query.filter_by(id=cohort_id).first()

    @classmethod
    def delete(cls, cohort_id):
        cohort_filter = CohortFilter.query.filter_by(id=cohort_id).first()
        db.session.delete(cohort_filter)
        std_commit()

    @classmethod
    def compose_filter_criteria(
            cls,
            advisor_ldap_uids=None,
            gpa_ranges=None,
            group_codes=None,
            in_intensive_cohort=None,
            is_inactive_asc=None,
            levels=None,
            majors=None,
            unit_ranges=None,
    ):
        has_criteria = next((c for c in [gpa_ranges, group_codes, levels, majors, unit_ranges] if c), None)
        has_criteria = has_criteria or next((c for c in [advisor_ldap_uids, in_intensive_cohort, is_inactive_asc] if c is not None), None)
        if not has_criteria:
            raise InternalServerError('CohortFilter creation requires one or more non-empty criteria.')
        # Validate
        for arg in [gpa_ranges, group_codes, levels, majors, unit_ranges]:
            if arg and not isinstance(arg, list):
                raise InternalServerError('Certain \'filter_criteria\' must be instance of \'list\' type.')
        group_code_syntax = re.compile('^[A-Z\-]+$')
        if group_codes and any(not group_code_syntax.match(code) for code in group_codes):
            raise InternalServerError('\'group_codes\' arg has invalid data: ' + str(group_codes))
        level_syntax = re.compile('^[A-Z][a-z]+$')
        if levels and any(not level_syntax.match(level) for level in levels):
            raise InternalServerError('\'levels\' arg has invalid data: ' + str(levels))
        if majors and any(not isinstance(m, str) for m in majors):
            raise InternalServerError('\'majors\' arg has invalid data: ' + str(majors))
        # The 'numrange' syntax is based on https://www.postgresql.org/docs/9.3/static/rangetypes.html
        numrange_syntax = re.compile('^numrange\([0-9\.NUL]+, [0-9\.NUL]+, \'..\'\)$')
        for r in (gpa_ranges or []) + (unit_ranges or []):
            if not numrange_syntax.match(r):
                msg = f'Range argument \'{r}\' does not match expected \'numrange\' syntax: {numrange_syntax.pattern}'
                raise InternalServerError(msg)
        return {
            'gpaRanges': gpa_ranges,
            'groupCodes': group_codes,
            'inIntensiveCohort': in_intensive_cohort,
            'advisorLdapUids': advisor_ldap_uids,
            'isInactiveAsc': is_inactive_asc,
            'levels': levels,
            'majors': majors,
            'unitRanges': unit_ranges,
        }
