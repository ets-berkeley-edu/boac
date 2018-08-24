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


from boac import db, std_commit
from boac.api.errors import InternalServerError
from boac.lib.util import camelize
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
    def create(cls, uid, label, **kwargs):
        at_least_one_is_defined = False
        filter_criteria = {}
        for k, v in kwargs.items():
            at_least_one_is_defined = at_least_one_is_defined or (len(v) if isinstance(v, list) else v is not None)
            filter_criteria[camelize(k)] = v
        if not at_least_one_is_defined:
            raise InternalServerError('Cohort creation requires at least one filter specification.')
        cohort = CohortFilter(label=label, filter_criteria=filter_criteria)
        user = AuthorizedUser.find_by_uid(uid)
        user.cohort_filters.append(cohort)
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
