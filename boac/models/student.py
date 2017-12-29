from boac import db
import boac.api.util as api_util
from boac.lib import util
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
    def get_students(cls, gpa_ranges=None, group_codes=None, in_intensive_cohort=None, levels=None, majors=None,
                     unit_ranges_eligibility=None, unit_ranges_pacing=None, order_by=None, offset=0, limit=50):
        # TODO: unit ranges
        query = """
            FROM students s
                JOIN normalized_cache_students n ON n.sid = s.sid
                LEFT JOIN student_athletes sa ON sa.sid = s.sid
                LEFT JOIN normalized_cache_student_majors m ON m.sid = s.sid
            WHERE
        """
        and_operator = False
        all_bindings = {}
        if group_codes:
            args = sqlalchemy_bindings(group_codes, 'group_code')
            all_bindings.update(args)
            query += ' sa.group_code IN ({})'.format(':' + ', :'.join(args.keys()))
            and_operator = True
        if gpa_ranges:
            # 'sqlalchemy_bindings' is not used here due to extravagant SQL syntax.
            query += ' AND ' if and_operator else ''
            query += ' n.gpa <@ ANY(ARRAY[{}])'.format(', '.join(gpa_ranges))
            and_operator = True
        if levels:
            query += ' AND ' if and_operator else ''
            args = sqlalchemy_bindings(levels, 'level')
            all_bindings.update(args)
            query += ' n.level IN ({})'.format(':' + ', :'.join(args.keys()))
            and_operator = True
        if majors:
            query += ' AND ' if and_operator else ''
            args = sqlalchemy_bindings(majors, 'major')
            all_bindings.update(args)
            query += ' m.major IN ({})'.format(':' + ', :'.join(args.keys()))
        if in_intensive_cohort is not None:
            query += ' s.in_intensive_cohort IS {}'.format(str(in_intensive_cohort))
        # First, get total_count of matching students
        connection = db.engine.connect()
        result = connection.execute(text(f'SELECT COUNT(DISTINCT(s.sid)) {query}'), **all_bindings)
        total_count = result.fetchone()[0]
        # Next, get matching students per order_by, offset, limit
        o = 's.first_name'
        if order_by in ['first_name', 'in_intensive_cohort', 'last_name']:
            o = f's.{order_by}'
        elif order_by in ['group_code']:
            o = f'sa.{order_by}'
        elif order_by in ['gpa', 'level', 'units']:
            o = f'n.{order_by}'
        elif order_by in ['major']:
            o = f'm.{order_by}'
        sql = f'SELECT DISTINCT(s.sid), {o} {query} ORDER BY {o} OFFSET {offset}'
        sql += f' LIMIT {limit}' if limit else ''
        # SQLAlchemy will escape parameter values
        result = connection.execute(text(sql), **all_bindings)
        connection.close()
        # Model query using list of SIDs
        sid_list = util.get_distinct_with_order([row['sid'] for row in result])
        students = cls.query.filter(cls.sid.in_(sid_list)).all() if sid_list else []
        # Order of students from query (above) might not match order of sid_list.
        students = [next(s for s in students if s.sid == sid) for sid in sid_list]
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

    def to_api_json(self):
        return api_util.student_to_json(self)

    def to_expanded_api_json(self):
        api_json = self.to_api_json()
        if self.athletics:
            api_json['athletics'] = [a.to_api_json() for a in self.athletics]
        return api_json
