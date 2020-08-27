"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac import db
from boac.lib.berkeley import previous_term_id, sis_term_id_for_name
from boac.lib.mockingdata import fixture
from boac.lib.util import join_if_present, tolerant_remove
from flask import current_app as app
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text


# Lazy init to support testing.
data_loch_db_rds = None


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


def advisor_schema():
    return app.config['DATA_LOCH_ADVISOR_SCHEMA']


def asc_schema():
    return app.config['DATA_LOCH_ASC_SCHEMA']


def boac_schema():
    return app.config['DATA_LOCH_BOAC_SCHEMA']


def coe_schema():
    return app.config['DATA_LOCH_COE_SCHEMA']


def data_science_advising_schema():
    return app.config['DATA_LOCH_DATA_SCIENCE_ADVISING_SCHEMA']


def e_i_schema():
    return app.config['DATA_LOCH_E_I_SCHEMA']


def oua_schema():
    return app.config['DATA_LOCH_OUA_SCHEMA']


def sis_advising_notes_schema():
    return app.config['DATA_LOCH_SIS_ADVISING_NOTES_SCHEMA']


def sis_schema():
    return app.config['DATA_LOCH_SIS_SCHEMA']


def sis_terms_schema():
    return app.config['DATA_LOCH_SIS_TERMS_SCHEMA']


def student_schema():
    return app.config['DATA_LOCH_STUDENT_SCHEMA']


def earliest_term_id():
    return sis_term_id_for_name(app.config['LEGACY_EARLIEST_TERM'])


def get_admit_colleges():
    return _get_admit_options_excluding_blanks('college')


def get_admit_ethnicities():
    return _get_admit_options_excluding_blanks('xethnic')


def get_admit_freshman_or_transfer():
    return _get_admit_options_excluding_blanks('freshman_or_transfer')


def get_admit_residency_categories():
    return _get_admit_options_excluding_blanks('residency_category')


def get_admit_special_program_cep():
    return _get_admit_options_excluding_blanks('special_program_cep')


def _get_admit_options_excluding_blanks(column):
    return safe_execute_rds(f"SELECT DISTINCT({column}) FROM {oua_schema()}.student_admits WHERE {column} IS NOT NULL AND {column} != ''")


def get_current_term_index():
    rows = safe_execute_rds(f'SELECT * FROM {sis_terms_schema()}.current_term_index')
    return None if not rows or (len(rows) == 0) else rows[0]


