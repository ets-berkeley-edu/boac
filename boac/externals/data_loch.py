"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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
from flask import current_app as app
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text


# Lazy init to support testing.
data_loch_db = None
data_loch_db_rds = None


def safe_execute_redshift(string, **kwargs):
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


def advising_notes_schema():
    return app.config['DATA_LOCH_ADVISING_NOTES_SCHEMA']


def asc_advising_notes_schema():
    return app.config['DATA_LOCH_ASC_ADVISING_NOTES_SCHEMA']


def asc_schema():
    return app.config['DATA_LOCH_ASC_SCHEMA']


def boac_schema():
    return app.config['DATA_LOCH_BOAC_SCHEMA']


def coe_schema():
    return app.config['DATA_LOCH_COE_SCHEMA']


def intermediate_schema():
    return app.config['DATA_LOCH_INTERMEDIATE_SCHEMA']


def l_s_schema():
    return app.config['DATA_LOCH_L_S_SCHEMA']


def physics_schema():
    return app.config['DATA_LOCH_PHYSICS_SCHEMA']


def sis_schema():
    return app.config['DATA_LOCH_SIS_SCHEMA']


def student_schema():
    return app.config['DATA_LOCH_STUDENT_SCHEMA']


def earliest_term_id():
    return sis_term_id_for_name(app.config['LEGACY_EARLIEST_TERM'])


def get_regular_undergraduate_session(term_id):
    sql = f"""SELECT * FROM {sis_schema()}.sis_terms
              WHERE term_id = '{term_id}'
              AND academic_career = 'UGRD'
              AND session_id = '1'
           """
    return safe_execute_rds(sql)


def get_enrolled_primary_sections(term_id, course_name):
    sql = f"""SELECT * FROM {sis_schema()}.enrolled_primary_sections
              WHERE term_id = :term_id
              AND sis_course_name_compressed LIKE :course_name
              ORDER BY sis_course_name_compressed, sis_instruction_format, sis_section_num
           """
    return safe_execute_rds(sql, term_id=term_id, course_name=f'{course_name}%')


def get_enrolled_primary_sections_for_parsed_code(term_id, subject_area, catalog_id):
    params = {
        'term_id': term_id,
        'catalog_id': f'{catalog_id}%',
    }
    if subject_area:
        subject_area_clause = 'AND sis_subject_area_compressed LIKE :subject_area'
        params.update({'subject_area': f'{subject_area}%'})
    else:
        subject_area_clause = ''
    sql = f"""SELECT * FROM {sis_schema()}.enrolled_primary_sections
              WHERE term_id = :term_id
              {subject_area_clause}
              AND sis_catalog_id LIKE :catalog_id
              ORDER BY sis_course_name_compressed, sis_instruction_format, sis_section_num
           """
    return safe_execute_rds(sql, **params)


@fixture('loch_sis_enrollments_{uid}_{term_id}.csv')
def get_sis_enrollments(uid, term_id):
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
    return safe_execute_redshift(sql)


def get_sis_holds(sid):
    sql = f"""SELECT feed
        FROM {student_schema()}.student_holds
        WHERE sid = '{sid}'
        """
    return safe_execute_redshift(sql)


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
    return safe_execute_redshift(sql)


def get_sis_section_enrollment_for_uid(term_id, sis_section_id, uid):
    sql = f"""SELECT DISTINCT sas.sid
              FROM {student_schema()}.student_academic_status sas
              JOIN {intermediate_schema()}.sis_enrollments enr
                ON sas.uid = enr.ldap_uid
                AND enr.ldap_uid = :uid
                AND enr.sis_term_id = :term_id
                AND enr.sis_section_id = :sis_section_id"""
    params = {'term_id': term_id, 'sis_section_id': sis_section_id, 'uid': uid}
    return safe_execute_redshift(sql, **params)


@fixture('loch_sis_section_enrollments_{term_id}_{sis_section_id}.csv')
def get_sis_section_enrollments(term_id, sis_section_id, offset=None, limit=None):
    sql = f"""SELECT DISTINCT sas.sid, sas.uid, sas.first_name, sas.last_name
              FROM {student_schema()}.student_academic_status sas
              JOIN {intermediate_schema()}.sis_enrollments enr
                ON sas.uid = enr.ldap_uid
                AND enr.sis_term_id = :term_id
                AND enr.sis_section_id = :sis_section_id
              ORDER BY {naturalize_order('sas.last_name')}, {naturalize_order('sas.first_name')}, sas.sid"""
    params = {'term_id': term_id, 'sis_section_id': sis_section_id}
    if offset:
        sql += ' OFFSET :offset'
        params['offset'] = offset
    if limit:
        sql += ' LIMIT :limit'
        params['limit'] = limit
    return safe_execute_redshift(sql, **params)


