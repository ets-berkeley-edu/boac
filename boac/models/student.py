from boac import db, std_commit
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
    is_active_asc = db.Column(db.Boolean, nullable=False, default=True)
    status_asc = db.Column(db.String(80))

    def __repr__(self):
        return f'<Athlete sid={self.sid}, uid={self.uid}, first_name={self.first_name}, last_name={self.last_name}, ' \
               f'in_intensive_cohort={self.in_intensive_cohort}, is_active_asc={self.is_active_asc}, status_asc={self.status_asc}, ' \
               f'updated={self.updated_at}, created={self.created_at}>'

    @classmethod
    def find_by_sid(cls, sid):
        return cls.query.filter_by(sid=sid).first()

    @classmethod
    def get_students(
            cls,
            gpa_ranges=None,
            group_codes=None,
            in_intensive_cohort=None,
            levels=None,
            majors=None,
            unit_ranges_eligibility=None,
            unit_ranges_pacing=None,
            order_by=None,
            offset=0,
            limit=50,
            sids_only=False,
            is_inactive=False,
    ):
        # TODO: unit ranges
        query_tables, query_filter, all_bindings = cls.get_students_query(group_codes, gpa_ranges, levels, majors, in_intensive_cohort, is_inactive)
        # First, get total_count of matching students
        connection = db.engine.connect()
        result = connection.execute(text(f'SELECT DISTINCT(s.sid) {query_tables} {query_filter}'), **all_bindings)
        summary = {
            'totalStudentCount': result.rowcount,
        }
        if sids_only:
            rows = result.fetchall()
            connection.close()
            summary.update({
                'sids': [row[0] for row in rows],
            })
        else:
            # Next, get matching students per order_by, offset, limit
            o = 's.first_name'
            if order_by == 'level':
                # Sort by an implicit value, not a column in db
                o = 'ol.ordinal'
            elif order_by in ['first_name', 'in_intensive_cohort', 'last_name']:
                o = f's.{order_by}'
            elif order_by in ['gpa', 'units']:
                o = f'n.{order_by}'
            elif order_by in ['group_name']:
                # In the special case where team group name is both a filter criterion and an ordering criterion, we have to do extra work.
                # The athletics join specified in get_students_query join will include only those group names that are in filter criteria, but if
                # any students are in multiple team groups, ordering may depend on group names not present in filter criteria; so we have to join
                # the athletics rows a second time.
                # Why not do this complex sorting after the query? Because correctly calculating pagination offsets requires filtering and ordering
                # to be done at the SQL level.
                if group_codes:
                    query_tables += """LEFT JOIN student_athletes sa2 ON sa2.sid = s.sid
                                       LEFT JOIN athletics a2 ON a2.group_code = sa2.group_code"""
                    o = f'a2.{order_by}'
                else:
                    o = f'a.{order_by}'
            elif order_by in ['major']:
                # Majors, like group names, require extra handling in the special case where they are both filter criteria and ordering criteria.
                if majors:
                    query_tables += ' LEFT JOIN normalized_cache_student_majors m2 ON m2.sid = s.sid'
                    o = f'm2.{order_by}'
                else:
                    o = f'm.{order_by}'
            o_secondary = 's.last_name' if order_by == 'first_name' else 's.first_name'
            sql = f'SELECT DISTINCT(s.sid), {o}, {o_secondary} {query_tables} {query_filter} ORDER BY {o}, {o_secondary} OFFSET {offset}'
            sql += f' LIMIT {limit}' if limit else ''
            # SQLAlchemy will escape parameter values
            result = connection.execute(text(sql), **all_bindings)
            # Model query using list of SIDs
            sid_list = util.get_distinct_with_order([row['sid'] for row in result])
            connection.close()
            students = cls.query.filter(cls.sid.in_(sid_list)).all() if sid_list else []
            # Order of students from query (above) might not match order of sid_list.
            students = [next(s for s in students if s.sid == sid) for sid in sid_list]
            summary.update({
                'students': [student.to_expanded_api_json() for student in students],
            })
        return summary

    @classmethod
    def get_all(cls, order_by=None, include_inactive=False):
        query = Student.query
        if not include_inactive:
            query = query.filter(cls.is_active_asc.is_(True))
        students = query.options(joinedload('athletics')).all()
        if order_by and len(students) > 0:
            # For now, only one order_by value is supported
            if order_by == 'groupName':
                students = sorted(students, key=lambda student: student.athletics and student.athletics[0].group_name)
        return [s.to_expanded_api_json() for s in students]

    @classmethod
    def get_students_query(cls, group_codes, gpa_ranges, levels, majors, in_intensive_cohort, is_inactive):
        query_tables = """
            FROM students s
                JOIN normalized_cache_students n ON n.sid = s.sid
                LEFT JOIN student_athletes sa ON sa.sid = s.sid
                LEFT JOIN athletics a ON a.group_code = sa.group_code
                LEFT JOIN normalized_cache_student_majors m ON m.sid = s.sid
                LEFT JOIN (VALUES
                    (1, 'Freshman'),
                    (2, 'Sophomore'),
                    (3, 'Junior'),
                    (4, 'Senior'),
                    (5, 'Graduate')
                ) AS ol (ordinal, level) ON n.level = ol.level
        """
        query_filter = """
            WHERE
                s.is_active_asc IS {}
        """.format(not is_inactive)
        all_bindings = {}
        if group_codes:
            args = sqlalchemy_bindings(group_codes, 'group_code')
            all_bindings.update(args)
            query_filter += ' AND sa.group_code IN ({})'.format(':' + ', :'.join(args.keys()))
        if gpa_ranges:
            # 'sqlalchemy_bindings' is not used here due to extravagant SQL syntax.
            query_filter += ' AND n.gpa <@ ANY(ARRAY[{}])'.format(', '.join(gpa_ranges))
        if levels:
            args = sqlalchemy_bindings(levels, 'level')
            all_bindings.update(args)
            query_filter += ' AND n.level IN ({})'.format(':' + ', :'.join(args.keys()))
        if majors:
            args = sqlalchemy_bindings(majors, 'major')
            all_bindings.update(args)
            query_filter += ' AND m.major IN ({})'.format(':' + ', :'.join(args.keys()))
        if in_intensive_cohort is not None:
            query_filter += ' AND s.in_intensive_cohort IS {}'.format(str(in_intensive_cohort))
        return query_tables, query_filter, all_bindings

    @classmethod
    def delete_student(cls, sid):
        student = Student.query.filter(Student.sid == sid).first()
        student.athletics = []
        db.session.delete(student)
        std_commit()
        return

    def to_api_json(self):
        return api_util.student_to_json(self)

    def to_expanded_api_json(self):
        api_json = self.to_api_json()
        if self.athletics:
            api_json['athletics'] = sorted((a.to_api_json() for a in self.athletics), key=lambda a: a['groupName'])
        return api_json
