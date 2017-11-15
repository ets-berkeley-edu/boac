"""
This package integrates with Flask-Login to determine who can use the app,
and which privileges they have. It will probably end up as a DB table, but is
simply mocked-out a la "demo mode" for now.
"""

from boac import db
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user import cohort_filter_owners
from boac.models.base import Base
from flask_login import UserMixin


class CohortFilter(Base, UserMixin):
    __tablename__ = 'cohort_filters'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    filter_criteria = db.Column(db.Text, nullable=False)
    owners = db.relationship('AuthorizedUser', secondary=cohort_filter_owners, back_populates='cohort_filters')

    def __init__(self, label, filter_criteria):
        self.label = label
        self.filter_criteria = filter_criteria

    def __repr__(self):
        return '<CohortFilter {}, label={}, owners={}, filter_criteria={}>'.format(
            self.id,
            self.label,
            self.owners,
            self.filter_criteria,
        )

    @classmethod
    def create(cls, label, team_codes, uid):
        codes = ','.join(map('"{0}"'.format, team_codes))
        cohort = CohortFilter(label=label, filter_criteria='{"teams": [' + codes + ']}')
        user = AuthorizedUser.find_by_uid(uid)
        user.cohort_filters.append(cohort)
        db.session.commit()

    @classmethod
    def update(cls, cohort_id, label):
        cohort = CohortFilter.find_by_id(cohort_id=cohort_id)
        cohort.label = label
        db.session.add(cohort)
        db.session.commit()

    @classmethod
    def share(cls, cohort_filter_id, user_id):
        cohort_filter = CohortFilter.query.filter_by(id=cohort_filter_id).first()
        user = AuthorizedUser.find_by_uid(user_id)
        user.cohort_filters.append(cohort_filter)
        db.session.commit()

    @classmethod
    def all(cls):
        return CohortFilter.query.all()

    @classmethod
    def all_owned_by(cls, uid):
        return CohortFilter.query.filter(CohortFilter.owners.any(uid=uid)).all()

    @classmethod
    def find_by_id(cls, cohort_id):
        return CohortFilter.query.filter_by(id=cohort_id).first()

    @classmethod
    def delete(cls, cohort_id):
        cohort = CohortFilter.query.filter_by(id=cohort_id).first()
        db.session.delete(cohort)
        db.session.commit()
