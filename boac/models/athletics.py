"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


from boac import db
from boac.models.base import Base
from boac.models.db_relationships import student_athletes
from boac.models.student import Student
from sqlalchemy import func


class Athletics(Base):
    __tablename__ = 'athletics'

    group_code = db.Column(db.String(80), nullable=False, primary_key=True)
    group_name = db.Column(db.String(255))
    team_code = db.Column(db.String(80))
    team_name = db.Column(db.String(255))
    athletes = db.relationship('Student', secondary=student_athletes, back_populates='athletics')

    def __repr__(self):
        return '<TeamGroup {} ({}), team {} ({}), updated={}, created={}>'.format(
            self.group_name,
            self.group_code,
            self.team_code,
            self.team_name,
            self.updated_at,
            self.created_at,
        )

    @classmethod
    def all_team_groups(cls):
        query = db.session.query(cls.group_code, cls.group_name, cls.team_code, cls.team_name, func.count(Student.sid))
        order_by = [cls.group_name, cls.group_code]
        results = query.join(Athletics.athletes).filter(Student.is_active_asc.is_(True)).order_by(*order_by).group_by(*order_by).all()

        def translate_row(row):
            return {
                'groupCode': row[0],
                'groupName': row[1],
                'name': row[1],
                'teamCode': row[2],
                'teamName': row[3],
                'totalStudentCount': row[4],
            }
        return [translate_row(row) for row in results]

    @classmethod
    def get_team_groups(cls, group_codes):
        query_filter = cls.group_code.in_(group_codes)
        athletes = cls.query.order_by(cls.group_name).distinct(cls.group_name).filter(query_filter).all()
        return [athlete.to_api_json() for athlete in athletes]

    @classmethod
    def all_teams(cls):
        query = db.session.query(cls.team_code, cls.team_name, func.count(func.distinct(Student.sid)))
        query = query.distinct(cls.team_name).join(Athletics.athletes).filter(Student.is_active_asc.is_(True))
        order_by = [cls.team_name, cls.team_code]
        results = query.order_by(*order_by).group_by(*order_by).all()

        def translate_row(row):
            return {
                'code': row[0],
                'name': row[1],
                'totalStudentCount': row[2],
            }
        return [translate_row(row) for row in results]

    @classmethod
    def get_team(cls, team_code, order_by):
        results = db.session.query(
            cls.team_code,
            cls.team_name,
            cls.group_code,
            cls.group_name,
        ).filter(cls.team_code == team_code).all()
        team = None
        if len(results):
            team = {
                'teamGroups': [],
            }
            for row in results:
                team['code'] = row[0]
                team['name'] = row[1]
                team['teamGroups'].append({
                    'groupCode': row[2],
                    'groupName': row[3],
                })
            group_codes = [group['groupCode'] for group in team['teamGroups']]
            results = Student.get_students(
                group_codes=group_codes,
                is_active_asc=True,
                order_by=order_by,
                offset=0,
                limit=None,
            )
            team['students'] = results['students']
            team['totalStudentCount'] = results['totalStudentCount']
        return team

    def to_api_json(self):
        return {
            'groupCode': self.group_code,
            'groupName': self.group_name,
            'name': self.group_name,
            'teamCode': self.team_code,
            'teamName': self.team_name,
        }
