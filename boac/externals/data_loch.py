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

from datetime import datetime
import re

from boac.lib.berkeley import sis_term_id_for_name
from boac.lib.mockingdata import fixture
from boac.lib.util import tolerant_remove
from boac.models.json_cache import stow
from flask import current_app as app
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text


# Lazy init to support testing.
data_loch_db = None
data_loch_db_rds = None


def safe_execute(string, **kwargs):
    global data_loch_db
    if data_loch_db is None:
        data_loch_db = create_engine(app.config['DATA_LOCH_URI'])
    return _safe_execute(string, data_loch_db, **kwargs)


def safe_execute_rds(string, **kwargs):
    global data_loch_db_rds
    if data_loch_db_rds is None:
        data_loch_db_rds = create_engine(app.config['DATA_LOCH_RDS_URI'])
    return _safe_execute(string, data_loch_db_rds, **kwargs)


def _safe_execute(string, db, **kwargs):
    try:
        s = text(string)
        ts = datetime.now().timestamp()
        dbresp = db.execute(s, **kwargs)
    except sqlalchemy.exc.SQLAlchemyError as err:
        app.logger.error(f'SQL {s} threw {err}')
        return None
    rows = dbresp.fetchall()
    query_time = datetime.now().timestamp() - ts
    row_array = [dict(r) for r in rows]
    app.logger.debug(f'Query returned {len(row_array)} rows in {query_time} seconds:\n{string}\n{kwargs}')
    return row_array


def asc_schema():
    return app.config['DATA_LOCH_ASC_SCHEMA']


def boac_schema():
    return app.config['DATA_LOCH_BOAC_SCHEMA']


def coe_schema():
    return app.config['DATA_LOCH_COE_SCHEMA']


def intermediate_schema():
    return app.config['DATA_LOCH_INTERMEDIATE_SCHEMA']


def student_schema():
    return app.config['DATA_LOCH_STUDENT_SCHEMA']


def cutoff_term_id():
    return sis_term_id_for_name(app.config['CANVAS_EARLIEST_TERM'])


@stow('loch_canvas_course_scores_{course_id}', for_term=True)
def get_canvas_course_scores(course_id, term_id):
    return _get_canvas_course_scores(course_id)


@fixture('loch_canvas_course_scores_{course_id}.csv')
def _get_canvas_course_scores(course_id):
    sql = f"""SELECT
                canvas_user_id,
                current_score,
                EXTRACT(EPOCH FROM last_activity_at) AS last_activity_at,
                sis_enrollment_status
              FROM {boac_schema()}.course_enrollments
              WHERE course_id={course_id}
              ORDER BY canvas_user_id
        """
    return safe_execute(sql)


def get_sis_enrollments(uid, term_id):
    return _get_sis_enrollments(uid, term_id)


@fixture('loch_sis_enrollments_{uid}_{term_id}.csv')
def _get_sis_enrollments(uid, term_id):
    sql = f"""SELECT
                  enr.grade, enr.units, enr.grading_basis, enr.sis_enrollment_status, enr.sis_term_id, enr.ldap_uid,
                  crs.sis_course_title, crs.sis_course_name,
                  crs.sis_section_id, crs.sis_primary, crs.sis_instruction_format, crs.sis_section_num
              FROM {intermediate_schema()}.sis_enrollments enr
              JOIN {intermediate_schema()}.course_sections crs
                  ON crs.sis_section_id = enr.sis_section_id
                  AND crs.sis_term_id = enr.sis_term_id
              WHERE enr.ldap_uid = {uid}
                  AND enr.sis_enrollment_status != 'D'
                  AND enr.sis_term_id = {term_id}
              ORDER BY crs.sis_course_name, crs.sis_primary DESC, crs.sis_instruction_format, crs.sis_section_num
        """
    return safe_execute(sql)


