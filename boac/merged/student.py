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

import json

from boac.externals import data_loch
from boac.lib import analytics
from boac.lib.berkeley import current_term_id
from flask_login import current_user


"""Provide merged student data from external sources."""


def get_api_json(sids):
    def distill_profile(profile):
        distilled = {key: profile[key] for key in ['uid', 'sid', 'firstName', 'lastName', 'name']}
        if profile.get('athleticsProfile'):
            distilled['athleticsProfile'] = profile['athleticsProfile']
        return distilled
    return [distill_profile(profile) for profile in get_full_student_profiles(sids)]


def get_full_student_profiles(sids):
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

    return profiles


def get_course_student_profiles(term_id, section_id):
    sids = [str(r['sid']) for r in data_loch.get_sis_section_enrollments(term_id, section_id, get_student_query_scope())]

    # TODO It's probably more efficient to store class profiles in the loch, rather than distilling them
    # on the fly from full profiles.
    students = get_full_student_profiles(sids)

    enrollments_for_term = data_loch.get_enrollments_for_term(term_id, sids)
    enrollments_by_sid = {row['sid']: json.loads(row['enrollment_term']) for row in enrollments_for_term}
    for student in students:
        # Strip SIS details to lighten the API load.
        sis_profile = student.pop('sisProfile', None)
        if sis_profile:
            student['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
            student['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
            student['level'] = sis_profile.get('level', {}).get('description')
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
                    }
                    student['analytics'] = analytics.mean_metrics_across_sites(canvas_sites)
                    continue
    return students


def get_summary_student_profiles(sids, term_id=None):
    # TODO It's probably more efficient to store summary profiles in the loch, rather than distilling them
    # on the fly from full profiles.
    profiles = get_full_student_profiles(sids)
    # TODO Many views require no term enrollment information other than a units count. This datum too should be
    # stored in the loch without BOAC having to crunch it.
    if not term_id:
        term_id = current_term_id()
    enrollments_for_term = data_loch.get_enrollments_for_term(term_id, sids)
    enrollments_by_sid = {row['sid']: json.loads(row['enrollment_term']) for row in enrollments_for_term}
    for profile in profiles:
        # Strip SIS details to lighten the API load.
        sis_profile = profile.pop('sisProfile', None)
        if sis_profile:
            profile['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
            profile['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
            profile['level'] = sis_profile.get('level', {}).get('description')
            profile['majors'] = sorted(plan.get('description') for plan in sis_profile.get('plans', []))
        # Add the singleton term.
        term = enrollments_by_sid.get(profile['sid'])
        profile['hasCurrentTermEnrollments'] = False
        if term:
            profile['analytics'] = term.pop('analytics', None)
            profile['term'] = term
            if term['termId'] == current_term_id() and len(term['enrollments']) > 0:
                profile['hasCurrentTermEnrollments'] = True
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
    enrollments_for_sid = data_loch.get_enrollments_for_sid(student['sid'])
    profile['enrollmentTerms'] = [json.loads(row['enrollment_term']) for row in enrollments_for_sid]
    profile['hasCurrentTermEnrollments'] = False
    for term in profile['enrollmentTerms']:
        if term['termId'] == current_term_id():
            profile['hasCurrentTermEnrollments'] = len(term['enrollments']) > 0
            break
    return profile


def query_students(
        include_profiles=False,
        advisor_ldap_uid=None,
        gpa_ranges=None,
        group_codes=None,
        in_intensive_cohort=None,
        is_active_asc=None,
        levels=None,
        limit=50,
        majors=None,
        offset=0,
        order_by=None,
        sids_only=False,
        unit_ranges=None,
):
    scope = narrow_scope_by_criteria(
        get_student_query_scope(),
        in_intensive_cohort=in_intensive_cohort,
        is_active_asc=is_active_asc,
        group_codes=group_codes,
        advisor_ldap_uid=advisor_ldap_uid,
    )
    query_tables, query_filter, query_bindings = data_loch.get_students_query(
        group_codes=group_codes,
        gpa_ranges=gpa_ranges,
        levels=levels,
        majors=majors,
        unit_ranges=unit_ranges,
        in_intensive_cohort=in_intensive_cohort,
        is_active_asc=is_active_asc,
        advisor_ldap_uid=advisor_ldap_uid,
        scope=scope,
    )
    if not query_tables:
        return {
            'sids': [],
            'students': [],
            'totalStudentCount': 0,
        }    # First, get total_count of matching students
    result = data_loch.safe_execute_rds(f'SELECT DISTINCT(sas.sid) {query_tables} {query_filter}', **query_bindings)
    if result is None:
        return None
    summary = {
        'totalStudentCount': len(result),
    }
    if sids_only:
        summary['sids'] = [row['sid'] for row in result]
    else:
        o, o_secondary, o_tertiary, supplemental_query_tables = data_loch.get_students_ordering(
            order_by=order_by,
            group_codes=group_codes,
            majors=majors,
        )
        if supplemental_query_tables:
            query_tables += supplemental_query_tables
        sql = f"""SELECT
            sas.sid, MIN({o}), MIN({o_secondary}), MIN({o_tertiary})
            {query_tables}
            {query_filter}
            GROUP BY sas.sid
            ORDER BY MIN({o}) NULLS FIRST, MIN({o_secondary}) NULLS FIRST, MIN({o_tertiary}) NULLS FIRST"""
        if o_tertiary != 'sas.sid':
            sql += ', sas.sid'
        sql += ' OFFSET :offset'
        query_bindings['offset'] = offset
        if limit and limit < 100:  # Sanity check large limits
            query_bindings['limit'] = limit
            sql += f' LIMIT :limit'
        result = data_loch.safe_execute_rds(sql, **query_bindings)
        if include_profiles:
            summary['students'] = get_summary_student_profiles([row['sid'] for row in result])
        else:
            summary['students'] = get_api_json([row['sid'] for row in result])
    return summary


def search_for_students(
    include_profiles=False,
    search_phrase=None,
    is_active_asc=None,
    order_by=None,
    offset=0,
    limit=None,
):
    scope = narrow_scope_by_criteria(
        get_student_query_scope(),
        is_active_asc=is_active_asc,
    )
    query_tables, query_filter, query_bindings = data_loch.get_students_query(
        search_phrase=search_phrase,
        is_active_asc=is_active_asc,
        scope=scope,
    )
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
        ],
        'COENG': [
            'advisor_ldap_uid',
        ],
    }

    # An explicit False counts as present, but other falsey criteria don't.
    def any_criterion_present(criteria):
        for c in criteria:
            value = kwargs.get(c)
            if value or value is False:
                return True
        return False

    for code, criteria in criteria_for_code.items():
        if any_criterion_present(criteria):
            if 'ADMIN' in scope or code in scope:
                # We've found a department-specific criterion; constrain scope to that department only.
                return [code]
            else:
                # We've found a department-specific criterion but that department wasn't in the provided scope.
                # Return empty.
                return []
    # No department-specific criteria found; return unmodified.
    return scope