def get_sis_section_enrollments_count(term_id, sis_section_id):
    sql = f"""SELECT COUNT(DISTINCT sas.sid) as count
              FROM {student_schema()}.student_academic_status sas
              JOIN {intermediate_schema()}.sis_enrollments enr
                ON sas.uid = enr.ldap_uid
                AND enr.sis_term_id = :term_id
                AND enr.sis_section_id = :sis_section_id
        """
    params = {'term_id': term_id, 'sis_section_id': sis_section_id}
    return safe_execute_redshift(sql, **params)


def get_sis_section_mean_gpas(term_id, sis_section_id):
    params = {'term_id': term_id, 'sis_section_id': sis_section_id}
    sql = f"""SELECT gpa_term_id, avg_gpa
          FROM {boac_schema()}.section_mean_gpas
          WHERE sis_term_id = :term_id
          AND sis_section_id = :sis_section_id
    """
    return safe_execute_redshift(sql, **params)


def get_team_groups(group_codes=None, team_code=None):
    params = {}
    sql = f"""SELECT group_code, group_name, team_code, team_name, COUNT(DISTINCT sid)
        FROM {asc_schema()}.students
        WHERE team_code IS NOT NULL"""
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
    return safe_execute_rds(sql, sids=sids)


def get_coe_profiles(sids):
    sql = f"""SELECT sid, profile
        FROM {coe_schema()}.student_profiles
        WHERE sid = ANY(:sids)
        """
    return safe_execute_rds(sql, sids=sids)


def get_student_by_sid(sid):
    sql = f"""SELECT sas.*
        FROM {student_schema()}.student_academic_status sas
        WHERE sas.sid = :sid"""
    rows = safe_execute_rds(sql, sid=sid)
    return None if not rows or (len(rows) == 0) else rows[0]


def get_student_by_uid(uid):
    sql = f"""SELECT sas.*
        FROM {student_schema()}.student_academic_status sas
        WHERE sas.uid = :uid"""
    rows = safe_execute_rds(sql, uid=uid)
    return None if not rows or (len(rows) == 0) else rows[0]


def get_basic_student_data(sids):
    sql = f"""SELECT sid, uid, first_name, last_name
        FROM {student_schema()}.student_academic_status
        WHERE sid = ANY(:sids)
        """
    return safe_execute_rds(sql, sids=sids)


def get_student_profiles(sids=None):
    sql = f"""SELECT sid, profile
        FROM {student_schema()}.student_profiles
        """
    if sids is not None:
        sql += 'WHERE sid = ANY(:sids)'
        return safe_execute_rds(sql, sids=sids)
    else:
        return safe_execute_rds(sql)


def extract_valid_sids(sids):
    sql = f'SELECT sid FROM {student_schema()}.student_profiles WHERE sid = ANY(:sids)'
    return safe_execute_rds(sql, sids=sids)


def get_term_gpas(sids):
    sql = f"""SELECT sid, term_id, gpa, units_taken_for_gpa
        FROM {student_schema()}.student_term_gpas
        WHERE sid = ANY(:sids)
        AND units_taken_for_gpa > 0
        ORDER BY sid, term_id DESC"""
    return safe_execute_rds(sql, sids=sids)


def get_enrollments_for_sid(sid, latest_term_id=None):
    sql = f"""SELECT term_id, enrollment_term
        FROM {student_schema()}.student_enrollment_terms
        WHERE sid = :sid
        AND term_id >= '{earliest_term_id()}'"""
    if latest_term_id:
        sql += f""" AND term_id <= '{latest_term_id}'"""
    sql += ' ORDER BY term_id DESC'
    return safe_execute_rds(sql, sid=sid)


def get_enrollments_for_term(term_id, sids=None):
    sql = f"""SELECT sid, enrollment_term
        FROM {student_schema()}.student_enrollment_terms
        WHERE term_id = :term_id"""
    if sids is not None:
        sql += ' AND sid = ANY(:sids)'
    return safe_execute_rds(sql, term_id=term_id, sids=sids)