def get_undergraduate_term(term_id):
    sql = f"""SELECT * FROM {sis_terms_schema()}.term_definitions
              WHERE term_id = '{term_id}'
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


def get_sis_holds(sid):
    sql = f"""SELECT feed
        FROM {student_schema()}.student_holds
        WHERE sid = '{sid}'
        """
    return safe_execute_rds(sql)


@fixture('loch/sis_section_{term_id}_{sis_section_id}.csv')
def get_sis_section(term_id, sis_section_id):
    sql = f"""SELECT
                  sc.sis_term_id, sc.sis_section_id, sc.sis_course_title, sc.sis_course_name,
                  sc.is_primary, sc.sis_instruction_format, sc.instruction_mode, sc.sis_section_num,
                  sc.allowed_units, sc.instructor_uid, sc.instructor_name, sc.instructor_role_code,
                  sc.meeting_location, sc.meeting_days, sc.meeting_start_time, sc.meeting_end_time,
                  sc.meeting_start_date, sc.meeting_end_date
              FROM {sis_schema()}.sis_sections sc
              WHERE sc.sis_section_id = :sis_section_id
                  AND sc.sis_term_id = :term_id
              ORDER BY sc.meeting_days, sc.meeting_start_time, sc.meeting_end_time, sc.instructor_name
        """
    params = {
        'term_id': term_id,
        'sis_section_id': sis_section_id,
    }
    return safe_execute_rds(sql, **params)


def get_sis_section_enrollment_for_uid(term_id, sis_section_id, uid):
    sql = f"""SELECT DISTINCT sas.sid
              FROM {student_schema()}.student_academic_status sas
              JOIN {sis_schema()}.sis_enrollments enr
                ON sas.uid = enr.ldap_uid
                AND enr.ldap_uid = :uid
                AND enr.sis_term_id = :term_id
                AND enr.sis_section_id = :sis_section_id"""
    params = {'term_id': term_id, 'sis_section_id': sis_section_id, 'uid': uid}
    return safe_execute_rds(sql, **params)


@fixture('loch/sis_section_enrollments_{term_id}_{sis_section_id}.csv')
def get_sis_section_enrollments(term_id, sis_section_id, offset=None, limit=None):
    sql = f"""SELECT sas.sid, sas.uid, sas.first_name, sas.last_name
              FROM {student_schema()}.student_academic_status sas
              JOIN {sis_schema()}.sis_enrollments enr
                ON sas.uid = enr.ldap_uid
                AND enr.sis_term_id = :term_id
                AND enr.sis_section_id = :sis_section_id
              GROUP BY sas.sid, sas.uid, sas.first_name, sas.last_name
              ORDER BY {_naturalize_order('sas.last_name')}, {_naturalize_order('sas.first_name')}, sas.sid"""
    params = {'term_id': term_id, 'sis_section_id': sis_section_id}
    if offset:
        sql += ' OFFSET :offset'
        params['offset'] = offset
    if limit:
        sql += ' LIMIT :limit'
        params['limit'] = limit
    return safe_execute_rds(sql, **params)


def get_sis_section_enrollments_count(term_id, sis_section_id):
    sql = f"""SELECT COUNT(DISTINCT sas.sid) as count
              FROM {student_schema()}.student_academic_status sas
              JOIN {sis_schema()}.sis_enrollments enr
                ON sas.uid = enr.ldap_uid
                AND enr.sis_term_id = :term_id
                AND enr.sis_section_id = :sis_section_id
        """
    params = {'term_id': term_id, 'sis_section_id': sis_section_id}
    return safe_execute_rds(sql, **params)


def get_sis_section_mean_gpas(term_id, sis_section_id):
    params = {'term_id': term_id, 'sis_section_id': sis_section_id}
    sql = f"""SELECT gpa_term_id, avg_gpa
          FROM {boac_schema()}.section_mean_gpas
          WHERE sis_term_id = :term_id
          AND sis_section_id = :sis_section_id
    """
    return safe_execute_rds(sql, **params)


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
    sql = f"""SELECT p.sid, p.profile, d.gender, d.minority
        FROM {student_schema()}.student_profiles p
        LEFT JOIN {student_schema()}.demographics d ON d.sid = p.sid
        """
    if sids is not None:
        sql += 'WHERE p.sid = ANY(:sids)'
        return safe_execute_rds(sql, sids=sids)
    else:
        return safe_execute_rds(sql)


def query_historical_sids(sids):
    sql = f'SELECT sid FROM {student_schema()}.student_profiles_hist_enr WHERE sid = ANY(:sids) ORDER BY sid'
    return safe_execute_rds(sql, sids=sids)


def get_historical_student_profiles_for_sids(sids):
    sql = f"""SELECT sid, uid, profile
        FROM {student_schema()}.student_profiles_hist_enr
        WHERE sid = ANY(:sids)"""
    return safe_execute_rds(sql, sids=sids)


def get_historical_student_profiles_for_uid(uid):
    sql = f"""SELECT sid, uid, profile
        FROM {student_schema()}.student_profiles_hist_enr
        WHERE uid = :uid"""
    return safe_execute_rds(sql, uid=uid)


def get_historical_enrollments_for_sid(sid, latest_term_id=None):
    sql = f"""SELECT term_id, enrollment_term
        FROM {student_schema()}.student_enrollment_terms_hist_enr
        WHERE sid = :sid
        AND term_id >= '{earliest_term_id()}'"""
    if latest_term_id:
        sql += f" AND term_id <= '{latest_term_id}'"
    sql += 'ORDER BY term_id DESC'
    return safe_execute_rds(sql, sid=sid)


def get_historical_enrollments_for_term(term_id, sids):
    sql = f"""SELECT term_id, sid, enrollment_term
        FROM {student_schema()}.student_enrollment_terms_hist_enr
        WHERE term_id = :term_id
        AND sid = ANY(:sids)"""
    return safe_execute_rds(sql, term_id=term_id, sids=sids)


def extract_valid_sids(sids):
    sql = f'SELECT sid FROM {student_schema()}.student_profiles WHERE sid = ANY(:sids)'
    return safe_execute_rds(sql, sids=sids)


def get_academic_standing(sids):
    sql = f"""SELECT acad_standing_status as status, action_date, sid, term_id
        FROM {student_schema()}.academic_standing
        WHERE sid = ANY(:sids)
        ORDER BY sid, term_id DESC"""
    return safe_execute_rds(sql, sids=sids)


def get_academic_standing_terms(min_term_id=0):
    return safe_execute_rds(f"""SELECT DISTINCT term_id
        FROM {student_schema()}.academic_standing
        WHERE term_id >= '{min_term_id}'
        ORDER BY term_id DESC""")


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


def match_appointment_advisors_by_name(prefixes, limit=None):
    prefix_conditions = []
    prefix_kwargs = {}
    for prefix in prefixes:
        idx = prefixes.index(prefix)
        prefix_conditions.append(
            f"""JOIN {sis_advising_notes_schema()}.advising_appointment_advisor_names an{idx}
            ON an{idx}.name LIKE :prefix_{idx}
            AND an{idx}.uid = a.uid""",
        )
        prefix_kwargs[f'prefix_{idx}'] = f'{prefix}%'
    sql = f"""SELECT DISTINCT a.first_name, a.last_name, a.sid, a.uid
        FROM {sis_advising_notes_schema()}.advising_appointment_advisors a
        {' '.join(prefix_conditions)}
        ORDER BY a.first_name, a.last_name"""
    if limit:
        sql += f' LIMIT {limit}'
    return safe_execute_rds(sql, **prefix_kwargs)


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
    current_student_conditions = []
    non_current_student_conditions = []
    prefix_kwargs = {}
    for idx, prefix in enumerate(prefixes):
        current_student_conditions.append(
            f"""JOIN {student_schema()}.student_names sn{idx}
            ON (sn{idx}.name LIKE :prefix_{idx} OR sn{idx}.sid LIKE :prefix_{idx})
            AND sn{idx}.sid = sas.sid""",
        )
        if not prefix.isalpha():
            non_current_student_conditions.append(
                f"""JOIN {student_schema()}.student_name_index_hist_enr sn{idx}
                ON sn{idx}.sid LIKE :prefix_{idx}
                AND sn{idx}.sid = s.sid""",
            )
        prefix_kwargs[f'prefix_{idx}'] = f'{prefix}%'

    inner_sql = f"""SELECT sas.first_name, sas.last_name, sas.sid, sas.uid
        FROM {student_schema()}.student_academic_status sas
        {' '.join(current_student_conditions)}"""
    if len(non_current_student_conditions) > 0:
        inner_sql += f"""\nUNION
            SELECT s.first_name, s.last_name, s.sid, s.uid
            FROM {student_schema()}.student_names_hist_enr s
            {' '.join(non_current_student_conditions)}"""
    sql = f"""SELECT DISTINCT q.*
        FROM ({inner_sql}) q
        ORDER BY q.first_name, q.last_name"""
    if limit:
        sql += f' LIMIT {limit}'
    return safe_execute_rds(sql, **prefix_kwargs)


def get_asc_advising_notes(sid):
    sql = f"""
        SELECT
            id, sid, advisor_uid AS author_uid,
            advisor_first_name || ' ' || advisor_last_name AS author_name,
            created_at, updated_at
        FROM {asc_schema()}.advising_notes
        WHERE sid=:sid
        ORDER BY created_at, updated_at, id"""
    return safe_execute_rds(sql, sid=sid)


def get_asc_advising_note_count():
    return safe_execute_rds(f'SELECT COUNT(id) FROM {asc_schema()}.advising_notes')[0]['count']


def get_asc_advising_note_topics(sid):
    sql = f"""SELECT id, topic
        FROM {asc_schema()}.advising_note_topics
        WHERE sid=:sid
        ORDER BY id"""
    return safe_execute_rds(sql, sid=sid)


def get_data_science_advising_notes(sid):
    sql = f"""
        SELECT
            n.id, n.sid, n.advisor_sid AS author_sid, n.advisor_uid AS author_uid,
            n.advisor_first_name || ' ' || n.advisor_last_name AS author_name, dsn.advisor_email,
            dsn.reason_for_appointment, n.note_body, n.created_at
        FROM {data_science_advising_schema()}.advising_notes dsn
        JOIN {advising_notes_schema()}.advising_notes n ON dsn.id = n.id
        WHERE n.sid=:sid
        ORDER BY n.created_at, n.id"""
    return safe_execute_rds(sql, sid=sid)


def get_e_i_advising_notes(sid):
    sql = f"""
        SELECT
            id, sid, advisor_uid AS author_uid,
            advisor_first_name || ' ' || advisor_last_name AS author_name,
            created_at, updated_at
        FROM {e_i_schema()}.advising_notes
        WHERE sid=:sid
        AND advisor_last_name <> 'Front Desk'
        ORDER BY created_at, updated_at, id"""
    return safe_execute_rds(sql, sid=sid)


def get_e_and_i_advising_note_count():
    sql = f"""
        SELECT COUNT(id)
        FROM {e_i_schema()}.advising_notes
        WHERE advisor_last_name <> 'Front Desk'"""
    return safe_execute_rds(sql)[0]['count']


def get_e_i_advising_note_topics(sid):
    sql = f"""SELECT id, topic
        FROM {e_i_schema()}.advising_note_topics
        WHERE sid=:sid
        ORDER BY id"""
    return safe_execute_rds(sql, sid=sid)


def get_admitted_student_by_sid(sid):
    rows = get_admitted_students_by_sids([sid])
    return None if not rows or (len(rows) == 0) else rows[0]


def get_admitted_students_by_sids(sids):
    sql = f"""
        SELECT a.applyuc_cpid, a.cs_empl_id AS sid, a.uid, s.uid AS student_uid,
        a.residency_category, a.freshman_or_transfer, a.admit_term, a.admit_status, a.current_sir, college, a.first_name, a.middle_name,
        a.last_name, a.birthdate, a.daytime_phone, a.mobile, a.email, a.campus_email_1, a.permanent_street_1, permanent_street_2,
        a.permanent_city, a.permanent_region, a.permanent_postal, a.permanent_country, sex, a.gender_identity, a.xethnic, a.hispanic,
        a.urem, a.first_generation_college, a.parent_1_education_level, parent_2_education_level,
        a.highest_parent_education_level, a.hs_unweighted_gpa, a.hs_weighted_gpa, a.transfer_gpa, a.act_composite, a.act_math, a.act_english,
        a.act_reading, a.act_writing, a.sat_total, a.sat_r_evidence_based_rw_section, a.sat_r_math_section, a.sat_r_essay_reading,
        a.sat_r_essay_analysis, a.sat_r_essay_writing, a.application_fee_waiver_flag, a.foster_care_flag, a.family_is_single_parent,
        a.student_is_single_parent, a.family_dependents_num, a.student_dependents_num, a.family_income, a.student_income,
        a.is_military_dependent, a.military_status, a.reentry_status, a.athlete_status, a.summer_bridge_status, a.last_school_lcff_plus_flag,
        a.special_program_cep, a.us_citizenship_status, a.us_non_citizen_status, a.citizenship_country, a.permanent_residence_country,
        a.non_immigrant_visa_current, a.non_immigrant_visa_planned, a.updated_at
        FROM {oua_schema()}.student_admits a
        LEFT JOIN {student_schema()}.student_academic_status s ON a.cs_empl_id = s.sid
        WHERE a.cs_empl_id = ANY(:sids)"""
    return safe_execute_rds(sql, sids=sids)


def get_sis_advising_notes(sid):
    sql = f"""
        SELECT
            id, sid, advisor_sid, appointment_id, note_category, note_subcategory,
            created_by, updated_by, note_body, created_at, updated_at
        FROM {sis_advising_notes_schema()}.advising_notes
        WHERE sid=:sid
        ORDER BY created_at, updated_at, id"""
    return safe_execute_rds(sql, sid=sid)


def get_sis_advising_note_count():
    return safe_execute_rds(f'SELECT COUNT(id) FROM {sis_advising_notes_schema()}.advising_notes')[0]['count']


def get_sis_advising_topics(ids):
    sql = f"""SELECT advising_note_id, note_topic
        FROM {sis_advising_notes_schema()}.advising_note_topics
        WHERE advising_note_id=ANY(:ids)
        AND note_topic IS NOT NULL
        ORDER BY advising_note_id"""
    return safe_execute_rds(sql, ids=ids)


def get_sis_advising_note_attachment(sid, filename):
    sql = f"""SELECT advising_note_id, created_by, sis_file_name, user_file_name, is_historical
        FROM {sis_advising_notes_schema()}.advising_note_attachments
        WHERE sid = :sid
        AND sis_file_name = :filename"""
    return safe_execute_rds(sql, sid=sid, filename=filename)


def get_sis_advising_attachments(ids):
    # Priority is given to is_historical=FALSE.
    sql = f"""SELECT advising_note_id, created_by, sis_file_name, user_file_name, MIN(is_historical::int)
        FROM {sis_advising_notes_schema()}.advising_note_attachments
        WHERE advising_note_id=ANY(:ids)
        GROUP BY advising_note_id, created_by, sis_file_name, user_file_name
        ORDER BY advising_note_id"""
    return safe_execute_rds(sql, ids=ids)


def get_sis_advising_appointments(sid):
    sql = f"""
        SELECT
            a.id, a.sid AS student_sid, a.advisor_sid, aa.uid as advisor_uid, aa.first_name AS advisor_first_name,
            aa.last_name AS advisor_last_name, a.appointment_id, a.created_by, a.updated_by,
            a.note_body AS details, a.created_at, a.updated_at
        FROM {sis_advising_notes_schema()}.advising_appointments a
        LEFT JOIN {sis_advising_notes_schema()}.advising_appointment_advisors aa ON a.advisor_sid = aa.sid
        WHERE a.sid=:sid
        ORDER BY created_at, updated_at, id"""
    return safe_execute_rds(sql, sid=sid)


def search_advising_appointments(
    search_phrase,
    advisor_uid=None,
    advisor_csid=None,
    student_csid=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    offset=None,
    limit=None,
):
    query_columns = """an.sid, an.id, an.note_body, an.advisor_sid, aa.uid AS advisor_uid,
            an.created_by, an.created_at, an.updated_at, an.note_category, an.note_subcategory,
            spi.uid, spi.first_name, spi.last_name, aa.first_name AS advisor_first_name, aa.last_name AS advisor_last_name"""
    query_tables = f"""{sis_advising_notes_schema()}.advising_appointments an
        LEFT JOIN {sis_advising_notes_schema()}.advising_appointment_advisors aa ON an.advisor_sid = aa.sid
        JOIN {student_schema()}.student_profile_index spi ON an.sid = spi.sid"""
    if search_phrase:
        query_tables += f"""
            JOIN {sis_advising_notes_schema()}.advising_appointments_search_index idx
            ON idx.id = an.id
            AND idx.fts_index @@ plainto_tsquery('english', :search_phrase)"""
    uid_advisor_filter = 'aa.uid = :advisor_uid' if advisor_uid else None
    return search_sis_advising(
        query_columns=query_columns,
        query_tables=query_tables,
        uid_advisor_filter=uid_advisor_filter,
        search_phrase=search_phrase,
        advisor_uid=advisor_uid,
        advisor_csid=advisor_csid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=offset,
        limit=limit,
    )


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
    query_columns = """an.sid, an.id, an.note_body, an.advisor_sid, an.advisor_uid,
            an.created_by, an.created_at, an.updated_at, an.note_category, an.note_subcategory,
            spi.uid, spi.first_name, spi.last_name, an.advisor_first_name, an.advisor_last_name"""
    query_tables = f"""{advising_notes_schema()}.advising_notes an
        JOIN {student_schema()}.student_profile_index spi ON an.sid = spi.sid"""
    if search_phrase:
        query_tables += f"""
            JOIN {advising_notes_schema()}.advising_notes_search_index idx
            ON idx.id = an.id
            AND idx.fts_index @@ plainto_tsquery('english', :search_phrase)"""
    uid_advisor_filter = 'an.advisor_uid = :advisor_uid' if author_uid else None
    return search_sis_advising(
        query_columns=query_columns,
        query_tables=query_tables,
        uid_advisor_filter=uid_advisor_filter,
        search_phrase=search_phrase,
        advisor_uid=author_uid,
        advisor_csid=author_csid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=offset,
        limit=limit,
    )


def search_sis_advising(
    query_columns,
    query_tables,
    uid_advisor_filter,
    search_phrase,
    advisor_uid=None,
    advisor_csid=None,
    student_csid=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    offset=None,
    limit=None,
):

    if advisor_uid or advisor_csid:
        sid_advisor_filter = 'an.advisor_sid = :advisor_csid' if advisor_csid else None
        advisor_filter = 'AND (' + join_if_present(' OR ', [uid_advisor_filter, sid_advisor_filter]) + ')'
    else:
        advisor_filter = ''

    sid_filter = 'AND an.sid = :student_csid' if student_csid else ''

    if topic:
        topic_join = f"""JOIN {sis_advising_notes_schema()}.advising_note_topic_mappings antm
            ON antm.boa_topic = :topic
        JOIN {sis_advising_notes_schema()}.advising_note_topics ant
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

    if search_phrase:
        query_columns += ", ts_rank(idx.fts_index, plainto_tsquery('english', :search_phrase)) AS rank"
    else:
        query_columns += ', 0 AS rank'

    sql = f"""SELECT DISTINCT {query_columns} FROM {query_tables}
        {topic_join}
        WHERE TRUE
        {advisor_filter}
        {sid_filter}
        {date_filter}
        ORDER BY rank DESC, an.id"""

    if offset is not None and offset > 0:
        sql += ' OFFSET :offset'
    if limit is not None and limit < 150:  # Sanity check large limits
        sql += ' LIMIT :limit'
    params = dict(
        search_phrase=search_phrase,
        advisor_csid=advisor_csid,
        advisor_uid=advisor_uid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=offset,
        limit=limit,
    )
    return safe_execute_rds(sql, **params)


