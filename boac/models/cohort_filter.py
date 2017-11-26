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
        return summarize(cohort)

    @classmethod
    def update(cls, cohort_id, label):
        cohort = CohortFilter.query.filter_by(id=cohort_id).first()
        cohort.label = label
        db.session.commit()
        return summarize(cohort)

    @classmethod
    def share(cls, cohort_id, user_id):
        cohort = CohortFilter.query.filter_by(id=cohort_id).first()
        user = AuthorizedUser.find_by_uid(user_id)
        user.cohort_filters.append(cohort)
        db.session.commit()
        return summarize(cohort)

    @classmethod
    def all(cls):
        return [summarize(cohort) for cohort in CohortFilter.query.all()]

    @classmethod
    def all_owned_by(cls, uid):
        cohorts = CohortFilter.query.filter(CohortFilter.owners.any(uid=uid)).all()
        return [summarize(cohort) for cohort in cohorts]

    @classmethod
    def find_by_id(cls, cohort_id, order_by='member_name', offset=0, limit=50):
        result = CohortFilter.query.filter_by(id=cohort_id).first()
        cohort = result and summarize(result, order_by, offset, limit)
        return cohort

    @classmethod
    def delete(cls, cohort_id):
        cohort = CohortFilter.query.filter_by(id=cohort_id).first()
        db.session.delete(cohort)
        db.session.commit()


def summarize(cohort, order_by='member_name', offset=0, limit=50):
    filter_criteria = json.loads(cohort.filter_criteria)
    team_codes = filter_criteria['teams'] if 'teams' in filter_criteria else None
    summary = {
        'id': cohort.id,
        'label': cohort.label,
        'owners': [user.uid for user in cohort.owners],
    }

    if limit > 0 and len(team_codes) > 0:
        summary['teams'] = []
        for code in team_codes:
            team = TeamMember.for_code(code)
            summary['teams'].append({
                'code': code,
                'name': team['name'],
            })
        o = TeamMember.member_uid if order_by == 'member_uid' else TeamMember.member_name
        f = TeamMember.code.in_(team_codes)
        results = TeamMember.query.distinct(o).order_by(o).filter(f).offset(offset).limit(limit).all()

        summary['members'] = []
        for row in results:
            summary['members'].append(TeamMember.translate_row(row))

        summary['totalMemberCount'] = TeamMember.query.distinct(o).filter(f).count()
        db.session.commit()

    # Return a serializable object
    return summary