@fixture('loch_sis_section_{term_id}_{sis_section_id}.csv')
def get_sis_section(term_id, sis_section_id):
    sql = f"""SELECT
                  sc.sis_term_id, sc.sis_section_id, sc.sis_course_title, sc.sis_course_name,
                  sc.is_primary, sc.sis_instruction_format, sc.sis_section_num, sc.allowed_units,
                  sc.instructor_uid, sc.instructor_name, sc.instructor_role_code,
                  sc.meeting_location, sc.meeting_days,
                  sc.meeting_start_time, sc.meeting_end_time, sc.meeting_start_date, sc.meeting_end_date
              FROM {intermediate_schema()}.sis_sections sc
              WHERE sc.sis_section_id = {sis_section_id}
                  AND sc.sis_term_id = {term_id}
              ORDER BY sc.meeting_days, sc.meeting_start_time, sc.meeting_end_time, sc.instructor_name
        """
    return safe_execute(sql)


@fixture('loch_sis_section_enrollments_{term_id}_{sis_section_id}.csv')
def get_sis_section_enrollments(term_id, sis_section_id, scope):
    query_tables = _student_query_tables_for_scope(scope)
    if not query_tables:
        return []
    sql = f"""SELECT DISTINCT sas.sid, sas.first_name, sas.last_name
              {query_tables}
              JOIN {intermediate_schema()}.sis_enrollments enr
                ON sas.uid = enr.ldap_uid
                AND enr.sis_term_id = :term_id
                AND enr.sis_section_id = :sis_section_id
              ORDER BY sas.last_name, sas.first_name, sas.sid
        """
    params = {'term_id': term_id, 'sis_section_id': sis_section_id}
    return safe_execute(sql, **params)


@stow('loch_sis_sections_in_canvas_course_{canvas_course_id}', for_term=True)
def get_sis_sections_in_canvas_course(canvas_course_id, term_id):
    return _get_sis_sections_in_canvas_course(canvas_course_id)


@fixture('loch_sis_sections_in_canvas_course_{canvas_course_id}.csv')
def _get_sis_sections_in_canvas_course(canvas_course_id):
    # The GROUP BY clause eliminates duplicates when multiple site sections include the same SIS class section.
    sql = f"""SELECT sis_section_id
        FROM {intermediate_schema()}.course_sections
        WHERE canvas_course_id={canvas_course_id}
        GROUP BY sis_section_id
        """
    return safe_execute(sql)


@stow('loch_student_canvas_courses_{uid}.csv')
def get_student_canvas_courses(uid):
    return _get_student_canvas_courses(uid)


@fixture('loch_student_canvas_courses_{uid}.csv')
def _get_student_canvas_courses(uid):
    sql = f"""SELECT DISTINCT enr.canvas_course_id, cs.canvas_course_name, cs.canvas_course_code, cs.canvas_course_term
        FROM {intermediate_schema()}.active_student_enrollments enr
        JOIN {intermediate_schema()}.course_sections cs
            ON cs.canvas_course_id = enr.canvas_course_id
        WHERE enr.uid = {uid}
        """
    return safe_execute(sql)


def get_all_teams():
    sql = f"""SELECT team_code, team_name, COUNT(DISTINCT sid)
        FROM {asc_schema()}.students
        WHERE active = TRUE
        AND team_code IS NOT NULL
        GROUP BY team_name, team_code
        ORDER BY team_name"""
    return safe_execute_rds(sql)


def get_team_groups(group_codes=None, team_code=None):
    params = {}
    sql = f"""SELECT group_code, group_name, team_code, team_name, COUNT(DISTINCT sid)
        FROM {asc_schema()}.students
        WHERE active = TRUE
        AND team_code IS NOT NULL"""
    if group_codes:
        sql += ' AND group_code = ANY(:group_codes)'
        params.update({'group_codes': group_codes})
    if team_code:
        sql += ' AND team_code = :team_code'
        params.update({'team_code': team_code})
    sql += """ GROUP BY group_code, group_name, team_code, team_name
        ORDER BY group_name, group_code"""
    return safe_execute_rds(sql, **params)


