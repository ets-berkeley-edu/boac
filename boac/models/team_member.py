"""Team membership"""

from boac import db
from boac.models.base import Base
from sqlalchemy import UniqueConstraint


class TeamMember(Base):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    code = db.Column(db.String(255), nullable=False)
    member_uid = db.Column(db.String(80))
    member_csid = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    asc_sport_code_core = db.Column(db.String(80))
    asc_sport_code = db.Column(db.String(80))
    asc_sport = db.Column(db.String(80))
    asc_sport_core = db.Column(db.String(80))
    in_intensive_cohort = db.Column(db.Boolean, nullable=False, default=False)
    UniqueConstraint('code', 'member_csid', name='team_member')

    def __repr__(self):
        return """
        <TeamMember {} ({}), asc_sport {} ({}), asc_sport_core {} ({}), uid={}, csid={}, first_name={}, last_name={},
            in_intensive_cohort={}, updated={}, created={}>
        """.format(
            self.team_definitions.get(self.code),
            self.code,
            self.asc_sport,
            self.asc_sport_code,
            self.asc_sport_core,
            self.asc_sport_code_core,
            self.member_uid,
            self.member_csid,
            self.first_name,
            self.last_name,
            self.in_intensive_cohort,
            self.updated_at,
            self.created_at,
        )

    team_definitions = {
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
    def get_all_athletes(cls, order_by=None):
        athletes = cls.query.order_by(cls.first_name).all()
        athletes = [athlete.to_api_json() for athlete in athletes]
        if order_by and len(athletes) > 0:
            is_valid_key = order_by in athletes[0]
            athletes = sorted(athletes, key=lambda athlete: athlete[order_by]) if is_valid_key else athletes
        return athletes

    def to_api_json(self):
        feed = {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'name': self.first_name + ' ' + self.last_name,
            'sid': self.member_csid,
            'inIntensiveCohort': self.in_intensive_cohort,
            'sportCode': self.asc_sport_code_core,
            'sportName': self.asc_sport_core,
            'teamCode': self.code,
            'teamGroupCode': self.asc_sport_code,
            'teamGroupName': self.asc_sport,
            'uid': self.member_uid,
        }
        return feed
