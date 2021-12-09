"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from itertools import groupby
import json
import operator

from boac import db
from boac.externals import data_loch, s3
from boac.lib import analytics
from boac.lib.berkeley import academic_year_for_term_name, dept_codes_where_advising, term_name_for_sis_id
from boac.lib.util import get_benchmarker
from boac.merged.sis_terms import current_term_id, current_term_name, future_term_id
from flask import current_app as app
from flask_login import current_user
from sqlalchemy import text


"""Provide merged student data from external sources."""


def get_distilled_student_profiles(sids):
    if not sids:
        return []

    def distill_profile(profile):
        distilled = {
            key: profile.get(key) for key in
            [
                'firstName',
                'gender',
                'lastName',
                'name',
                'photoUrl',
                'sid',
                'uid',
                'underrepresented',
            ]
        }
        distilled['academicCareerStatus'] = profile['sisProfile'].get('academicCareerStatus')
        distilled['termsInAttendance'] = profile['sisProfile'].get('termsInAttendance')
        if profile.get('athleticsProfile'):
            distilled['athleticsProfile'] = profile['athleticsProfile']
        if profile.get('coeProfile'):
            distilled['coeProfile'] = profile['coeProfile']
        return distilled
    profiles = get_full_student_profiles(sids)
    return [distill_profile(profile) for profile in profiles]


def get_full_student_profiles(sids):
    benchmark = get_benchmarker('get_full_student_profiles')
    benchmark('begin')
    if not sids:
        return []
    benchmark('begin SIS profile query')
    profile_results = data_loch.get_student_profiles(sids)
    benchmark('end SIS profile query')
    if not profile_results:
        return []
    profiles_by_sid = _get_profiles_by_sid(profile_results)
    profiles = []
    for sid in sids:
        profile = profiles_by_sid.get(sid)
        if profile:
            profiles.append(profile)

    benchmark('begin photo merge')
    _merge_photo_urls(profiles)
    benchmark('end photo merge')

    scope = get_student_query_scope()

    benchmark('begin ASC profile merge')
    athletics_profiles = data_loch.get_athletics_profiles(sids)
    if athletics_profiles:
        for athletics_profile in athletics_profiles:
            sid = athletics_profile['sid']
            _merge_asc_student_profile_data(profiles_by_sid.get(sid), athletics_profile, scope)
    benchmark('end ASC profile merge')

    if 'COENG' in scope or 'ADMIN' in scope:
        benchmark('begin COE profile merge')
        coe_profiles = data_loch.get_coe_profiles(sids)
        if coe_profiles:
            for coe_profile in coe_profiles:
                sid = coe_profile['sid']
                _merge_coe_student_profile_data(profiles_by_sid.get(sid), coe_profile)
        benchmark('end COE profile merge')
    return profiles


