from boac import db
import boac.api.util as api_util
from boac.models.base import Base
from boac.models.db_relationships import student_athletes


class Student(Base):
    __tablename__ = 'students'

    sid = db.Column(db.String(80), nullable=False, primary_key=True)
    uid = db.Column(db.String(80))
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    in_intensive_cohort = db.Column(db.Boolean, nullable=False, default=False)
    athletics = db.relationship('Athletics', secondary=student_athletes, back_populates='athletes')

    def __repr__(self):
        return '<Athlete sid={}, uid={}, first_name={}, last_name={}, in_intensive_cohort={}, updated={}, created={}>'.format(
            self.sid,
            self.uid,
            self.first_name,
            self.last_name,
            self.in_intensive_cohort,
            self.updated_at,
            self.created_at,
        )

    @classmethod
    def in_intensive(cls, order_by=None, offset=0, limit=50):
        o = cls.get_ordering(order_by)
        query_filter = cls.in_intensive_cohort.is_(True)
        students = cls.query.order_by(o).filter(query_filter).offset(offset).limit(limit).all()
        return {
            'students': [student.to_api_json() for student in students],
            'totalStudentCount': cls.query.filter(query_filter).count(),
        }

    @classmethod
    def get_students(cls, criteria, order_by=None, offset=0, limit=50):
        students = []
        total_count = 0
        group_codes = criteria['team_group_codes'] if 'team_group_codes' in criteria else []
        if group_codes:
            o = cls.get_ordering(order_by)
            _filter = student_athletes.c.group_code.in_(group_codes)
            sid_list = db.session.query(student_athletes.c.sid).filter(_filter).all()
            total_count = len(sid_list)
            if sid_list:
                students = cls.query.order_by(o).filter(cls.sid.in_(sid_list)).offset(offset).limit(limit).all()
        return {
            'students': [student.to_api_json() for student in students],
            'totalStudentCount': total_count,
        }

    @classmethod
    def get_all(cls, order_by=None):
        students = Student.query.outerjoin(Student.athletics).all()
        if order_by and len(students) > 0:
            # For now, only one order_by value is supported
            if order_by == 'teamGroupName':
                students = sorted(students, key=lambda student: student.athletics and student.athletics[0].group_name)
        return [s.to_expanded_api_json() for s in students]

    @classmethod
    def get_ordering(cls, order_by):
        return cls.last_name if order_by == 'last_name' else cls.first_name

    def to_api_json(self):
        return api_util.student_to_json(self)

    def to_expanded_api_json(self):
        api_json = self.to_api_json()
        if self.athletics:
            api_json['athletics'] = {}
            for a in self.athletics:
                api_json.update({
                    'teamGroupCode': a.group_code,
                    'teamGroupName': a.group_name,
                    'teamName': a.team_name,
                    'teamCode': a.team_code,
                })
        return api_json