def match_advising_note_authors_by_name(prefixes, limit=None):
    prefix_conditions = []
    prefix_kwargs = {}
    for idx, prefix in enumerate(prefixes):
        prefix_conditions.append(
            f"""JOIN {advising_notes_schema()}.advising_note_author_names an{idx}
            ON an{idx}.name LIKE :prefix_{idx}
            AND an{idx}.uid = a.uid""",
        )
        prefix_kwargs[f'prefix_{idx}'] = f'{prefix}%'
    sql = f"""SELECT DISTINCT a.first_name, a.last_name, a.sid, a.uid
        FROM {advising_notes_schema()}.advising_note_authors a
        {' '.join(prefix_conditions)}
        ORDER BY a.first_name, a.last_name"""
    if limit:
        sql += f' LIMIT {limit}'
    return safe_execute_rds(sql, **prefix_kwargs)


def match_students_by_name_or_sid(prefixes, limit=None):
    prefix_conditions = []
    prefix_kwargs = {}
    for idx, prefix in enumerate(prefixes):
        prefix_conditions.append(
            f"""JOIN {student_schema()}.student_names sn{idx}
            ON (sn{idx}.name LIKE :prefix_{idx} OR sn{idx}.sid LIKE :prefix_{idx})
            AND sn{idx}.sid = sas.sid""",
        )
        prefix_kwargs[f'prefix_{idx}'] = f'{prefix}%'
    sql = f"""SELECT DISTINCT sas.first_name, sas.last_name, sas.sid, sas.uid
        FROM {student_schema()}.student_academic_status sas
        {' '.join(prefix_conditions)}
        ORDER BY sas.first_name, sas.last_name"""
    if limit:
        sql += f' LIMIT {limit}'
    return safe_execute_rds(sql, **prefix_kwargs)


def get_asc_advising_notes(sid):
    sql = f"""
        SELECT
            id, sid, advisor_uid AS author_uid,
            advisor_first_name || ' ' || advisor_last_name AS author_name,
            created_at, updated_at
        FROM {asc_advising_notes_schema()}.advising_notes
        WHERE sid=:sid
        ORDER BY created_at, updated_at, id"""
    return safe_execute_redshift(sql, sid=sid)


def get_asc_advising_note_topics(sid):
    sql = f"""SELECT id, topic
        FROM {asc_advising_notes_schema()}.advising_note_topics
        WHERE sid=:sid"""
    return safe_execute_redshift(sql, sid=sid)


def get_sis_advising_notes(sid):
    sql = f"""
        SELECT
            id, sid, advisor_sid, appointment_id, note_category, note_subcategory,
            created_by, updated_by, note_body, created_at, updated_at
        FROM {advising_notes_schema()}.advising_notes
        WHERE sid=:sid
        ORDER BY created_at, updated_at, id"""
    return safe_execute_redshift(sql, sid=sid)


def get_sis_advising_note_topics(sid):
    sql = f"""SELECT advising_note_id, note_topic
        FROM {advising_notes_schema()}.advising_note_topics
        WHERE sid=:sid
        ORDER BY advising_note_id"""
    return safe_execute_redshift(sql, sid=sid)


def get_sis_advising_note_attachment(sid, filename):
    query_tables, query_filter, query_bindings = get_students_query()
    if not query_tables:
        return None
    sql = f"""SELECT advising_note_id, created_by, sis_file_name, user_file_name
        {query_tables}
        JOIN {advising_notes_schema()}.advising_note_attachments ana
        ON sas.sid = :sid
        AND ana.sid = sas.sid
        AND ana.sis_file_name = :filename
        {query_filter}"""
    return safe_execute_redshift(sql, sid=sid, filename=filename, **query_bindings)


def get_sis_advising_note_attachments(sid):
    sql = f"""SELECT advising_note_id, created_by, sis_file_name, user_file_name
        FROM {advising_notes_schema()}.advising_note_attachments
        WHERE sid=:sid
        ORDER BY advising_note_id"""
    return safe_execute_redshift(sql, sid=sid)


