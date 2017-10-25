"""Cohort definitions and memberships

This table is a temporary aid for early development. It will be dropped
when LDAP binds and caching are in place.
"""

from boac import db
from boac.models.base import Base
from sqlalchemy import func, UniqueConstraint


class Cohort(Base):
    __tablename__ = 'cohorts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    code = db.Column(db.String(255), nullable=False)
    member_uid = db.Column(db.String(80))
    member_csid = db.Column(db.String(80), nullable=False)
    member_name = db.Column(db.String(255))
    asc_sport_code_core = db.Column(db.String(80))
    asc_sport_code = db.Column(db.String(80))
    asc_sport = db.Column(db.String(80))
    asc_sport_core = db.Column(db.String(80))
    UniqueConstraint('code', 'member_csid', name='cohort_membership')

    def __repr__(self):
        return '<Cohort {} ({}), asc_sport {} ({}), asc_sport_core {} ({}), uid={}, csid={}, name={}, updated={}, created={}>'.format(
            self.cohort_definitions.get(self.code),
            self.code,
            self.asc_sport,
            self.asc_sport_code,
            self.asc_sport_core,
            self.asc_sport_code_core,
            self.member_uid,
            self.member_csid,
            self.member_name,
            self.updated_at,
            self.created_at,
        )

    cohort_definitions = {
        'BAM': 'Baseball - Men',
        'BBM': 'Basketball - Men',
        'BBW': 'Basketball - Women',
        'CCM': 'Cross Country - Men',
        'CCW': 'Cross Country - Women',
        'CRM': 'Crew - Men',
        'CRW': 'Crew - Women',
        'EMX': 'Equipment Managers',
        'FBM': 'Football - Men',
        'FHW': 'Field Hockey - Women',
        'GOM': 'Golf - Men',
        'GOW': 'Golf - Women',
        'GYM': 'Gymnastics - Men',
        'GYW': 'Gymnastics - Women',
        'LCW': 'Lacrosse - Women',
        'RGM': 'Rugby - Men',
        'SBW': 'Softball - Women',
        'SCM': 'Soccer - Men',
        'SCW': 'Soccer - Women',
        'SDM': 'Swimming & Diving - Men',
        'SDW': 'Swimming & Diving - Women',
        'STX': 'Student Trainers',
        'SVW': 'Sand Volleyball - Women',
        'TIM': 'Indoor Track & Field - Men',
        'TIW': 'Indoor Track & Field - Women',
        'TNM': 'Tennis - Men',
        'TNW': 'Tennis - Women',
        'TOM': 'Outdoor Track & Field - Men',
        'TOW': 'Outdoor Track & Field - Women',
        'VBW': 'Volleyball - Women',
        'WPM': 'Water Polo - Men',
        'WPW': 'Water Polo - Women',
    }

    @classmethod
    def list_all(cls):
        results = db.session.query(cls.code, func.count(cls.member_uid)).group_by(cls.code).all()

        def translate_row(row):
            return {
                'code': row[0],
                'name': cls.cohort_definitions.get(row[0], row[0]),
                'memberCount': row[1],
            }
        return [translate_row(row) for row in results]

    @classmethod
    def for_code(cls, code):
        members = cls.query.filter_by(code=code).all()
        return {
            'code': code,
            'name': cls.cohort_definitions.get(code, code),
            'members': [member.to_api_json() for member in members],
        }

    def to_api_json(self):
        return {
            'name': self.member_name,
            'uid': self.member_uid,
        }