def get_athletics_profiles(sids):
    sql = f"""SELECT sid, profile
        FROM {asc_schema()}.student_profiles
        WHERE sid = ANY(:sids)
        """
    return safe_execute(sql, sids=sids)


def get_all_student_ids():
    sql = f"""SELECT sid, uid
        FROM {student_schema()}.student_academic_status
        """
    return safe_execute_rds(sql)


def get_student_for_uid_and_scope(uid, scope):
    query_tables = _student_query_tables_for_scope(scope)
    if not query_tables:
        return None
    sql = f"""SELECT sas.*
        {query_tables}
        WHERE sas.uid = :uid"""
    rows = safe_execute_rds(sql, uid=uid)
    return None if not rows or (len(rows) == 0) else rows[0]


def get_student_profiles(sids):
    sql = f"""SELECT sid, profile
        FROM {student_schema()}.student_profiles
        WHERE sid = ANY(:sids)
        """
    return safe_execute(sql, sids=sids)


def get_enrollments_for_sid(sid):
    sql = f"""SELECT term_id, enrollment_term
        FROM {student_schema()}.student_enrollment_terms
        WHERE sid = :sid
        AND term_id >= '{cutoff_term_id()}'"""
    sql += ' ORDER BY term_id DESC'
    return safe_execute(sql, sid=sid)


def get_enrollments_for_term(term_id, sids):
    sql = f"""SELECT sid, enrollment_term
        FROM {student_schema()}.student_enrollment_terms
        WHERE term_id = :term_id
        AND sid = ANY(:sids)
        """
    return safe_execute(sql, term_id=term_id, sids=sids)


@stow('loch_submissions_turned_in_relative_to_user_{course_id}_{user_id}', for_term=True)
def get_submissions_turned_in_relative_to_user(course_id, user_id, term_id):
    return _get_submissions_turned_in_relative_to_user(course_id, user_id)


@fixture('loch_submissions_turned_in_relative_to_user_{course_id}_{user_id}.csv')
def _get_submissions_turned_in_relative_to_user(course_id, user_id):
    sql = f"""SELECT canvas_user_id,
        COUNT(CASE WHEN
          assignment_status IN ('graded', 'late', 'on_time', 'submitted')
        THEN 1 ELSE NULL END) AS submissions_turned_in
        FROM {boac_schema()}.assignment_submissions_scores
        WHERE assignment_id IN
        (
          SELECT DISTINCT assignment_id FROM {boac_schema()}.assignment_submissions_scores
          WHERE canvas_user_id = {user_id} AND course_id = {course_id}
        )
        GROUP BY canvas_user_id
        HAVING count(*) = (
          SELECT count(*) FROM {boac_schema()}.assignment_submissions_scores
          WHERE canvas_user_id = {user_id} AND course_id = {course_id}
        )
        """
    return safe_execute(sql)


@stow('loch_user_for_uid_{uid}')
def get_user_for_uid(uid):
    rows = _get_user_for_uid(uid)
    return False if not rows or (len(rows) == 0) else rows[0]


@fixture('loch_user_for_uid_{uid}.csv')
def _get_user_for_uid(uid):
    sql = f"""SELECT canvas_id, name, uid
        FROM {intermediate_schema()}.users
        WHERE uid = {uid}
        """
    return safe_execute(sql)


def get_majors(scope=[]):
    query_tables = _student_query_tables_for_scope(scope)
    if not query_tables:
        return []
    sql = f"""SELECT DISTINCT maj.major AS major
        {query_tables}
        JOIN {student_schema()}.student_majors maj ON maj.sid = sas.sid
        ORDER BY major"""
    return safe_execute_rds(sql)