def get_academic_plans_for_advisor(advisor_sid):
    sql = f"""SELECT DISTINCT advs.academic_plan_code, advs.academic_plan
        FROM {advisor_schema()}.advisor_students advs
        JOIN {student_schema()}.student_academic_status sas
        ON sas.sid = advs.student_sid
        AND advs.advisor_sid = :advisor_sid"""
    return safe_execute_rds(sql, advisor_sid=advisor_sid)


def get_advisor_uids_for_affiliations(program, affiliations):
    sql = f"""SELECT DISTINCT uid,
        CASE WHEN cs_permissions = 'UC_CS_AA_ADVISOR_VIEW' THEN false ELSE true END AS can_access_advising_data,
        CASE
            WHEN advisor_type_code IS NULL OR cs_permissions = 'UC_CS_AA_ADVISOR_VIEW' THEN false
            ELSE true END
        AS can_access_canvas_data
        FROM {advisor_schema()}.advisor_roles"""
    if program:
        sql += ' WHERE academic_program_code = :program'
    else:
        sql += " WHERE academic_program_code = '' OR academic_program_code IS NULL"
    if affiliations:
        sql += ' AND advisor_type_code = ANY(:affiliations)'
    return safe_execute_rds(sql, program=program, affiliations=affiliations)


def get_coe_ethnicity_codes(scope=()):
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


