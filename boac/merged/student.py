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

from datetime import timezone
from itertools import groupby
import json
import operator
import re

from boac.externals import data_loch
from boac.lib import analytics
from boac.lib.berkeley import current_term_id, term_name_for_sis_id
from boac.models.note_read import NoteRead
from flask import current_app as app
from flask_login import current_user


"""Provide merged student data from external sources."""


def get_api_json(sids):
    if not sids:
        return []

    def distill_profile(profile):
        distilled = {key: profile[key] for key in ['uid', 'sid', 'firstName', 'lastName', 'name']}
        if profile.get('athleticsProfile'):
            distilled['athleticsProfile'] = profile['athleticsProfile']
        if profile.get('coeProfile'):
            distilled['coeProfile'] = profile['coeProfile']
        return distilled
    return [distill_profile(profile) for profile in get_full_student_profiles(sids)]


def get_full_student_profiles(sids):
    if not sids:
        return []
    profile_results = data_loch.get_student_profiles(sids)
    if not profile_results:
        return []
    profiles_by_sid = {row['sid']: json.loads(row['profile']) for row in profile_results}
    profiles = []
    for sid in sids:
        profile = profiles_by_sid.get(sid)
        if profile:
            profiles.append(profile)

    scope = get_student_query_scope()
    if 'UWASC' in scope or 'ADMIN' in scope:
        athletics_profiles = data_loch.get_athletics_profiles(sids)
        for row in athletics_profiles:
            profile = profiles_by_sid.get(row['sid'])
            if profile:
                profile['athleticsProfile'] = json.loads(row['profile'])
    if 'COENG' in scope or 'ADMIN' in scope:
        coe_profiles = data_loch.get_coe_profiles(sids)
        if coe_profiles:
            for row in coe_profiles:
                profile = profiles_by_sid.get(row['sid'])
                if profile:
                    profile['coeProfile'] = json.loads(row['profile'])
                    if profile['coeProfile'].get('status') in ['D', 'P', 'U', 'W', 'X', 'Z']:
                        profile['coeProfile']['isActiveCoe'] = False
                    else:
                        profile['coeProfile']['isActiveCoe'] = True

    return profiles


