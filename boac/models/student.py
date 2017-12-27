from boac import db
import boac.api.util as api_util
from boac.models.base import Base
from boac.models.db_relationships import student_athletes
from sqlalchemy import text
from sqlalchemy.orm import joinedload


def sqlalchemy_bindings(values, column_name):
    # In support of SQLAlchemy expression language
    bindings = {}
    for index, value in enumerate(values, start=1):
        bindings[column_name + str(index)] = value
    return bindings


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
    def get_students(cls, gpa_ranges=None, group_codes=None, levels=None, majors=None, unit_ranges_eligibility=None,
                     unit_ranges_pacing=None, order_by=None, offset=0, limit=50):
        # TODO: unit ranges
        students = []
        sql = 'SELECT DISTINCT(s.sid) FROM students s JOIN normalized_cache_students n ON n.sid = s.sid'
        if group_codes:
            sql += ' JOIN student_athletes sa ON sa.sid = s.sid'
        if majors:
            sql += ' JOIN normalized_cache_student_majors m ON m.sid = s.sid'
        sql += ' WHERE'
        and_operator = False
        all_bindings = {}
        if group_codes:
            args = sqlalchemy_bindings(group_codes, 'group_code')
            all_bindings.update(args)
            sql += ' sa.group_code IN ({})'.format(':' + ', :'.join(args.keys()))
            and_operator = True
        if gpa_ranges:
            # 'sqlalchemy_bindings' is not used here due to extravagant SQL syntax.
            sql += ' AND ' if and_operator else ''
            sql += ' n.gpa <@ ANY(ARRAY[{}])'.format(', '.join(gpa_ranges))
            and_operator = True
        if levels:
            sql += ' AND ' if and_operator else ''
            args = sqlalchemy_bindings(levels, 'level')
            all_bindings.update(args)
            sql += ' n.level IN ({})'.format(':' + ', :'.join(args.keys()))
            and_operator = True
        if majors:
            sql += ' AND ' if and_operator else ''
            args = sqlalchemy_bindings(majors, 'major')
            all_bindings.update(args)
            sql += ' m.major IN ({})'.format(':' + ', :'.join(args.keys()))
        connection = db.engine.connect()
        # SQLAlchemy will escape parameter values
        result = connection.execute(text(sql), **all_bindings)
        connection.close()
        sid_list = [row['sid'] for row in result]
        total_count = len(sid_list)
        if sid_list:
            o = cls.get_ordering(order_by)
            students = cls.query.order_by(o).filter(cls.sid.in_(sid_list)).offset(offset).limit(limit).all()
        return {
            'students': [student.to_api_json() for student in students],
            'totalStudentCount': total_count,
        }

    @classmethod
    def get_all(cls, order_by=None):
        students = Student.query.options(joinedload('athletics')).all()
        if order_by and len(students) > 0:
            # For now, only one order_by value is supported
            if order_by == 'groupName':
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
            api_json['athletics'] = [a.to_api_json() for a in self.athletics]
        return api_json