def search_advising_notes(
    search_phrase,
    author_uid=None,
    author_csid=None,
    student_csid=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    offset=None,
    limit=None,
):
    if author_csid and author_uid:
        author_filter = 'AND (an.advisor_sid = :author_csid OR an.advisor_uid = :author_uid)'
    elif author_csid:
        author_filter = 'AND an.advisor_sid = :author_csid'
    else:
        author_filter = ''

    sid_filter = 'AND an.sid = :student_csid' if student_csid else ''

    if topic:
        topic_join = f"""JOIN {advising_notes_schema()}.advising_note_topic_mappings antm
            ON antm.boa_topic = :topic
        JOIN {advising_notes_schema()}.advising_note_topics ant
            ON ant.note_topic = antm.sis_topic
            AND ant.advising_note_id = an.id"""
    else:
        topic_join = ''

    date_filter = ''
    # We prefer to filter on updated_at, but that value is not meaningful for UCBCONVERSION notes.
    if datetime_from:
        date_filter += """ AND ((an.created_by = 'UCBCONVERSION' AND an.created_at >= :datetime_from)
            OR ((an.created_by != 'UCBCONVERSION' OR an.created_by IS NULL) AND an.updated_at >= :datetime_from))"""
    if datetime_to:
        date_filter += """ AND ((an.created_by = 'UCBCONVERSION' AND an.created_at < :datetime_to)
            OR ((an.created_by != 'UCBCONVERSION' OR an.created_by IS NULL) AND an.updated_at < :datetime_to))"""

    sql = f"""WITH an AS (
        (SELECT sis.sid, sis.id, sis.note_body, sis.advisor_sid, NULL AS advisor_uid, NULL AS advisor_first_name, NULL AS advisor_last_name,
                sis.note_category, sis.note_subcategory, sis.created_by, sis.created_at, sis.updated_at, idx.rank
            FROM {advising_notes_schema()}.advising_notes sis
            JOIN (
                SELECT id, ts_rank(fts_index, plainto_tsquery('english', :search_phrase)) AS rank
                FROM {advising_notes_schema()}.advising_notes_search_index
                WHERE fts_index @@ plainto_tsquery('english', :search_phrase)
            ) AS idx
            ON idx.id = sis.id)
        UNION
        (SELECT ascn.sid, ascn.id, NULL AS note_body, NULL AS advisor_sid, ascn.advisor_uid, ascn.advisor_first_name, ascn.advisor_last_name,
                NULL AS note_category, NULL AS note_subcategory, NULL AS created_by, ascn.created_at, ascn.updated_at, idx.rank
            FROM {asc_schema()}.advising_notes ascn
            JOIN (
                SELECT id, ts_rank(fts_index, plainto_tsquery('english', :search_phrase)) AS rank
                FROM {asc_schema()}.advising_notes_search_index
                WHERE fts_index @@ plainto_tsquery('english', :search_phrase)
            ) AS idx
            ON idx.id = ascn.id)
        )
        SELECT DISTINCT
            an.sid, an.id, an.note_body, an.advisor_sid, an.advisor_uid,
            an.created_by, an.created_at, an.updated_at, an.note_category, an.note_subcategory,
            sas.uid, sas.first_name, sas.last_name, an.advisor_first_name, an.advisor_last_name, an.rank
        FROM {student_schema()}.student_academic_status sas
        JOIN an
            ON an.sid = sas.sid
            {author_filter}
            {date_filter}
            {sid_filter}
        {topic_join}
        ORDER BY an.rank DESC, an.id"""
    if offset is not None and offset > 0:
        sql += ' OFFSET :offset'
    if limit is not None and limit < 150:  # Sanity check large limits
        sql += ' LIMIT :limit'
    params = dict(
        search_phrase=search_phrase,
        author_csid=author_csid,
        author_uid=author_uid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=offset,
        limit=limit,
    )
    return safe_execute_rds(sql, **params)


def get_ethnicity_codes(scope=()):
    # TODO Scoping remains in place for the moment, as ethnicity is still a COE-specific category.
    query_tables = _student_query_tables_for_scope(scope)
    if not query_tables:
        return []
    # TODO 'Z' is an international visa status rather than an ethnicity, and should be suppressed for now.
    # BOAC will handle international status separately from ethnicity after switching to campus-wide demographic
    # data.
    return safe_execute_rds(f"""SELECT DISTINCT s.ethnicity AS ethnicity_code
        {query_tables}
        WHERE s.ethnicity IS NOT NULL AND s.ethnicity != '' AND s.ethnicity != 'Z'
        ORDER BY ethnicity_code
        """)


