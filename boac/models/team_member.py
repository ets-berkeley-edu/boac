"""Team membership"""

from boac import db
from boac.models.base import Base
from sqlalchemy import func, UniqueConstraint


class TeamMember(Base):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    code = db.Column(db.String(255), nullable=False)
    member_uid = db.Column(db.String(80))
    member_csid = db.Column(db.String(80), nullable=False)
    member_name = db.Column(db.String(255))
    asc_sport_code_core = db.Column(db.String(80))
    asc_sport_code = db.Column(db.String(80))
    asc_sport = db.Column(db.String(80))
    asc_sport_core = db.Column(db.String(80))
    UniqueConstraint('code', 'member_csid', name='team_member')

    def __repr__(self):
        return '<TeamMember {} ({}), asc_sport {} ({}), asc_sport_core {} ({}), uid={}, csid={}, name={}, updated={}, created={}>'.format(
            self.team_definitions.get(self.code),
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
    def all_teams(cls, sort_by='name'):
        results = db.session.query(cls.code, func.count(cls.member_uid)).group_by(cls.code).all()

        def translate_row(row):
            return {
                'code': row[0],
                'name': cls.team_definitions.get(row[0], row[0]),
                'memberCount': row[1],
            }
        teams = [translate_row(row) for row in results]
        return sorted(teams, key=lambda team: team[sort_by])

    @classmethod
    def all_athletes(cls, sort_by=None):
        athletes = cls.query.order_by(cls.member_name).all()

        def translate_row(athlete):
            return {
                'id': athlete.id,
                'sport': athlete.asc_sport,
                'name': athlete.member_name,
                'sid': athlete.member_csid,
                'uid': athlete.member_uid,
                'teamCode': athlete.code,
            }

        athletes = [translate_row(athlete) for athlete in athletes]
        if sort_by and len(athletes) > 0:
            is_valid_key = sort_by in athletes[0]
            athletes = sorted(athletes, key=lambda athlete: athlete[sort_by]) if is_valid_key else athletes

        return athletes

    @classmethod
    def for_code(cls, code):
        members = cls.query.filter_by(code=code).all()
        return {
            'code': code,
            'name': cls.team_definitions.get(code, code),
            'members': [member.to_api_json() for member in members],
        }

    def to_api_json(self):
        return {
            'name': self.member_name,
            'uid': self.member_uid,
        }