def get_students_query(
        search_phrase=None,
        group_codes=None,
        gpa_ranges=None,
        levels=None,
        majors=None,
        unit_ranges=None,
        in_intensive_cohort=None,
        is_active_asc=None,
        advisor_ldap_uid=None,
        scope=[],
):  # noqa
    query_tables = _student_query_tables_for_scope(scope)
    if not query_tables:
        return None, None, None
    query_filter = ' WHERE true'
    query_bindings = {}

    # Name or SID search
    if search_phrase:
        phrase = ' '.join(f'{word}%' for word in search_phrase.split())
        query_filter += """
            AND (sas.sid ILIKE :phrase OR
                (sas.first_name || ' ' || sas.last_name) ILIKE :phrase OR
                (sas.first_name || ' ' || sas.last_name) ILIKE :phrase_padded OR
                (sas.last_name || ' ' || sas.first_name) ILIKE :phrase OR
                (sas.last_name || ' ' || sas.first_name) ILIKE :phrase_padded)
        """
        query_bindings.update({
            'phrase': phrase,
            'phrase_padded': f'% {phrase}',
        })

    # Generic SIS criteria
    if gpa_ranges:
        query_filter += numranges_to_sql('sas.gpa', gpa_ranges)
    if levels:
        query_filter += ' AND sas.level = ANY(:levels)'
        query_bindings.update({'levels': [level_to_code(l) for l in levels]})
    if majors:
        # Only modify the majors list clone
        _majors = majors.copy()
        major_filters = []
        # Afaik, no student can declare a major and remain undeclared. However, in the interest of surfacing
        # front-end bugs we do not use an 'if...else' below. We expect the front-end to be smart.
        if tolerant_remove(_majors, 'Declared'):
            major_filters.append('NOT maj.major ~* \'undeclared\'')
        if tolerant_remove(_majors, 'Undeclared'):
            major_filters.append('maj.major ~* \'undeclared\'')
        if _majors:
            major_filters.append('maj.major = ANY(:majors)')
        query_filter += ' AND (' + ' OR '.join(major_filters) + ')'
        query_tables += f' LEFT JOIN {student_schema()}.student_majors maj ON maj.sid = sas.sid'
        query_bindings.update({'majors': _majors})
    if unit_ranges:
        query_filter += numranges_to_sql('sas.units', unit_ranges)

    # ASC criteria
    if is_active_asc is not None:
        query_filter += ' AND s.active IS :is_active_asc'
        query_bindings.update({'is_active_asc': is_active_asc})
    if in_intensive_cohort is not None:
        query_filter += f' AND s.intensive IS :in_intensive_cohort'
        query_bindings.update({
            'in_intensive_cohort': in_intensive_cohort,
        })
    if group_codes:
        query_filter += ' AND s.group_code = ANY(:group_codes)'
        query_bindings.update({'group_codes': group_codes})

    # COE criteria
    if advisor_ldap_uid:
        query_filter += ' AND s.advisor_ldap_uid = :advisor_ldap_uid'
        query_bindings.update({'advisor_ldap_uid': advisor_ldap_uid})

    return query_tables, query_filter, query_bindings