def get_expected_graduation_terms():
    sql = f"""SELECT DISTINCT expected_grad_term FROM {student_schema()}.student_academic_status
        ORDER BY expected_grad_term"""
    return safe_execute_rds(sql)


def get_majors():
    sql = f"""SELECT DISTINCT maj.major AS major
        FROM {student_schema()}.student_academic_status sas
        JOIN {student_schema()}.student_majors maj ON maj.sid = sas.sid
        ORDER BY major"""
    return safe_execute_rds(sql)


def get_students_query(     # noqa
    advisor_ldap_uids=None,
    coe_prep_statuses=None,
    coe_probation=None,
    ethnicities=None,
    expected_grad_terms=None,
    genders=None,
    gpa_ranges=None,
    group_codes=None,
    in_intensive_cohort=None,
    is_active_asc=None,
    is_active_coe=None,
    last_name_range=None,
    levels=None,
    majors=None,
    scope=(),
    search_phrase=None,
    sids=(),
    transfer=None,
    underrepresented=None,
    unit_ranges=None,
):

    # If no specific scope is required by criteria, default to the admin view.
    if not scope:
        scope = ['ADMIN']
    query_tables = _student_query_tables_for_scope(scope)
    if not query_tables:
        return None, None, None

    query_filter = ' WHERE true'
    query_bindings = {}

    # Name or SID search
    if search_phrase:
        words = search_phrase.upper().split()
        # A numeric string indicates an SID search.
        if len(words) == 1 and re.match(r'^\d+$', words[0]):
            query_filter += ' AND (sas.sid LIKE :sid_phrase)'
            query_bindings.update({'sid_phrase': f'{words[0]}%'})
        # Other strings indicate a name search.
        else:
            for i, word in enumerate(words):
                query_tables += f"""
                    JOIN {student_schema()}.student_names n{i}
                        ON n{i}.name LIKE :name_phrase_{i}
                        AND n{i}.sid = sas.sid"""
                word = ''.join(re.split('\W', word))
                query_bindings.update({f'name_phrase_{i}': f'{word}%'})
    if sids:
        query_filter += f' AND sas.sid = ANY(:sids)'
        query_bindings.update({'sids': sids})

    # Generic SIS criteria
    query_filter += _numranges_to_sql('sas.gpa', gpa_ranges) if gpa_ranges else ''
    query_filter += _numranges_to_sql('sas.units', unit_ranges) if unit_ranges else ''
    query_filter += _query_filter_last_name_range(last_name_range)
    if expected_grad_terms:
        query_filter += ' AND sas.expected_grad_term = ANY(:expected_grad_terms)'
        query_bindings.update({'expected_grad_terms': expected_grad_terms})
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
    if transfer is True:
        query_filter += ' AND sas.transfer = TRUE'

    # ASC criteria
    query_filter += f' AND s.active IS {is_active_asc}' if is_active_asc is not None else ''
    query_filter += f' AND s.intensive IS {in_intensive_cohort}' if in_intensive_cohort is not None else ''
    if group_codes:
        query_filter += ' AND s.group_code = ANY(:group_codes)'
        query_bindings.update({'group_codes': group_codes})

    # COE criteria
    if advisor_ldap_uids:
        query_filter += ' AND s.advisor_ldap_uid = ANY(:advisor_ldap_uids)'
        query_bindings.update({'advisor_ldap_uids': advisor_ldap_uids})
    if coe_prep_statuses:
        query_filter += ' AND (' + ' OR '.join([f's.{cps} IS TRUE' for cps in coe_prep_statuses]) + ')'
    if ethnicities:
        query_filter += ' AND s.ethnicity = ANY(:ethnicities)'
        query_bindings.update({'ethnicities': ethnicities})
    if genders:
        query_filter += ' AND s.gender = ANY(:genders)'
        query_bindings.update({'genders': genders})
    query_filter += f' AND s.probation IS {coe_probation}' if coe_probation is not None else ''
    query_filter += f' AND s.minority IS {underrepresented}' if underrepresented is not None else ''
    if is_active_coe is False:
        query_filter += f" AND s.status IN ('D','P','U','W','X','Z')"
    elif is_active_coe is True:
        query_filter += f" AND s.status NOT IN ('D','P','U','W','X','Z')"

    return query_tables, query_filter, query_bindings


