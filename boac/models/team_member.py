"""Team membership"""

from boac import db
from boac.api.util import canvas_courses_api_feed
from boac.externals import canvas
from boac.lib.analytics import mean_course_analytics_for_user
from boac.models.base import Base
from flask import current_app as app
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
                'totalMemberCount': row[1],
                'name': cls.team_definitions.get(row[0], row[0]),
            }
        teams = [translate_row(row) for row in results]
        return sorted(teams, key=lambda team: team[sort_by])

    @classmethod
    def all_athletes(cls, sort_by=None):
        athletes = cls.query.order_by(cls.member_name).all()

        athletes = [athlete.to_api_json() for athlete in athletes]
        if sort_by and len(athletes) > 0:
            is_valid_key = sort_by in athletes[0]
            athletes = sorted(athletes, key=lambda athlete: athlete[sort_by]) if is_valid_key else athletes

        return athletes

    @classmethod
    def for_code(cls, code, order_by='member_name', offset=0, limit=50):
        team = {
            'code': code,
            'name': cls.team_definitions.get(code, code),
            'totalMemberCount': TeamMember.query.filter_by(code=code).count(),
        }
        # Update object, at the base level, with 'members' list
        team.update(TeamMember.get_team_members([code], True, order_by, offset, limit))
        return team

    @classmethod
    def get_team_members(cls, team_codes, include_canvas_profiles=False, order_by='member_name', offset=0, limit=50):
        summary = {
            'teams': [],
        }
        for code in team_codes:
            summary['teams'].append({
                'code': code,
                'name': cls.team_definitions.get(code),
            })
        o = TeamMember.member_uid if order_by == 'member_uid' else TeamMember.member_name
        f = TeamMember.code.in_(team_codes)
        results = TeamMember.query.distinct(o).order_by(o).filter(f).offset(offset).limit(limit).all()

        summary['members'] = []

        for row in results:
            member = row.to_api_json()
            if include_canvas_profiles:
                uid = member['uid']
                cache_key = 'user/{uid}'.format(uid=uid)
                canvas_profile = app.cache.get(cache_key) if app.cache else None
                if not canvas_profile:
                    canvas_profile = canvas.get_user_for_uid(uid)
                    # Cache Canvas profiles
                    if app.cache and canvas_profile:
                        app.cache.set(cache_key, canvas_profile)

                if canvas_profile:
                    member['avatar_url'] = canvas_profile['avatar_url']
                    student_courses = canvas.get_student_courses(uid)
                    current_term = app.config.get('CANVAS_CURRENT_ENROLLMENT_TERM')
                    student_courses_in_current_term = [course for course in student_courses if
                                                       course.get('term', {}).get('name') == current_term]
                    canvas_courses = canvas_courses_api_feed(student_courses_in_current_term)
                    if canvas_courses:
                        member['analytics'] = mean_course_analytics_for_user(canvas_courses,
                                                                             canvas_profile['id'],
                                                                             current_term)
            summary['members'].append(member)

        summary['totalMemberCount'] = TeamMember.query.distinct(o).filter(f).count()
        db.session.commit()
        return summary

    def to_api_json(self):
        return {
            'id': self.id,
            'name': self.member_name,
            'sid': self.member_csid,
            'sport': self.asc_sport,
            'teamCode': self.code,
            'uid': self.member_uid,
        }
