"""Cohort definitions and memberships

This table is a temporary aid for early development. It will be dropped
when LDAP binds and caching are in place.
"""

from boac import db
from boac.models.base import Base
from sqlalchemy import UniqueConstraint


class Cohort(Base):
    __tablename__ = 'cohorts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    code = db.Column(db.String(255), nullable=False)
    member_uid = db.Column(db.String(80), nullable=False)
    member_csid = db.Column(db.String(80))
    member_name = db.Column(db.String(255))
    UniqueConstraint('code', 'member_uid', name='cohort_membership')

    def __init__(self, code, member_uid, member_csid=None, member_name=None):
        self.code = code
        self.member_uid = member_uid
        self.member_csid = member_csid
        self.member_name = member_name

    def __repr__(self):
        return '<Cohort {} ({}), uid={}, csid={}, name={}, updated={}, created={}>'.format(
            self.cohort_definitions.get(self.code),
            self.code,
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
