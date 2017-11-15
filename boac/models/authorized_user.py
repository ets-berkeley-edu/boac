"""
This package integrates with Flask-Login to determine who can use the app,
and which privileges they have. It will probably end up as a DB table, but is
simply mocked-out a la "demo mode" for now.
"""

from boac import db
from boac.models.base import Base
from flask_login import UserMixin

cohort_filter_owners = db.Table(
    'cohort_filter_owners',
    Base.metadata,
    db.Column('cohort_filter_id', db.Integer, db.ForeignKey('cohort_filters.id'), primary_key=True),
    db.Column('user_id', db.String(255), db.ForeignKey('authorized_users.uid'), primary_key=True),
)


class AuthorizedUser(Base, UserMixin):
    __tablename__ = 'authorized_users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    uid = db.Column(db.String(255), nullable=False, unique=True)
    is_advisor = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    is_director = db.Column(db.Boolean)
    cohort_filters = db.relationship('CohortFilter', secondary=cohort_filter_owners, back_populates='owners')

    def __init__(self, uid, is_advisor=True, is_admin=False, is_director=False):
        self.uid = uid
        self.is_advisor = is_advisor
        self.is_admin = is_admin
        self.is_director = is_director

    def __repr__(self):
        return '<AuthorizedUser {}, is_advisor={}, is_admin={}, is_director={}, updated={}, created={}>'.format(
            self.uid,
            self.is_advisor,
            self.is_admin,
            self.is_director,
            self.updated_at,
            self.created_at,
        )

    def get_id(self):
        """Override UserMixin, since our DB conventionally reserves 'id' for generated keys."""
        return self.uid


class CohortFilter(Base):
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
    def create(cls, label, team_codes):
        codes = ','.join(map('"{0}"'.format, team_codes))
        return CohortFilter(label=label, filter_criteria='{"teams": [' + codes + ']}')


def load_user(user_id):
    return AuthorizedUser.query.filter_by(uid=user_id).first()


def load_cohorts_owned_by(user_id):
    return CohortFilter.query.filter(CohortFilter.owners.any(uid=user_id)).all()


def load_cohort_by_id(cohort_id):
    return CohortFilter.query.filter_by(id=cohort_id).first()


def create_cohort_filter(cohort_filter, user_id):
    user = load_user(user_id)
    user.cohort_filters.append(cohort_filter)
    db.session.commit()


def update_cohort(cohort_id, label):
    cohort = load_cohort_by_id(cohort_id=cohort_id)
    cohort.label = label
    db.session.add(cohort)
    db.session.commit()


def share_cohort_filter(cohort_filter_id, user_id):
    cohort_filter = CohortFilter.query.filter_by(id=cohort_filter_id).first()
    user = load_user(user_id)
    user.cohort_filters.append(cohort_filter)
    db.session.commit()


def delete_cohort(cohort_id):
    cohort_filter = CohortFilter.query.filter_by(id=cohort_id).first()
    db.session.delete(cohort_filter)
    db.session.commit()