def get_course_student_profiles(term_id, section_id, offset=None, limit=None, featured=None):
    enrollment_rows = data_loch.get_sis_section_enrollments(
        term_id,
        section_id,
        scope=get_student_query_scope(),
        offset=offset,
        limit=limit,
    )
    sids = [str(r['sid']) for r in enrollment_rows]
    if offset or len(sids) >= 50:
        count_result = data_loch.get_sis_section_enrollments_count(term_id, section_id, scope=get_student_query_scope())
        total_student_count = count_result[0]['count']
    else:
        total_student_count = len(sids)

    # If we have a featured UID not already present in the result set, add the corresponding SID only if the
    # student is enrolled and falls within view permissions.
    if featured and not next((r for r in enrollment_rows if str(r['uid']) == featured), None):
        featured_enrollment_rows = data_loch.get_sis_section_enrollment_for_uid(term_id, section_id, featured, get_student_query_scope())
        if featured_enrollment_rows:
            sids = [str(featured_enrollment_rows[0]['sid'])] + sids

    # TODO It's probably more efficient to store class profiles in the loch, rather than distilling them
    # on the fly from full profiles.
    students = get_full_student_profiles(sids)

    enrollments_for_term = data_loch.get_enrollments_for_term(term_id, sids)
    enrollments_by_sid = {row['sid']: json.loads(row['enrollment_term']) for row in enrollments_for_term}
    term_gpas = get_term_gpas_by_sid(sids, as_dicts=True)
    all_canvas_sites = {}
    for student in students:
        # Strip SIS details to lighten the API load.
        sis_profile = student.pop('sisProfile', None)
        if sis_profile:
            student['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
            student['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
            student['level'] = _get_sis_level_description(sis_profile)
            student['currentTerm'] = sis_profile.get('currentTerm')
            student['majors'] = sorted(plan.get('description') for plan in sis_profile.get('plans', []))
        term = enrollments_by_sid.get(student['sid'])
        student['hasCurrentTermEnrollments'] = False
        if term:
            # Strip the enrollments list down to the section of interest.
            enrollments = term.pop('enrollments', [])
            for enrollment in enrollments:
                _section = next((s for s in enrollment['sections'] if str(s['ccn']) == section_id), None)
                if _section:
                    canvas_sites = enrollment.get('canvasSites', [])
                    student['enrollment'] = {
                        'canvasSites': canvas_sites,
                        'enrollmentStatus': _section.get('enrollmentStatus', None),
                        'grade': enrollment.get('grade', None),
                        'gradingBasis': enrollment.get('gradingBasis', None),
                        'midtermGrade': enrollment.get('midtermGrade', None),
                    }
                    student['analytics'] = analytics.mean_metrics_across_sites(canvas_sites, 'student')
                    # If more than one course site is associated with this section, derive mean metrics from as many sites as possible.
                    for site in canvas_sites:
                        if site['canvasCourseId'] not in all_canvas_sites:
                            all_canvas_sites[site['canvasCourseId']] = site
                    continue
        student['termGpa'] = term_gpas.get(student['sid'])
    mean_metrics = analytics.mean_metrics_across_sites(all_canvas_sites.values(), 'courseMean')
    mean_metrics['gpa'] = {}
    mean_gpas = data_loch.get_sis_section_mean_gpas(term_id, section_id)
    for row in mean_gpas:
        mean_metrics['gpa'][str(row['gpa_term_id'])] = row['avg_gpa']
    return {
        'students': students,
        'totalStudentCount': total_student_count,
        'meanMetrics': mean_metrics,
    }


def get_summary_student_profiles(sids, term_id=None):
    if not sids:
        return []
    # TODO It's probably more efficient to store summary profiles in the loch, rather than distilling them
    # on the fly from full profiles.
    profiles = get_full_student_profiles(sids)
    # TODO Many views require no term enrollment information other than a units count. This datum too should be
    # stored in the loch without BOAC having to crunch it.
    if not term_id:
        term_id = current_term_id()
    enrollments_for_term = data_loch.get_enrollments_for_term(term_id, sids)
    enrollments_by_sid = {row['sid']: json.loads(row['enrollment_term']) for row in enrollments_for_term}
    term_gpas = get_term_gpas_by_sid(sids)
    for profile in profiles:
        # Strip SIS details to lighten the API load.
        sis_profile = profile.pop('sisProfile', None)
        if sis_profile:
            profile['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
            profile['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
            profile['currentTerm'] = sis_profile.get('currentTerm')
            profile['expectedGraduationTerm'] = sis_profile.get('expectedGraduationTerm')
            profile['level'] = _get_sis_level_description(sis_profile)
            profile['majors'] = sorted(plan.get('description') for plan in sis_profile.get('plans', []))
            if sis_profile.get('withdrawalCancel'):
                profile['withdrawalCancel'] = sis_profile['withdrawalCancel']
        # Add the singleton term.
        term = enrollments_by_sid.get(profile['sid'])
        profile['hasCurrentTermEnrollments'] = False
        if term:
            profile['analytics'] = term.pop('analytics', None)
            profile['term'] = term
            if term['termId'] == current_term_id() and len(term['enrollments']) > 0:
                profile['hasCurrentTermEnrollments'] = True
        profile['termGpa'] = term_gpas.get(profile['sid'])
    return profiles


def get_student_and_terms(uid):
    """Provide external data for student-specific view."""
    student = data_loch.get_student_for_uid_and_scope(uid, get_student_query_scope())
    if not student:
        return
    profiles = get_full_student_profiles([student['sid']])
    if not profiles or not profiles[0]:
        return
    profile = profiles[0]
    sis_profile = profile.get('sisProfile', None)
    if sis_profile and 'level' in sis_profile:
        sis_profile['level']['description'] = _get_sis_level_description(sis_profile)
    enrollments_for_sid = data_loch.get_enrollments_for_sid(student['sid'], latest_term_id=current_term_id())
    profile['enrollmentTerms'] = [json.loads(row['enrollment_term']) for row in enrollments_for_sid]
    profile['hasCurrentTermEnrollments'] = False
    for term in profile['enrollmentTerms']:
        if term['termId'] == current_term_id():
            profile['hasCurrentTermEnrollments'] = len(term['enrollments']) > 0
        else:
            # Omit dropped sections for past terms.
            term.pop('droppedSections', None)
    return profile


def get_term_gpas_by_sid(sids, as_dicts=False):
    results = data_loch.get_term_gpas(sids)
    term_gpa_dict = {}
    for sid, rows in groupby(results, key=operator.itemgetter('sid')):
        if as_dicts:
            term_gpa_dict[sid] = {str(r['term_id']): r['gpa'] for r in rows}
        else:
            term_gpa_dict[sid] = [{'termName': term_name_for_sis_id(r['term_id']), 'gpa': r['gpa']} for r in rows]
    return term_gpa_dict


def query_students(
    advisor_ldap_uids=None,
    coe_prep_statuses=None,
    coe_probation=None,
    ethnicities=None,
    genders=None,
    gpa_ranges=None,
    group_codes=None,
    in_intensive_cohort=None,
    include_profiles=False,
    is_active_asc=None,
    is_active_coe=None,
    last_name_range=None,
    levels=None,
    limit=50,
    majors=None,
    offset=0,
    order_by=None,
    sids_only=False,
    underrepresented=None,
    unit_ranges=None,
):
    criteria = {
        'advisor_ldap_uids': advisor_ldap_uids,
        'coe_prep_statuses': coe_prep_statuses,
        'coe_probation': coe_probation,
        'ethnicities': ethnicities,
        'genders': genders,
        'group_codes': group_codes,
        'in_intensive_cohort': in_intensive_cohort,
        'is_active_asc': is_active_asc,
        'is_active_coe': is_active_coe,
        'underrepresented': underrepresented,
    }
    scope = narrow_scope_by_criteria(get_student_query_scope(), **criteria)
    query_tables, query_filter, query_bindings = data_loch.get_students_query(
        advisor_ldap_uids=advisor_ldap_uids,
        coe_prep_statuses=coe_prep_statuses,
        coe_probation=coe_probation,
        ethnicities=ethnicities,
        genders=genders,
        gpa_ranges=gpa_ranges,
        group_codes=group_codes,
        in_intensive_cohort=in_intensive_cohort,
        is_active_asc=is_active_asc,
        is_active_coe=is_active_coe,
        last_name_range=last_name_range,
        levels=levels,
        majors=majors,
        scope=scope,
        underrepresented=underrepresented,
        unit_ranges=unit_ranges,
    )
    if not query_tables:
        return {
            'sids': [],
            'students': [],
            'totalStudentCount': 0,
        }    # First, get total_count of matching students
    sids_result = data_loch.safe_execute_rds(f'SELECT DISTINCT(sas.sid) {query_tables} {query_filter}', **query_bindings)
    if sids_result is None:
        return None
    # Upstream logic may require the full list of SIDs even if we're only returning full results for a particular
    # paged slice.
    summary = {
        'sids': [row['sid'] for row in sids_result],
        'totalStudentCount': len(sids_result),
    }
    if not sids_only:
        o, o_secondary, o_tertiary, supplemental_query_tables = data_loch.get_students_ordering(
            order_by=order_by,
            group_codes=group_codes,
            majors=majors,
            scope=scope,
        )
        if supplemental_query_tables:
            query_tables += supplemental_query_tables
        # Sorting by team is the one case where null results should go below not-null results.
        o_null_order = 'NULLS LAST' if 'group_name' in o else 'NULLS FIRST'
        sql = f"""SELECT
            sas.sid, MIN({o}), MIN({o_secondary}), MIN({o_tertiary})
            {query_tables}
            {query_filter}
            GROUP BY sas.sid
            ORDER BY MIN({o}) {o_null_order}, MIN({o_secondary}) NULLS FIRST, MIN({o_tertiary}) NULLS FIRST"""
        if o_tertiary != 'sas.sid':
            sql += ', sas.sid'
        sql += ' OFFSET :offset'
        query_bindings['offset'] = offset
        if limit and limit < 100:  # Sanity check large limits
            query_bindings['limit'] = limit
            sql += f' LIMIT :limit'
        students_result = data_loch.safe_execute_rds(sql, **query_bindings)
        if include_profiles:
            summary['students'] = get_summary_student_profiles([row['sid'] for row in students_result])
        else:
            summary['students'] = get_api_json([row['sid'] for row in students_result])
    return summary


def search_advising_notes(
    search_phrase=None,
    is_active_asc=None,
    is_active_coe=None,
    limit=None,
):
    scope = narrow_scope_by_criteria(
        get_student_query_scope(),
        is_active_asc=is_active_asc,
        is_active_coe=is_active_coe,
    )
    # Since we can't join between RDS and Redshift (or any future notes search implementation), we mimic a join
    # by first querying RDS for all student rows matching user scope, then incorporating SIDs into the notes query
    # as a very large array filter.
    query_tables, query_filter, query_bindings = data_loch.get_students_query(
        is_active_asc=is_active_asc,
        is_active_coe=is_active_coe,
        scope=scope,
    )
    if not query_tables:
        return []
    sids_result = data_loch.safe_execute_rds(
        f'SELECT sas.sid, sas.uid, sas.first_name, sas.last_name {query_tables} {query_filter}',
        **query_bindings,
    )
    if not sids_result:
        return []
    rows_by_sid = {row['sid']: row for row in sids_result}
    sid_filter = '{' + ','.join(rows_by_sid.keys()) + '}'

    notes_results = data_loch.search_advising_notes(
        search_phrase=f'%{search_phrase}%',
        sid_filter=sid_filter,
        limit=limit,
    )

    def _notes_result_to_json(row):
        rds_row = rows_by_sid[row.get('sid')]
        return {
            'studentSid': row.get('sid'),
            'studentUid': rds_row.get('uid'),
            'studentName': ' '.join([rds_row.get('first_name'), rds_row.get('last_name')]),
            'advisorSid': row.get('advisor_sid'),
            'noteId': row.get('id'),
            'noteSnippet': notes_text_snippet(row.get('note_body'), search_phrase),
            'createdAt': _stringify_note_timestamp(row.get('created_at')),
            'updatedAt': _stringify_note_timestamp(row.get('updated_at')),
        }
    return [_notes_result_to_json(row) for row in notes_results]


def notes_text_snippet(note_body, search_phrase):
    fragments = re.split(f'({re.escape(search_phrase)})', note_body, flags=re.IGNORECASE)
    if len(fragments) < 3:
        return note_body
    before_words = fragments[0].split(' ')
    match = fragments[1]
    after_words = ''.join(fragments[2:]).split(' ')
    before_text = ' '.join(before_words[-30:])
    after_text = ' '.join(after_words[:30])
    if len(before_words) > 30:
        before_text = '...' + before_text
    if len(after_words) > 30:
        after_text += '...'
    return f'{before_text}<strong>{match}</strong>{after_text}'


def search_for_students(
    include_profiles=False,
    search_phrase=None,
    order_by=None,
    offset=0,
    limit=None,
):
    scope = narrow_scope_by_criteria(get_student_query_scope())
    query_tables, query_filter, query_bindings = data_loch.get_students_query(search_phrase=search_phrase, scope=scope)
    if not query_tables:
        return {
            'students': [],
            'totalStudentCount': 0,
        }
    o, o_secondary, o_tertiary, supplemental_query_tables = data_loch.get_students_ordering(order_by=order_by)
    if supplemental_query_tables:
        query_tables += supplemental_query_tables
    result = data_loch.safe_execute_rds(f'SELECT DISTINCT(sas.sid) {query_tables} {query_filter}', **query_bindings)
    total_student_count = len(result)
    sql = f"""SELECT
        sas.sid
        {query_tables}
        {query_filter}
        GROUP BY sas.sid
        ORDER BY MIN({o}) NULLS FIRST, MIN({o_secondary}) NULLS FIRST, MIN({o_tertiary}) NULLS FIRST"""
    if o_tertiary != 'sas.sid':
        sql += ', sas.sid'
    sql += f' OFFSET {offset}'
    if limit and limit < 100:  # Sanity check large limits
        sql += f' LIMIT :limit'
        query_bindings['limit'] = limit
    result = data_loch.safe_execute_rds(sql, **query_bindings)
    if include_profiles:
        students = get_summary_student_profiles([row['sid'] for row in result])
    else:
        students = get_api_json([row['sid'] for row in result])
    return {
        'students': students,
        'totalStudentCount': total_student_count,
    }


def _note_to_json(note, topics, attachments):
    return {
        'id': note.get('id'),
        'sid': note.get('sid'),
        'advisorSid': note.get('advisor_sid'),
        'body': note.get('note_body'),
        'category': note.get('note_category'),
        'subcategory': note.get('note_subcategory'),
        'appointmentId': note.get('appointment_id'),
        'createdBy': note.get('created_by'),
        'createdAt': _stringify_note_timestamp(note.get('created_at')),
        'updatedBy': note.get('updated_by'),
        'updatedAt': _stringify_note_timestamp(note.get('updated_at')),
        'read': False,
        'topics': topics,
        'attachments': attachments,
    }


def _stringify_note_timestamp(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _get_advising_note_topics(sid):
    topics = data_loch.get_advising_note_topics(sid)
    topics_by_id = {}
    for advising_note_id, topics in groupby(topics, key=operator.itemgetter('advising_note_id')):
        topics_by_id[advising_note_id] = [topic['note_topic'] for topic in topics]
    return topics_by_id


def _get_advising_note_attachments(sid):
    attachments = data_loch.get_advising_note_attachments(sid)
    attachments_by_id = {}
    for advising_note_id, attachments in groupby(attachments, key=operator.itemgetter('advising_note_id')):
        attachments_by_id[advising_note_id] = [attachments['sis_file_name'] for attachments in attachments]
    return attachments_by_id


def get_advising_notes(sid):
    advising_notes = data_loch.get_advising_notes(sid)
    if not advising_notes:
        return None
    topics = _get_advising_note_topics(sid)
    attachments = _get_advising_note_attachments(sid)
    notes_by_id = {}
    for note in advising_notes:
        note_id = note['id']
        notes_by_id[note_id] = _note_to_json(note, topics.get(note_id), attachments.get(note_id))
    notes_read = NoteRead.get_notes_read_by_user(current_user.id, notes_by_id.keys())
    for note_read in notes_read:
        note_feed = notes_by_id.get(note_read.note_id)
        if note_feed:
            note_feed['read'] = True
        else:
            app.logger.error(f'DB query mismatch for note id {note_read.note_id}')
    return list(notes_by_id.values())


def get_student_query_scope():
    # Use department membership and admin status to determine what data we can surface about which students.
    # If this code is being called outside an HTTP request context, then assume it is an administrative task.
    # Not all current_user proxy types define all attributes, and so the ordering of these conditional checks
    # is important.
    if not current_user:
        return ['ADMIN']
    elif not current_user.is_authenticated:
        return []
    elif current_user.is_admin:
        return ['ADMIN']
    else:
        return [m.university_dept.dept_code for m in current_user.department_memberships]


def narrow_scope_by_criteria(scope, **kwargs):
    # Searching by ASC-specific criteria will constrain the scope to ASC students; likewise for COE.
    criteria_for_code = {
        'UWASC': [
            'in_intensive_cohort',
            'is_active_asc',
            'group_codes',
            'group_name',
        ],
        'COENG': [
            'advisor_ldap_uids',
            'is_active_coe',
            'coe_prep_statuses',
            'coe_probation',
            'ethnicities',
            'genders',
            'underrepresented',
        ],
    }

    # An explicit False counts as present, but other falsey criteria don't.
    def any_criterion_present(criteria_):
        for c in criteria_:
            value = kwargs.get(c)
            if value or value is False:
                return True
        return False

    narrowed_scope = []
    for code, criteria in criteria_for_code.items():
        if any_criterion_present(criteria):
            if 'ADMIN' in scope or code in scope:
                # We've found a department-specific criterion; add a scope constraint for that department.
                narrowed_scope.append(code)
            else:
                # We've found a department-specific criterion but that department wasn't in the provided scope.
                # Return empty.
                return []

    if not narrowed_scope:
        # No department-specific criteria found; return the original scope unmodified.
        return scope
    elif len(narrowed_scope) == 1:
        # Criteria were found for one department; return a single-item array including that department.
        return narrowed_scope
    else:
        # Criteria were found for more than one department; return an intersection of those departments.
        return {'intersection': narrowed_scope}


def _get_sis_level_description(profile):
    level = profile.get('level', {}).get('description')
    if level == 'Not Set':
        return None
    else:
        return level