def get_colleges():
    sql = f"""SELECT DISTINCT maj.college
        FROM {student_schema()}.student_academic_status sas
        JOIN {student_schema()}.student_majors maj ON maj.sid = sas.sid
        WHERE maj.college NOT LIKE 'Graduate%'
        ORDER BY college"""
    return safe_execute_rds(sql)


def get_distinct_genders():
    return safe_execute_rds(f'SELECT DISTINCT gender FROM {student_schema()}.demographics ORDER BY gender')


def get_distinct_ethnicities():
    return safe_execute_rds(f'SELECT DISTINCT ethnicity FROM {student_schema()}.ethnicities ORDER BY ethnicity')


def get_entering_terms():
    sql = f"""SELECT DISTINCT entering_term FROM {student_schema()}.student_academic_status
        WHERE entering_term > '0'
        ORDER BY entering_term DESC"""
    return safe_execute_rds(sql)


def get_expected_graduation_terms():
    sql = f"""SELECT DISTINCT expected_grad_term FROM {student_schema()}.student_academic_status
        WHERE expected_grad_term > '0'
        ORDER BY expected_grad_term DESC"""
    return safe_execute_rds(sql)


def get_intended_majors():
    sql = f"""SELECT DISTINCT im.major
        FROM {student_schema()}.student_academic_status sas
        JOIN {student_schema()}.intended_majors im ON im.sid = sas.sid
        ORDER BY major"""
    return safe_execute_rds(sql)