def get_students_ordering(order_by=None, group_codes=None, majors=None, scope=None):
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
        # Sorting by athletic team introduces a couple of onerous special cases where we
        # have to do an extra join on the athletics table.
        # 1) If team name is both a filter criterion and a sort criterion, the athletics join specified in the
        # get_students_query join will include only those group names that are in filter criteria. But if any
        # students are in multiple team groups, ordering may depend on group names not present in filter criteria,
        # so we have to join the athletics rows a second time.
        # 2) If team group name has been specified as an ordering criterion but is not yet present as a join table
        # (for instance, because the current user is an admin), we have to explicitly bring it in.
        # Why not do this complex sorting after the query? Because correctly calculating
        # pagination offsets requires filtering and ordering to be done at the SQL level.
        if group_codes or (scope and asc_schema() not in _student_query_tables_for_scope(scope)):
            supplemental_query_tables = f' LEFT JOIN {asc_schema()}.students asc_students ON asc_students.sid = sas.sid'
            o = naturalize_order('asc_students.group_name')
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
        include_null = False
        if numrange_match[1] != 'NULL':
            lower_bound_condition = '>'
            # Square brackets in numrange syntax indicate an inclusive range.
            if numrange_match[3] == '[':
                lower_bound_condition += '='
            bounds.append(f'{column} {lower_bound_condition} {numrange_match[1]}')
        else:
            # An inclusive lower bound of NULL is interpreted as including null values.
            include_null = (numrange_match[3] == '[')
        if numrange_match[2] != 'NULL':
            upper_bound_condition = '<'
            if numrange_match[4] == ']':
                upper_bound_condition += '='
            bounds.append(f'{column} {upper_bound_condition} {numrange_match[2]}')
        sql_clause = f"({' AND '.join(bounds)})"
        if include_null:
            sql_clause = f'({column} IS NULL OR {sql_clause})'
        return sql_clause


def _numranges_to_sql(column, numranges):
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
            'PHYSI': physics_schema(),
            'QCADV': l_s_schema(),
        }
        tables = []
        # A dictionary with key 'intersection' indicates that multiple scopes should be treated as an intersection
        # rather than a union.
        if 'intersection' in scope:
            scope = scope['intersection']
            join_type = 'intersection'
        else:
            join_type = 'union'

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
        elif join_type == 'union':
            # In a union of multiple schemas, SID will be the only common element.
            table_sql = f"""FROM ({' UNION '.join(['SELECT sid FROM ' + t for t in tables])}) s
                JOIN {student_schema()}.student_academic_status sas ON sas.sid = s.sid"""
        elif join_type == 'intersection':
            # In an intersection of multiple schemas, all queryable columns should be returned.
            columns_for_codes = {
                'COENG': [
                    'advisor_ldap_uid',
                    'did_prep',
                    'did_tprep',
                    'ethnicity',
                    'gender',
                    'minority',
                    'prep_eligible',
                    'probation',
                    'status',
                    'tprep_eligible',
                ],
                'QCADV': [
                    'acadplan_code',
                    'acadplan_descr',
                    'acadplan_type_code',
                    'acadplan_ownedby_code',
                ],
                'UWASC': [
                    'active',
                    'group_code',
                    'group_name',
                    'intensive',
                ],
            }
            intersection_columns = []
            for code in scope:
                intersection_columns += columns_for_codes[code]
            intersection_sql = f"SELECT {tables[0]}.sid, {', '.join(intersection_columns)} FROM {tables[0]}"
            for table in tables[1:]:
                intersection_sql += f' INNER JOIN {table} ON {table}.sid = {tables[0]}.sid'
            table_sql = f"""FROM ({intersection_sql}) s
                JOIN {student_schema()}.student_academic_status sas ON sas.sid = s.sid"""
    return table_sql


def _query_filter_last_name_range(range_):
    query_filter = ''
    if isinstance(range_, list) and len(range_):
        start = range_[0].upper()
        stop = range_[-1].upper()
        if start == stop:
            query_filter += f' AND sas.last_name ILIKE \'{start}%\''
        else:
            query_filter += f' AND UPPER(sas.last_name) >= \'{start}\''
            if stop < 'Z':
                # If 'stop' were 'Z' then upper bound would not be necessary
                query_filter += f' AND UPPER(sas.last_name) < \'{chr(ord(stop) + 1)}\''
    return query_filter
