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
    db.Column('user_id', db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True),
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

    @classmethod
    def find_by_uid(cls, uid):
        return AuthorizedUser.query.filter_by(uid=uid).first()