def get_majors():
    sql = f"""SELECT DISTINCT maj.major AS major
        FROM {student_schema()}.student_academic_status sas
        JOIN {student_schema()}.student_majors maj ON maj.sid = sas.sid
        ORDER BY major"""
    return safe_execute_rds(sql)


def get_minors():
    sql = f"""SELECT DISTINCT min.minor AS minor
        FROM {student_schema()}.student_academic_status sas
        JOIN {student_schema()}.minors min ON min.sid = sas.sid
        ORDER BY minor"""
    return safe_execute_rds(sql)


def get_other_visa_types():
    sql = f"""SELECT DISTINCT visa_type FROM {student_schema()}.visas
        WHERE visa_status = 'G' and visa_type NOT IN ('F1','J1','PR')"""
    return safe_execute_rds(sql)


def get_students_query(     # noqa
    academic_standings=None,
    advisor_plan_mappings=None,
    coe_advisor_ldap_uids=None,
    coe_ethnicities=None,
    coe_genders=None,
    coe_prep_statuses=None,
    coe_probation=None,
    coe_underrepresented=None,
    colleges=None,
    curated_group_ids=None,
    current_term_id=None,
    ethnicities=None,
    entering_terms=None,
    expected_grad_terms=None,
    genders=None,
    gpa_ranges=None,
    group_codes=None,
    in_intensive_cohort=None,
    intended_majors=None,
    is_active_asc=None,
    is_active_coe=None,
    last_name_ranges=None,
    last_term_gpa_ranges=None,
    levels=None,
    majors=None,
    midpoint_deficient_grade=None,
    minors=None,
    scope=(),
    search_phrase=None,
    sids=(),
    transfer=None,
    underrepresented=None,
    unit_ranges=None,
    visa_types=None,
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
        # If a single word, search on both name and email.
        elif len(words) == 1:
            name_string = ''.join(re.split('\W', words[0]))
            email_string = search_phrase.lower()
            query_tables += f"""
                LEFT JOIN {student_schema()}.student_names n
                        ON n.name LIKE :name_string
                        AND n.sid = sas.sid"""
            query_filter += ' AND (sas.email_address LIKE :email_string OR n.name IS NOT NULL)'
            query_bindings.update({'email_string': f'{email_string}%', 'name_string': f'{name_string}%'})
        # If multiple words, search name only.
        else:
            for i, word in enumerate(words):
                query_tables += f"""
                    JOIN {student_schema()}.student_names n{i}
                        ON n{i}.name LIKE :name_phrase_{i}
                        AND n{i}.sid = sas.sid"""
                word = ''.join(re.split('\W', word))
                query_bindings.update({f'name_phrase_{i}': f'{word}%'})
    if academic_standings:
        query_tables += f""" JOIN {student_schema()}.academic_standing ass ON ass.sid = sas.sid"""
    if ethnicities:
        query_tables += f""" JOIN {student_schema()}.ethnicities e ON e.sid = sas.sid"""
    if genders or underrepresented is not None:
        query_tables += f""" JOIN {student_schema()}.demographics d ON d.sid = sas.sid"""
    if visa_types:
        query_tables += f""" JOIN {student_schema()}.visas v ON v.sid = sas.sid"""
    if sids:
        query_filter += ' AND sas.sid = ANY(:sids)'
        query_bindings.update({'sids': sids})
    if curated_group_ids:
        results = db.session.execute(
            'SELECT DISTINCT(sid) FROM student_group_members WHERE student_group_id = ANY(:curated_group_ids)',
            {'curated_group_ids': curated_group_ids},
        )
        query_filter += ' AND sas.sid = ANY(:sids_of_curated_groups)'
        query_bindings.update({'sids_of_curated_groups': [row['sid'] for row in results]})

    # Generic SIS criteria
    if academic_standings:
        query_filter += ' AND ('
        for idx, value in enumerate(academic_standings):
            query_filter += 'OR' if idx else ''
            query_filter += f'(ass.acad_standing_status = :academic_standing_{idx} AND ass.term_id = :academic_standing_term_id_{idx})'
            term_id, academic_standing = value.split(':')
            query_bindings.update({
                f'academic_standing_{idx}': academic_standing,
                f'academic_standing_term_id_{idx}': term_id,
            })
        query_filter += ')'
    if gpa_ranges:
        sql_ready_gpa_ranges = [f"numrange({gpa_range['min']}, {gpa_range['max']}, '[]')" for gpa_range in gpa_ranges]
        query_filter += _number_ranges_to_sql('sas.gpa', sql_ready_gpa_ranges)
    if last_term_gpa_ranges:
        sql_ready_term_gpa_ranges = [f"numrange({gpa_range['min']}, {gpa_range['max']}, '[]')" for gpa_range in last_term_gpa_ranges]
        query_filter += _number_ranges_to_sql('previous_term.term_gpa', sql_ready_term_gpa_ranges)
        query_tables += f"""
            JOIN {student_schema()}.student_enrollment_terms previous_term
            ON previous_term.sid = sas.sid AND previous_term.term_id = :previous_term_id"""
        query_bindings.update({'previous_term_id': previous_term_id(current_term_id)})
    query_filter += _number_ranges_to_sql('sas.units', unit_ranges) if unit_ranges else ''
    if last_name_ranges:
        query_filter += _last_name_ranges_to_sql(last_name_ranges)
    if entering_terms:
        query_filter += ' AND sas.entering_term = ANY(:entering_terms)'
        query_bindings.update({'entering_terms': entering_terms})
    if ethnicities:
        query_filter += ' AND e.ethnicity = ANY(:ethnicities)'
        query_bindings.update({'ethnicities': ethnicities})
    if expected_grad_terms:
        query_filter += ' AND sas.expected_grad_term = ANY(:expected_grad_terms)'
        query_bindings.update({'expected_grad_terms': expected_grad_terms})
    if underrepresented is not None:
        query_filter += ' AND d.minority IS :underrepresented'
        query_bindings.update({'underrepresented': underrepresented})
    if genders:
        query_filter += ' AND d.gender = ANY(:genders)'
        query_bindings.update({'genders': genders})
    if levels:
        query_filter += ' AND sas.level = ANY(:levels)'
        query_bindings.update({'levels': [_level_to_code(level) for level in levels]})
    if intended_majors:
        query_tables += f""" JOIN {student_schema()}.intended_majors i ON i.sid = sas.sid"""
        query_filter += ' AND i.major = ANY(:intended_majors)'
        query_bindings.update({'intended_majors': intended_majors})
    if colleges:
        query_filter += ' AND maj.college = ANY(:colleges)'
        query_bindings.update({'colleges': colleges})
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
        query_bindings.update({'majors': _majors})
    if majors or colleges:
        query_tables += f' LEFT JOIN {student_schema()}.student_majors maj ON maj.sid = sas.sid'
    if midpoint_deficient_grade is True:
        query_tables += f""" JOIN {student_schema()}.student_enrollment_terms ser
                             ON ser.sid = sas.sid
                             AND ser.term_id = :term_id
                             AND ser.midpoint_deficient_grade = TRUE"""
        query_bindings.update({'term_id': current_term_id})
    if minors:
        query_tables += f' LEFT JOIN {student_schema()}.minors min ON min.sid = sas.sid'
        query_filter += ' AND min.minor = ANY(:minors)'
        query_bindings.update({'minors': minors})
    if transfer is True:
        query_filter += ' AND sas.transfer = TRUE'
    if advisor_plan_mappings:
        advisor_plan_filters = []
        for idx, mapping in enumerate(advisor_plan_mappings):
            advisor_sid = mapping['advisor_sid']
            query_bindings.update({f'advisor_sid_{idx}': advisor_sid})
            if mapping['academic_plan_code'] == '*':
                advisor_plan_filters.append(f'advs.advisor_sid = :advisor_sid_{idx}')
            else:
                academic_plan_code = mapping['academic_plan_code']
                query_bindings.update({f'academic_plan_code_{idx}': academic_plan_code})
                advisor_plan_filters.append(
                    f'(advs.advisor_sid = :advisor_sid_{idx} AND advs.academic_plan_code = :academic_plan_code_{idx})',
                )
        query_tables += f""" JOIN {advisor_schema()}.advisor_students advs ON advs.student_sid = sas.sid"""
        query_tables += ' AND (' + ' OR '.join(advisor_plan_filters) + ')'
    if visa_types:
        if '*' in visa_types:
            query_filter += ' AND v.visa_status = \'G\' AND v.visa_type IS NOT NULL'
        else:
            query_filter += ' AND v.visa_status = \'G\' AND v.visa_type = ANY(:visa_types)'
            visa_types_flattened = []
            [visa_types_flattened.extend(t.split(',')) for t in visa_types]
            query_bindings.update({'visa_types': visa_types_flattened})

    # ASC criteria
    query_filter += f' AND s.active IS {is_active_asc}' if is_active_asc is not None else ''
    query_filter += f' AND s.intensive IS {in_intensive_cohort}' if in_intensive_cohort is not None else ''
    if group_codes:
        query_filter += ' AND s.group_code = ANY(:group_codes)'
        query_bindings.update({'group_codes': group_codes})

    # COE criteria
    if coe_advisor_ldap_uids:
        query_filter += ' AND s.advisor_ldap_uid = ANY(:coe_advisor_ldap_uids)'
        query_bindings.update({'coe_advisor_ldap_uids': coe_advisor_ldap_uids})
    if coe_ethnicities:
        query_filter += ' AND s.ethnicity = ANY(:coe_ethnicities)'
        query_bindings.update({'coe_ethnicities': coe_ethnicities})
    if coe_genders:
        query_filter += ' AND s.gender = ANY(:coe_genders)'
        query_bindings.update({'coe_genders': coe_genders})
    if coe_prep_statuses:
        query_filter += ' AND (' + ' OR '.join([f's.{cps} IS TRUE' for cps in coe_prep_statuses]) + ')'
    if coe_probation is not None:
        query_filter += f' AND s.probation IS {coe_probation}'
    if coe_underrepresented is not None:
        query_filter += f' AND s.minority IS {coe_underrepresented}'
    if is_active_coe is False:
        query_filter += " AND s.status IN ('D','P','U','W','X','Z')"
    elif is_active_coe is True:
        query_filter += " AND s.status NOT IN ('D','P','U','W','X','Z')"

    return query_tables, query_filter, query_bindings


def get_students_ordering(current_term_id, order_by=None, group_codes=None, majors=None, scope=None):
    o_direction = 'asc'
    if order_by and order_by.endswith('desc'):
        order_by, o_direction = order_by.rsplit(' ', 1)
    supplemental_query_tables = None
    # Case-insensitive sort of first_name and last_name.
    by_first_name = _naturalize_order('sas.first_name')
    by_last_name = _naturalize_order('sas.last_name')
    o = by_last_name
    if order_by == 'in_intensive_cohort':
        o = 's.intensive'
    elif order_by in ['first_name', 'last_name']:
        o = _naturalize_order(f'sas.{order_by}')
    elif order_by in ['entering_term', 'gpa', 'units', 'level', 'terms_in_attendance']:
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
            o = _naturalize_order('asc_students.group_name')
        else:
            o = _naturalize_order('s.group_name')
    elif order_by == 'major':
        # Majors, like group names, require extra handling in the special case where they are both filter
        # criteria and ordering criteria.
        if majors:
            supplemental_query_tables = f' LEFT JOIN {student_schema()}.student_majors maj2 ON maj2.sid = sas.sid'
            o = _naturalize_order('maj2.major')
        else:
            supplemental_query_tables = f' LEFT JOIN {student_schema()}.student_majors m ON m.sid = sas.sid'
            o = _naturalize_order('m.major')
    elif order_by == 'enrolled_units':
        supplemental_query_tables = f"""
            LEFT JOIN {student_schema()}.student_enrollment_terms set
            ON set.sid = sas.sid AND set.term_id = '{current_term_id}'"""
        o = 'set.enrolled_units'
    elif order_by and order_by.startswith('term_gpa_'):
        gpa_term_id = order_by.replace('term_gpa_', '')
        supplemental_query_tables = f"""
            LEFT JOIN {student_schema()}.student_enrollment_terms set
            ON set.sid = sas.sid AND set.term_id = '{gpa_term_id}'"""
        o = 'set.term_gpa'
    o_secondary = by_first_name if order_by == 'last_name' else by_last_name
    diff = {by_first_name, by_last_name} - {o, o_secondary}
    o_tertiary = diff.pop() if diff else 'sas.sid'
    return o, o_secondary, o_tertiary, o_direction, supplemental_query_tables


def get_admitted_students_query(
    colleges=None,
    family_dependent_ranges=None,
    freshman_or_transfer=None,
    has_fee_waiver=None,
    in_foster_care=None,
    is_family_single_parent=None,
    is_first_generation_college=None,
    is_hispanic=None,
    is_last_school_lcff=None,
    is_reentry=None,
    is_student_single_parent=None,
    is_urem=None,
    residency_categories=None,
    search_phrase=None,
    sir=None,
    special_program_cep=None,
    student_dependent_ranges=None,
    x_ethnicities=None,
):
    query_bindings = {
        'college': colleges,
        'freshman_or_transfer': freshman_or_transfer,
        'residency_categories': residency_categories,
        'special_program_cep': special_program_cep,
        'x_ethnicities': x_ethnicities,
    }
    query_tables = f'FROM {oua_schema()}.student_admits sa'
    query_filter = 'WHERE true'
    query_filter += ' AND sa.college = ANY(:college)' if colleges else ''
    query_filter += ' AND sa.current_sir = \'Yes\'' if sir else ''
    query_filter += ' AND sa.freshman_or_transfer = ANY(:freshman_or_transfer)' if freshman_or_transfer else ''
    query_filter += ' AND sa.application_fee_waiver_flag = \'FeeWaiver\'' if has_fee_waiver else ''
    query_filter += ' AND sa.foster_care_flag = \'Y\'' if in_foster_care else ''
    query_filter += ' AND sa.special_program_cep = ANY(:special_program_cep)' if special_program_cep else ''
    query_filter += ' AND sa.family_is_single_parent = \'Y\'' if is_family_single_parent else ''
    query_filter += ' AND sa.first_generation_college = \'Yes\'' if is_first_generation_college else ''
    query_filter += ' AND sa.hispanic = \'T\'' if is_hispanic else ''
    query_filter += ' AND sa.last_school_lcff_plus_flag = \'1\'' if is_last_school_lcff else ''
    query_filter += ' AND sa.reentry_status = \'Yes\'' if is_reentry else ''
    query_filter += ' AND sa.residency_category = ANY(:residency_categories)' if residency_categories else ''
    query_filter += ' AND sa.student_is_single_parent = \'Y\'' if is_student_single_parent else ''
    query_filter += ' AND sa.urem = \'Yes\'' if is_urem else ''
    query_filter += ' AND sa.xethnic = ANY(:x_ethnicities)' if x_ethnicities else ''
    # Ranges
    if family_dependent_ranges:
        sql_ready_ranges = [f"numrange({range_['min']}, {range_['max']}, '[]')" for range_ in family_dependent_ranges]
        query_filter += _number_ranges_to_sql('CAST(NULLIF(family_dependents_num, \'\') AS INT)', sql_ready_ranges)
    if student_dependent_ranges:
        sql_ready_ranges = [f"numrange({range_['min']}, {range_['max']}, '[]')" for range_ in student_dependent_ranges]
        query_filter += _number_ranges_to_sql('CAST(NULLIF(student_dependents_num, \'\') AS INT)', sql_ready_ranges)
    # Name or SID search
    if search_phrase:
        words = search_phrase.upper().split()
        # A numeric string indicates an SID search.
        if len(words) == 1 and re.match(r'^\d+$', words[0]):
            query_filter += ' AND (sa.cs_empl_id LIKE :sid_phrase)'
            query_bindings.update({'sid_phrase': f'{words[0]}%'})
            temp_table = ''
        else:
            for i, word in enumerate(words):
                query_tables += f"""
                    JOIN admit_names n{i}
                        ON n{i}.name LIKE :name_phrase_{i}
                        AND n{i}.cs_empl_id = sa.cs_empl_id"""
                word = ''.join(re.split(r'\W', word))
                query_bindings.update({f'name_phrase_{i}': f'{word}%'})
            temp_table = f"""WITH admit_names AS (
                SELECT DISTINCT cs_empl_id, unnest(string_to_array(
                regexp_replace(upper(first_name), '[^\w ]', '', 'g'),
                ' '
                )) AS name FROM {oua_schema()}.student_admits
                UNION
                SELECT DISTINCT cs_empl_id, unnest(string_to_array(
                    regexp_replace(upper(middle_name), '[^\w ]', '', 'g'),
                    ' '
                )) AS name FROM {oua_schema()}.student_admits
                UNION
                SELECT DISTINCT cs_empl_id, unnest(string_to_array(
                    regexp_replace(upper(last_name), '[^\w ]', '', 'g'),
                    ' '
                )) AS name FROM {oua_schema()}.student_admits
            )"""
        return query_tables, query_filter, query_bindings, temp_table
    return query_tables, query_filter, query_bindings


def _level_to_code(level):
    codes = {
        'Freshman': '10',
        'Sophomore': '20',
        'Junior': '30',
        'Senior': '40',
        'Graduate': 'GR',
    }
    return codes.get(level, level)


def _naturalize_order(column_name):
    return f"UPPER(regexp_replace({column_name}, '\\\W', ''))"


def _number_range_to_sql(column, numrange):
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


def _number_ranges_to_sql(column, number_ranges):
    sql_ranges = [_number_range_to_sql(column, number_range) for number_range in number_ranges]
    sql_ranges = [r for r in sql_ranges if r]
    if len(sql_ranges):
        return ' AND (' + ' OR '.join(sql_ranges) + ')'
    else:
        return ''


def _last_name_ranges_to_sql(last_name_ranges):
    query_filter = ''
    count = len(last_name_ranges)
    if count:
        query_filter += ' AND ('
        for idx, last_name_range in enumerate(last_name_ranges):
            range_min = last_name_range['min']
            range_max = last_name_range['max']
            if range_max == range_min:
                query_filter += f'(sas.last_name ILIKE \'{range_min}%\')'
            else:
                query_filter += f'(UPPER(sas.last_name) >= \'{range_min}\''
                if range_max < 'Z':
                    # If 'stop' were 'Z' then upper bound would not be necessary
                    query_filter += f' AND UPPER(sas.last_name) < \'{chr(ord(range_max) + 1)}\''
                query_filter += ')'
            if idx < count - 1:
                query_filter += ' OR '
        query_filter += ')'
    return query_filter


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
                    'gender',
                    'ethnicity',
                    'minority',
                    'did_prep',
                    'did_tprep',
                    'prep_eligible',
                    'probation',
                    'status',
                    'tprep_eligible',
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
