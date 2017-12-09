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
    def all_teams(cls):
        results = db.session.query(cls.code,
                                   cls.asc_sport_core,
                                   func.count(func.distinct(cls.member_uid))).order_by(cls.asc_sport_core).group_by(cls.code,
                                                                                                                    cls.asc_sport_core).all()

        def translate_row(row):
            return {
                'code': row[0],
                'name': row[1],
                'totalMemberCount': row[2],
            }
        return [translate_row(row) for row in results]

    @classmethod
    def all_team_groups(cls):
        results = db.session.query(cls.code,
                                   cls.asc_sport_code_core,
                                   cls.asc_sport_core,
                                   cls.asc_sport_code,
                                   cls.asc_sport,
                                   func.count(cls.member_uid)).order_by(cls.asc_sport).group_by(cls.asc_sport_code,
                                                                                                cls.code,
                                                                                                cls.asc_sport_code_core,
                                                                                                cls.asc_sport_core,
                                                                                                cls.asc_sport).all()

        def translate_row(row):
            return {
                'teamCode': row[0],
                'sportCode': row[1],
                'sportName': row[2],
                'teamGroupCode': row[3],
                'teamGroupName': row[4],
                'totalMemberCount': row[5],
            }
        return [translate_row(row) for row in results]

    @classmethod
    def get_all_athletes(cls, order_by=None):
        athletes = cls.query.order_by(cls.first_name).all()
        athletes = [athlete.to_api_json() for athlete in athletes]
        if order_by and len(athletes) > 0:
            is_valid_key = order_by in athletes[0]
            athletes = sorted(athletes, key=lambda athlete: athlete[order_by]) if is_valid_key else athletes
        return athletes

    @classmethod
    def get_intensive_cohort(cls, order_by=None, offset=0, limit=50):
        athletes = cls.query.distinct(cls.asc_sport_code).filter_by(in_intensive_cohort=True).all()
        team_groups = [athlete.team_group_summary() for athlete in athletes]
        query_filter = cls.in_intensive_cohort.is_(True)
        o = cls.get_ordering(order_by)
        athletes = cls.query.distinct(o, cls.member_uid).order_by(o, cls.member_uid).filter(query_filter).offset(offset).limit(limit).all()
        return cls.summarize_athletes(team_groups, athletes, query_filter)

    @classmethod
    def get_team(cls, code, order_by=None, offset=0, limit=50):
        team = None
        if cls.team_definitions.get(code):
            team = {
                'code': code,
                'name': cls.team_definitions.get(code, code),
            }
            results = cls.query.distinct(cls.asc_sport_code).filter_by(code=code).all()
            team_group_codes = [row.asc_sport_code for row in results]
            # Add athletes list to the team
            team.update(cls.get_athletes(team_group_codes, order_by, offset, limit))
        return team

    @classmethod
    def get_athletes(cls, team_group_codes, order_by=None, offset=0, limit=50):
        team_groups = cls.get_team_groups(team_group_codes)
        query_filter = cls.asc_sport_code.in_(team_group_codes)
        o = cls.get_ordering(order_by)
        athletes = cls.query.distinct(o, cls.member_uid).order_by(o, cls.member_uid).filter(query_filter).offset(offset).limit(limit).all()
        return cls.summarize_athletes(team_groups, athletes, query_filter)

    @classmethod
    def summarize_athletes(cls, team_groups, athletes, query_filter):
        summary = {
            'members': [],
            'teamGroups': team_groups,
            'totalMemberCount': 0,
        }
        for athlete in athletes:
            member = athlete.to_api_json()
            summary['members'].append(member)

        summary['totalMemberCount'] = cls.query.distinct(cls.member_uid).filter(query_filter).count()
        return summary

    @classmethod
    def get_team_groups(cls, team_group_codes):
        query_filter = cls.asc_sport_code.in_(team_group_codes)
        athletes = cls.query.distinct(cls.asc_sport_code).filter(query_filter).all()
        return [athlete.team_group_summary() for athlete in athletes]

    @classmethod
    def get_ordering(cls, order_by):
        return cls.last_name if order_by == 'last_name' else cls.first_name

    def to_api_json(self, details=False):
        feed = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'sid': self.member_csid,
            'inAdvisorWatchGroup': self.in_intensive_cohort,
            'sportCode': self.asc_sport_code_core,
            'sportName': self.asc_sport_core,
            'teamCode': self.code,
            'teamGroupCode': self.asc_sport_code,
            'teamGroupName': self.asc_sport,
            'uid': self.member_uid,
        }
        return feed

    def team_group_summary(self):
        return {
            'sportCode': self.asc_sport_code_core,
            'sportName': self.asc_sport_core,
            'teamCode': self.code,
            'teamGroupCode': self.asc_sport_code,
            'teamGroupName': self.asc_sport,
        }