def get_students_ordering(order_by=None, group_codes=None, majors=None):
    supplemental_query_tables = None
    # Case-insensitive sort of first_name and last_name.
    by_first_name = naturalize_order('sas.first_name')
    by_last_name = naturalize_order('sas.last_name')
    o = by_last_name
    if order_by == 'in_intensive_cohort':
        o = 's.intensive'
    elif order_by in ['first_name', 'last_name']:
        o = naturalize_order(f'sas.{order_by}')
    elif order_by in ['gpa', 'units', 'level']:
        o = f'sas.{order_by}'
    elif order_by == 'group_name':
        # In the special case where team group name is both a filter criterion and an ordering criterion, we
        # have to do extra work. The athletics join specified in get_students_query join will include only
        # those group names that are in filter criteria, but if any students are in multiple team groups,
        # ordering may depend on group names not present in filter criteria; so we have to join the athletics
        # rows a second time. Why not do this complex sorting after the query? Because correctly calculating
        # pagination offsets requires filtering and ordering to be done at the SQL level.
        if group_codes:
            supplemental_query_tables = f' LEFT JOIN {asc_schema()}.students s2 ON s2.sid = sas.sid'
            o = naturalize_order('s2.group_name')
        else:
            o = naturalize_order('s.group_name')
    elif order_by == 'major':
        # Majors, like group names, require extra handling in the special case where they are both filter
        # criteria and ordering criteria.
        if majors:
            supplemental_query_tables = f' LEFT JOIN {student_schema()}.student_majors maj2 ON maj2.sid = sas.sid'
            o = naturalize_order('maj2.major')
        else:
            supplemental_query_tables = f' LEFT JOIN {student_schema()}.student_majors m ON m.sid = sas.sid'
            o = naturalize_order('m.major')
    o_secondary = by_first_name if order_by == 'last_name' else by_last_name
    diff = {by_first_name, by_last_name} - {o, o_secondary}
    o_tertiary = diff.pop() if diff else 'sas.sid'
    return o, o_secondary, o_tertiary, supplemental_query_tables


def level_to_code(level):
    codes = {
        'Freshman': '10',
        'Sophomore': '20',
        'Junior': '30',
        'Senior': '40',
        'Graduate': 'GR',
    }
    return codes.get(level, level)


def naturalize_order(column_name):
    return f"UPPER(regexp_replace({column_name}, '\\\W', ''))"


def numrange_to_sql(column, numrange):
    # TODO BOAC currently expresses range criteria using Postgres-specific numrange syntax, which must be
    # translated into vanilla SQL for use against Redshift. If we end up keeping these criteria in Redshift
    # long-term, we should look into migrating stored ranges.
    numrange_syntax = re.compile('^numrange\(([0-9\.NUL]+), ([0-9\.NUL]+), \'(.)(.)\'\)$')
    numrange_match = numrange_syntax.match(numrange)
    if numrange_match:
        bounds = []
        if numrange_match[1] != 'NULL':
            lower_bound_condition = '>'
            # Square brackets in numrange syntax indicate an inclusive range.
            if numrange_match[3] == '[' and numrange_match[1] != '0':
                lower_bound_condition += '='
            bounds.append(f'{column} {lower_bound_condition} {numrange_match[1]}')
        if numrange_match[2] != 'NULL':
            upper_bound_condition = '<'
            if numrange_match[4] == ']':
                upper_bound_condition += '='
            bounds.append(f'{column} {upper_bound_condition} {numrange_match[2]}')
        return f"({' AND '.join(bounds)})"


def numranges_to_sql(column, numranges):
    sql_ranges = [numrange_to_sql(column, numrange) for numrange in numranges]
    sql_ranges = [r for r in sql_ranges if r]
    if len(sql_ranges):
        return ' AND (' + ' OR '.join(sql_ranges) + ')'
    else:
        return ''


def _student_query_tables_for_scope(scope):
    if not scope:
        return None
    elif 'ADMIN' in scope:
        table_sql = f"""FROM {student_schema()}.student_academic_status sas"""
    else:
        schemas_for_codes = {
            'UWASC': asc_schema(),
            'COENG': coe_schema(),
        }
        tables = []
        for code in scope:
            schema = schemas_for_codes.get(code)
            if schema:
                tables.append(f'{schema}.students')
        if not tables:
            return None
        elif len(tables) == 1:
            # If we are pulling from a single schema, include all schema-specific columns.
            table_sql = f"""FROM {tables[0]} s
                JOIN {student_schema()}.student_academic_status sas ON sas.sid = s.sid"""
        else:
            # If we are pulling from multiple schemas, SID will be the only common element in the union.
            table_sql = f"""FROM ({' UNION '.join(['SELECT sid FROM ' + t for t in tables])}) s
                JOIN {student_schema()}.student_academic_status sas ON sas.sid = s.sid"""
    return table_sql
