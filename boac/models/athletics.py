from boac import db
from boac.models.base import Base
from boac.models.student import Student
from sqlalchemy import func


student_athletes = db.Table(
    'student_athletes',
    Base.metadata,
    db.Column('group_code', db.String(80), db.ForeignKey('athletics.group_code'), primary_key=True),
    db.Column('sid', db.String(80), db.ForeignKey('students.sid'), primary_key=True),
)


class Athletics(Base):
    __tablename__ = 'athletics'

    group_code = db.Column(db.String(80), nullable=False, primary_key=True)
    group_name = db.Column(db.String(255))
    team_code = db.Column(db.String(80))
    team_name = db.Column(db.String(255))
    athletes = db.relationship('Student', secondary=student_athletes)

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
        results = query.join(Athletics.athletes).order_by(*order_by).group_by(*order_by).all()

        def translate_row(row):
            return {
                'teamGroupCode': row[0],
                'teamGroupName': row[1],
                'teamCode': row[2],
                'sportName': row[3],
                'totalMemberCount': row[4],
            }
        return [translate_row(row) for row in results]

    @classmethod
    def all_teams(cls):
        query = db.session.query(cls.team_code, cls.team_name, func.count(func.distinct(Student.sid)))
        order_by = [cls.team_name, cls.team_code]
        results = query.distinct(cls.team_name).join(Athletics.athletes).order_by(*order_by).group_by(*order_by).all()

        def translate_row(row):
            return {
                'code': row[0],
                'name': row[1],
                'totalMemberCount': row[2],
            }
        return [translate_row(row) for row in results]