def get_course_student_profiles(term_id, section_id, offset=None, limit=None, featured=None):
    benchmark = get_benchmarker('get_course_student_profiles')
    benchmark('begin')
    enrollment_rows = data_loch.get_sis_section_enrollments(
        term_id,
        section_id,
        offset=offset,
        limit=limit,
    )
    sids = [str(r['sid']) for r in enrollment_rows]
    if offset or len(sids) >= 50:
        count_result = data_loch.get_sis_section_enrollments_count(term_id, section_id)
        total_student_count = count_result[0]['count']
    else:
        total_student_count = len(sids)

    # If we have a featured UID not already present in the result set, add the corresponding SID only if the
    # student is enrolled.
    if featured and not next((r for r in enrollment_rows if str(r['uid']) == featured), None):
        featured_enrollment_rows = data_loch.get_sis_section_enrollment_for_uid(term_id, section_id, featured)
        if featured_enrollment_rows:
            sids = [str(featured_enrollment_rows[0]['sid'])] + sids

    # TODO It's probably more efficient to store class profiles in the loch, rather than distilling them
    # on the fly from full profiles.
    students = get_full_student_profiles(sids)

    benchmark('begin enrollments query')
    enrollments_for_term = data_loch.get_enrollments_for_term(term_id, sids)
    benchmark('end enrollments query')
    enrollments_by_sid = {row['sid']: json.loads(row['enrollment_term']) for row in enrollments_for_term}
    academic_standing = get_academic_standing_by_sid(sids, as_dicts=True)
    term_gpas = get_term_gpas_by_sid(sids, as_dicts=True)
    all_canvas_sites = {}
    benchmark('begin profile transformation')
    for student in students:
        # Strip SIS details to lighten the API load.
        sis_profile = student.pop('sisProfile', None)
        if sis_profile:
            student['academicCareerStatus'] = sis_profile.get('academicCareerStatus')
            student['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
            student['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
            student['degrees'] = sis_profile.get('degrees')
            student['level'] = _get_sis_level_description(sis_profile)
            student['currentTerm'] = sis_profile.get('currentTerm')
            student['majors'] = _get_active_plan_descriptions(sis_profile)
            student['transfer'] = sis_profile.get('transfer')
        term = enrollments_by_sid.get(student['sid'])
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
        student['academicStanding'] = academic_standing.get(student['sid'])
        student['termGpa'] = term_gpas.get(student['sid'])
    benchmark('end profile transformation')
    mean_metrics = analytics.mean_metrics_across_sites(all_canvas_sites.values(), 'courseMean')
    mean_metrics['gpa'] = {}
    mean_gpas = data_loch.get_sis_section_mean_gpas(term_id, section_id)
    for row in mean_gpas:
        mean_metrics['gpa'][str(row['gpa_term_id'])] = row['avg_gpa']
    benchmark('end')
    return {
        'students': students,
        'totalStudentCount': total_student_count,
        'meanMetrics': mean_metrics,
    }


def get_distinct_sids(sids=(), cohort_ids=(), curated_group_ids=()):
    all_sids = sids
    query = text("""
        SELECT sids
        FROM cohort_filters
        WHERE id = ANY(:cohort_ids) AND owner_id = :current_user_id
    """)
    for row in db.session.execute(query, {'cohort_ids': cohort_ids, 'current_user_id': current_user.get_id()}):
        if row and row['sids']:
            all_sids.extend(row['sids'])
    query = text("""
        SELECT distinct(m.sid)
        FROM student_group_members m
        JOIN student_groups g ON g.id = m.student_group_id
        WHERE m.student_group_id = ANY(:curated_group_ids) AND g.owner_id = :current_user_id
    """)
    rows = db.session.execute(
        query,
        {
            'curated_group_ids': curated_group_ids,
            'current_user_id': current_user.get_id(),
        },
    )
    curated_group_sids = [row['sid'] for row in rows]
    all_sids.extend(curated_group_sids)
    return set(all_sids)


def get_summary_student_profiles(sids, include_historical=False, term_id=None):
    if not sids:
        return []
    benchmark = get_benchmarker('get_summary_student_profiles')
    benchmark('begin')
    # TODO It's probably more efficient to store summary profiles in the loch, rather than distilling them
    # on the fly from full profiles.
    profiles = get_full_student_profiles(sids)
    # TODO Many views require no term enrollment information other than a units count. This datum too should be
    # stored in the loch without BOAC having to crunch it.
    if not term_id:
        term_id = current_term_id()
    benchmark('begin enrollments query')
    enrollments_for_term = data_loch.get_enrollments_for_term(term_id, sids)
    benchmark('end enrollments query')
    enrollments_by_sid = {row['sid']: json.loads(row['enrollment_term']) for row in enrollments_for_term}
    benchmark('begin academic standing query')
    academic_standing = get_academic_standing_by_sid(sids)
    benchmark('end academic standing query')
    benchmark('begin term GPA query')
    term_gpas = get_term_gpas_by_sid(sids)
    benchmark('end term GPA query')

    benchmark('begin profile transformation')
    for profile in profiles:
        summarize_profile(profile, enrollments=enrollments_by_sid, academic_standing=academic_standing, term_gpas=term_gpas)
    benchmark('end')

    return profiles


def summarize_profile(profile, enrollments=None, academic_standing=None, term_gpas=None):
    # Strip SIS details to lighten the API load.
    sis_profile = profile.pop('sisProfile', None)
    if sis_profile:
        profile['academicCareerStatus'] = sis_profile.get('academicCareerStatus')
        profile['cumulativeGPA'] = sis_profile.get('cumulativeGPA')
        profile['cumulativeUnits'] = sis_profile.get('cumulativeUnits')
        profile['currentTerm'] = sis_profile.get('currentTerm')
        profile['degrees'] = sis_profile.get('degrees')
        profile['expectedGraduationTerm'] = sis_profile.get('expectedGraduationTerm')
        profile['level'] = _get_sis_level_description(sis_profile)
        profile['majors'] = _get_active_plan_descriptions(sis_profile)
        profile['matriculation'] = sis_profile.get('matriculation')
        profile['termsInAttendance'] = sis_profile.get('termsInAttendance')
        profile['transfer'] = sis_profile.get('transfer')
        if sis_profile.get('withdrawalCancel'):
            profile['withdrawalCancel'] = sis_profile['withdrawalCancel']
            if not sis_profile['withdrawalCancel'].get('termId'):
                sis_profile['withdrawalCancel']['termId'] = current_term_id()
    if enrollments:
        # Add the singleton term.
        term = enrollments.get(profile['sid'])
        if term:
            if not current_user.can_access_canvas_data:
                _suppress_canvas_sites(term)
            profile['term'] = term
    if academic_standing:
        profile['academicStanding'] = academic_standing.get(profile['sid'])
    if term_gpas:
        profile['termGpa'] = term_gpas.get(profile['sid'])


def _academic_standing_to_feed(rows):
    def _row_to_json(row):
        return {
            'actionDate': row['action_date'],
            'sid': row['sid'],
            'status': row['status'],
            'termId': str(row['term_id']),
            'termName': term_name_for_sis_id(row['term_id']),
        }
    return [_row_to_json(row) for row in rows]


def get_academic_standing_by_sid(sids, as_dicts=False):
    results = data_loch.get_academic_standing(sids)
    academic_standing_feed = {}
    for sid, rows in groupby(results, key=operator.itemgetter('sid')):
        if as_dicts:
            academic_standing_feed[sid] = {str(r['term_id']): r['status'] for r in rows}
        else:
            academic_standing_feed[sid] = _academic_standing_to_feed(rows)
    return academic_standing_feed


def get_student_and_terms_by_sid(sid):
    student = data_loch.get_student_by_sid(sid)
    if student:
        return _construct_student_profile(student)


def get_student_and_terms_by_uid(uid):
    student = data_loch.get_student_by_uid(uid)
    if student:
        return _construct_student_profile(student)


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
    entering_terms=None,
    epn_cpn_grading_terms=None,
    ethnicities=None,
    expected_grad_terms=None,
    genders=None,
    gpa_ranges=None,
    group_codes=None,
    in_intensive_cohort=None,
    include_historical=False,
    include_profiles=False,
    intended_majors=None,
    is_active_asc=None,
    is_active_coe=None,
    last_name_ranges=None,
    last_term_gpa_ranges=None,
    levels=None,
    limit=50,
    majors=None,
    midpoint_deficient_grade=None,
    minors=None,
    offset=0,
    order_by=None,
    sids=(),
    sids_only=False,
    student_holds=None,
    term_id=None,
    transfer=None,
    underrepresented=None,
    unit_ranges=None,
    visa_types=None,
):

    criteria = {
        'advisor_plan_mappings': advisor_plan_mappings,
        'coe_advisor_ldap_uids': coe_advisor_ldap_uids,
        'coe_ethnicities': coe_ethnicities,
        'coe_genders': coe_genders,
        'coe_prep_statuses': coe_prep_statuses,
        'coe_probation': coe_probation,
        'coe_underrepresented': coe_underrepresented,
        'epn_cpn_grading_terms': epn_cpn_grading_terms,
        'ethnicities': ethnicities,
        'genders': genders,
        'group_codes': group_codes,
        'in_intensive_cohort': in_intensive_cohort,
        'is_active_asc': is_active_asc,
        'is_active_coe': is_active_coe,
        'underrepresented': underrepresented,
        'visa_types': visa_types,
    }

    # Cohorts pull from all students in BOA unless they include a department-specific criterion.
    scope = scope_for_criteria(**criteria)

    query_tables, query_filter, query_bindings = data_loch.get_students_query(
        academic_standings=academic_standings,
        advisor_plan_mappings=advisor_plan_mappings,
        coe_advisor_ldap_uids=coe_advisor_ldap_uids,
        coe_ethnicities=coe_ethnicities,
        coe_genders=coe_genders,
        coe_prep_statuses=coe_prep_statuses,
        coe_probation=coe_probation,
        coe_underrepresented=coe_underrepresented,
        colleges=colleges,
        curated_group_ids=curated_group_ids,
        current_term_id=current_term_id(),
        entering_terms=entering_terms,
        epn_cpn_grading_terms=epn_cpn_grading_terms,
        ethnicities=ethnicities,
        expected_grad_terms=expected_grad_terms,
        genders=genders,
        gpa_ranges=gpa_ranges,
        group_codes=group_codes,
        in_intensive_cohort=in_intensive_cohort,
        include_historical=include_historical,
        intended_majors=intended_majors,
        is_active_asc=is_active_asc,
        is_active_coe=is_active_coe,
        last_name_ranges=last_name_ranges,
        last_term_gpa_ranges=last_term_gpa_ranges,
        levels=levels,
        majors=majors,
        midpoint_deficient_grade=midpoint_deficient_grade,
        minors=minors,
        scope=scope,
        sids=sids,
        transfer=transfer,
        underrepresented=underrepresented,
        unit_ranges=unit_ranges,
        visa_types=visa_types,
        student_holds=student_holds,
    )
    if not query_tables:
        return {
            'sids': [],
            'students': [],
            'totalStudentCount': 0,
        }    # First, get total_count of matching students
    sids_result = data_loch.safe_execute_rds(f'SELECT DISTINCT(spi.sid) {query_tables} {query_filter}', **query_bindings)
    if sids_result is None:
        return None
    # Upstream logic may require the full list of SIDs even if we're only returning full results for a particular
    # paged slice.
    summary = {
        'sids': [row['sid'] for row in sids_result],
        'totalStudentCount': len(sids_result),
    }
    if not sids_only:
        o, o_secondary, o_tertiary, o_direction, supplemental_query_tables = data_loch.get_students_ordering(
            current_term_id=current_term_id(),
            order_by=order_by,
            group_codes=group_codes,
            majors=majors,
            scope=scope,
        )
        if supplemental_query_tables:
            query_tables += supplemental_query_tables

        nulls_last = ('entering_term', 'group_name', 'term_gpa', 'terms_in_attendance', 'units')
        o_null_order = 'NULLS LAST' if any(s in o for s in nulls_last) else 'NULLS FIRST'
        sql = f"""SELECT
            spi.sid, MIN({o}), MIN({o_secondary}), MIN({o_tertiary})
            {query_tables}
            {query_filter}
            GROUP BY spi.sid
            ORDER BY MIN({o}) {o_direction} {o_null_order}, MIN({o_secondary}) NULLS FIRST, MIN({o_tertiary}) NULLS FIRST"""
        if o_tertiary != 'spi.sid':
            sql += ', spi.sid'
        sql += ' OFFSET :offset'
        query_bindings['offset'] = offset
        if limit and limit < 100:  # Sanity check large limits
            query_bindings['limit'] = limit
            sql += ' LIMIT :limit'
        students_result = data_loch.safe_execute_rds(sql, **query_bindings)
        if include_profiles:
            summary['students'] = get_summary_student_profiles([row['sid'] for row in students_result], term_id=term_id)
        else:
            summary['students'] = get_distilled_student_profiles([row['sid'] for row in students_result])
    return summary


def search_for_students(
    search_phrase=None,
    order_by=None,
    offset=0,
    limit=None,
):
    benchmark = get_benchmarker('search_for_students')
    benchmark('begin')

    query_tables, query_filter, query_bindings = data_loch.get_students_query(search_phrase=search_phrase)
    if not query_tables:
        return {
            'students': [],
            'totalStudentCount': 0,
        }
    o, o_secondary, o_tertiary, o_direction, supplemental_query_tables = data_loch.get_students_ordering(
        current_term_id=current_term_id(),
        order_by=order_by,
    )
    if supplemental_query_tables:
        query_tables += supplemental_query_tables
    benchmark('begin SID query')
    result = data_loch.safe_execute_rds(f'SELECT DISTINCT(spi.sid) {query_tables} {query_filter}', **query_bindings)
    benchmark('end SID query')
    total_student_count = len(result)

    sql = f"""SELECT
        spi.sid
        {query_tables}
        {query_filter}
        GROUP BY spi.sid
        ORDER BY MIN({o}) {o_direction} NULLS FIRST, MIN({o_secondary}) NULLS FIRST, MIN({o_tertiary}) NULLS FIRST"""
    if o_tertiary != 'spi.sid':
        sql += ', spi.sid'
    sql += f' OFFSET {offset}'
    if limit and limit < 100:  # Sanity check large limits
        sql += ' LIMIT :limit'
        query_bindings['limit'] = limit
    benchmark('begin student query')
    result = data_loch.safe_execute_rds(sql, **query_bindings)
    benchmark('begin profile collection')
    students = get_summary_student_profiles([row['sid'] for row in result])
    benchmark('end')
    return {
        'students': students,
        'totalStudentCount': total_student_count,
    }


def get_student_query_scope(user=None):
    if user is None:
        user = current_user
    # Use department membership and admin status to determine what data we can surface about which students.
    # If this code is being called outside an HTTP request context, then assume it is an administrative task.
    # Not all current_user proxy types define all attributes, and so the ordering of these conditional checks
    # is important.
    if not user:
        return ['ADMIN']
    elif hasattr(user, 'is_authenticated') and not user.is_authenticated:
        # This function can be invoked with both (1) user session object or (2) user record from the db.
        # User session object is identified by the presence of 'is_authenticated' method.
        return []
    elif user.is_admin:
        return ['ADMIN']
    elif hasattr(user, 'departments'):
        return dept_codes_where_advising(user)
    else:
        return [m.university_dept.dept_code for m in user.department_memberships]


def merge_enrollment_terms(enrollment_results, academic_standing=None):
    current_term_found = False
    filtered_enrollment_terms = []
    for row in enrollment_results:
        term = json.loads(row['enrollment_term'])
        term_id = term['termId']
        if term_id == current_term_id():
            current_term_found = True
        else:
            if term_id < current_term_id():
                # Skip past terms with no enrollments or drops.
                if not term.get('enrollments') and not term.get('droppedSections'):
                    continue
                # Filter out old waitlisted enrollments from past terms.
                if term.get('enrollments'):
                    _omit_zombie_waitlisted_enrollments(term)

        term_name = term.get('termName')
        term['academicYear'] = academic_year_for_term_name(term_name)
        if academic_standing:
            term['academicStanding'] = {
                'status': academic_standing.get(term_id),
                'termId': term_id,
            }
        if not current_user.can_access_canvas_data:
            _suppress_canvas_sites(term)
        filtered_enrollment_terms.append(term)
    if not current_term_found:
        current_term = {
            'academicYear': academic_year_for_term_name(current_term_name()),
            'enrolledUnits': 0,
            'enrollments': [],
            'termId': current_term_id(),
            'termName': current_term_name(),
        }
        filtered_enrollment_terms.append(current_term)
    return filtered_enrollment_terms


def scope_for_criteria(**kwargs):
    # Searching by department-specific criteria will constrain scope to the department in question.
    criteria_for_code = {
        'UWASC': [
            'in_intensive_cohort',
            'is_active_asc',
            'group_codes',
            'group_name',
        ],
        'COENG': [
            'is_active_coe',
            'coe_advisor_ldap_uids',
            'coe_ethnicities',
            'coe_genders',
            'coe_prep_statuses',
            'coe_probation',
            'coe_underrepresented',
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
            narrowed_scope.append(code)

    if not narrowed_scope:
        # No department-specific criteria found; our scope covers everyone.
        return ['ADMIN']
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


def _get_active_plan_descriptions(profile):
    return sorted(plan.get('description') for plan in profile.get('plans', []) if plan.get('status') == 'Active')


def _merge_photo_urls(profiles):
    def _photo_key(profile):
        return f"{app.config['DATA_LOCH_S3_PHOTO_PATH']}/{profile['uid']}.jpg"

    photo_urls = s3.get_signed_urls(
        bucket=app.config['DATA_LOCH_S3_PHOTO_BUCKET'],
        keys=[_photo_key(profile) for profile in profiles],
        expiration=app.config['PHOTO_SIGNED_URL_EXPIRES_IN_SECONDS'],
    )
    for profile in profiles:
        profile['photoUrl'] = photo_urls.get(_photo_key(profile))


def _suppress_canvas_sites(enrollment_term):
    for enrollment in enrollment_term['enrollments']:
        enrollment['canvasSites'] = []


def _construct_student_profile(student):
    if not student:
        return
    profiles = get_full_student_profiles([student['sid']])
    if not profiles or not profiles[0]:
        return
    profile = profiles[0]
    sis_profile = profile.get('sisProfile', None)
    if sis_profile and 'level' in sis_profile:
        sis_profile['level']['description'] = _get_sis_level_description(sis_profile)

    academic_standing = get_academic_standing_by_sid([student['sid']], as_dicts=False)
    if academic_standing:
        profile['academicStanding'] = academic_standing.get(student['sid'])
        academic_standing = {term['termId']: term['status'] for term in profile['academicStanding']}

    enrollment_results = data_loch.get_enrollments_for_sid(student['sid'], latest_term_id=future_term_id())
    profile['enrollmentTerms'] = merge_enrollment_terms(enrollment_results, academic_standing=academic_standing)

    if sis_profile and sis_profile.get('withdrawalCancel'):
        profile['withdrawalCancel'] = sis_profile['withdrawalCancel']
        if not sis_profile['withdrawalCancel'].get('termId'):
            sis_profile['withdrawalCancel']['termId'] = current_term_id()

    advisors = profile.get('advisors', [])
    for index, advisor in enumerate(advisors):
        if advisor.get('sid') == 'UCBUGADHAAS':
            profile['advisors'][index]['firstName'] = 'Haas Undergraduate Program'
            profile['advisors'][index]['email'] = 'UGMajorAdvising@haas.berkeley.edu'
    return profile


def _get_profiles_by_sid(profiles):
    profiles_by_sid = {}
    for row in profiles:
        profiles_by_sid[row['sid']] = {
            **json.loads(row['profile']),
            **{
                'gender': row['gender'],
                'underrepresented': row['minority'],
            },
        }
    return profiles_by_sid


def _merge_asc_student_profile_data(profile, asc_profile, scope):
    if profile:
        asc_profile = json.loads(asc_profile['profile'])
        if 'UWASC' in scope or 'ADMIN' in scope:
            profile['athleticsProfile'] = asc_profile
        else:
            # Non-ASC advisors have access to team memberships but not other ASC data such as intensive or inactive status.
            profile['athleticsProfile'] = {'athletics': asc_profile.get('athletics')}


def _merge_coe_student_profile_data(profile, coe_profile):
    if profile:
        profile['coeProfile'] = json.loads(coe_profile['profile'])
        if 'minority' in profile['coeProfile']:
            profile['coeProfile']['underrepresented'] = profile['coeProfile']['minority']
        if profile['coeProfile'].get('status') in ['D', 'P', 'U', 'W', 'X', 'Z']:
            profile['coeProfile']['isActiveCoe'] = False
        else:
            profile['coeProfile']['isActiveCoe'] = True


def _omit_zombie_waitlisted_enrollments(past_term):
    # TODO Even for current terms, it may be a mistake when SIS data sources show both active and waitlisted
    # section enrollments for a single class, but that needs confirmation.
    for course in past_term['enrollments']:
        sections = course['sections']
        if sections:
            fixed_sections = []
            for enrollment in sections:
                if enrollment.get('enrollmentStatus') != 'W':
                    fixed_sections.append(enrollment)
            if not fixed_sections:
                app.logger.warn(f'SIS provided only waitlisted enrollments in a past term: {past_term}')
            else:
                course['sections'] = fixed_sections
