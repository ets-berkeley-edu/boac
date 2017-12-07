"""
This package integrates with Flask-Login to determine who can use the app,
and which privileges they have. It will probably end up as a DB table, but is
simply mocked-out a la "demo mode" for now.
"""

import json
from boac import db
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user import cohort_filter_owners
from boac.models.base import Base
from boac.models.team_member import TeamMember
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB


class CohortFilter(Base, UserMixin):
    __tablename__ = 'cohort_filters'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    filter_criteria = db.Column(JSONB, nullable=False)
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
    def create(cls, label, team_group_codes, uid):
        team_group_codes = ','.join(map('"{0}"'.format, team_group_codes))
        cf = CohortFilter(label=label, filter_criteria='{"team_group_codes": [' + team_group_codes + ']}')
        user = AuthorizedUser.find_by_uid(uid)
        user.cohort_filters.append(cf)
        db.session.commit()
        return construct_cohort(cf)

    @classmethod
    def update(cls, cohort_id, label):
        cf = CohortFilter.query.filter_by(id=cohort_id).first()
        cf.label = label
        db.session.commit()
        return construct_cohort(cf)

    @classmethod
    def share(cls, cohort_id, user_id):
        cf = CohortFilter.query.filter_by(id=cohort_id).first()
        user = AuthorizedUser.find_by_uid(user_id)
        user.cohort_filters.append(cf)
        db.session.commit()
        return construct_cohort(cf)

    @classmethod
    def all(cls):
        return [construct_cohort(cf) for cf in CohortFilter.query.all()]

    @classmethod
    def get_intensive_cohort(cls, order_by='member_name', offset=0, limit=50):
        cohort = {
            'id': 'intensive',
            'label': 'Intensive',
            'owners': None,
        }
        cohort.update(TeamMember.get_intensive_cohort(order_by=order_by, offset=offset, limit=limit))
        return cohort

    @classmethod
    def all_owned_by(cls, uid):
        filters = CohortFilter.query.filter(CohortFilter.owners.any(uid=uid)).all()
        return [construct_cohort(cohort_filter) for cohort_filter in filters]

    @classmethod
    def find_by_id(cls, cohort_id, order_by='member_name', offset=0, limit=50):
        cf = CohortFilter.query.filter_by(id=cohort_id).first()
        return cf and construct_cohort(cf, True, order_by, offset, limit)

    @classmethod
    def delete(cls, cohort_id):
        cohort_filter = CohortFilter.query.filter_by(id=cohort_id).first()
        db.session.delete(cohort_filter)
        db.session.commit()


def construct_cohort(cf, include_member_details=False, order_by='member_name', offset=0, limit=50):
    criteria = cf.filter_criteria if isinstance(cf.filter_criteria, dict) else json.loads(cf.filter_criteria)
    team_group_codes = criteria['team_group_codes'] if 'team_group_codes' in criteria else None
    cohort = {
        'id': cf.id,
        'label': cf.label,
        'owners': [user.uid for user in cf.owners],
    }
    if limit > 0:
        cohort.update(TeamMember.get_athletes(team_group_codes, include_member_details, order_by, offset, limit))
    return cohort
