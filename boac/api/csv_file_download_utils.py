"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.decorators import ce3_required
from boac.api.util import get_academic_standing, get_coe_status, get_college_advisors, \
    get_current_user_cohorts_containing, get_current_user_curated_groups_containing
from boac.externals import data_loch
from boac.externals.data_loch import get_admitted_students_by_sids, get_student_profiles
from boac.lib.berkeley import dept_codes_where_advising, previous_term_id, term_name_for_sis_id
from boac.lib.http import response_with_csv_download
from boac.merged.sis_terms import current_term_id
from boac.merged.student import get_term_gpas_by_sid, get_term_units_by_sid, merge_coe_student_profile_data
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from flask_login import current_user


def get_students_csv_header_labels(term_id):
    term_id_last = previous_term_id(term_id)
    term_id_previous = previous_term_id(term_id_last)
    return {
        'academic_standing': 'Academic Standing',
        'coe_status': 'CoE status',
        'cohorts': 'Cohorts',
        'college_advisor': 'College Advisor',
        'course_activity': 'Course Activity',
        'cumulative_gpa': 'Cumulative GPA',
        'curated_groups': 'Curated Groups',
        'email': 'Email Address',
        'expected_graduation_term': 'Expected Graduation Term',
        'first_name': 'First Name',
        'intended_major': 'Intended Major',
        'intended_majors': 'Intended Majors',
        'last_name': 'Last Name',
        'level_by_units': 'Level by Units',
        'majors': 'Major(s)',
        'minors': 'Minor(s)',
        'phone': 'Phone Number',
        'program_status': 'Program Status',
        'sid': 'SID',
        'subplans': 'Academic Subplans',
        f'term_gpa_{term_id_last}': f'{term_name_for_sis_id(term_id_last)} Term GPA',
        f'term_gpa_{term_id_previous}': f'{term_name_for_sis_id(term_id_previous)} Term GPA',
        'terms_in_attendance': 'Terms in Attendance',
        'transfer': 'Transfer Status',
        'units_completed': 'Units Completed',
        'units_in_progress': 'Units in Progress',
    }


def response_with_students_csv_download(benchmark, domain, fieldnames, sids, term_id):
    if domain == 'admitted_students':
        return _response_with_admits_csv_download(
            benchmark=benchmark,
            fieldnames=fieldnames,
            sids=sids,
        )
    else:
        return _response_with_students_csv_download(
            benchmark=benchmark,
            fieldnames=fieldnames,
            sids=sids,
            term_id=term_id,
        )


def _norm(row, key):
    value = row.get(key)
    return value and value.upper()


@ce3_required
def _response_with_admits_csv_download(sids, fieldnames, benchmark):
    key_aliases = {
        'cs_empl_id': 'sid',
    }

    def _row_for_csv(result):
        return {f: result.get(key_aliases.get(f, f)) for f in fieldnames}
    rows = [_row_for_csv(student) for student in get_admitted_students_by_sids(offset=0, sids=sids)]
    benchmark('end')

    return response_with_csv_download(
        rows=sorted(rows, key=lambda r: (_norm(r, 'last_name'), _norm(r, 'first_name'), _norm(r, 'cs_empl_id'))),
        filename_prefix='cohort',
        fieldnames=fieldnames,
    )


def _response_with_students_csv_download(sids, fieldnames, benchmark, term_id):
    term_id_last = previous_term_id(current_term_id())
    term_id_previous = previous_term_id(term_id_last)
    # The 'course_activity' option aliases a set of CSV columns: course_name, units, etc.
    is_requesting_course_activity = 'course_activity' in fieldnames
    if is_requesting_course_activity:
        # Remove 'course_activity' from fieldnames because it will not be a column name in CSV. The course-related
        # columns are added farther down in the code.
        fieldnames.remove('course_activity')

    getters = {
        'academic_standing': lambda profile: get_academic_standing(profile),
        'cohorts': lambda profile: '; '.join(get_current_user_cohorts_containing(profile, cohorts)),
        'college_advisor': lambda profile: '; '.join(get_college_advisors(profile)),
        'cumulative_gpa': lambda profile: profile.get('sisProfile', {}).get('cumulativeGPA'),
        'curated_groups': lambda profile: '; '.join(get_current_user_curated_groups_containing(profile, curated_groups)),
        'email': lambda profile: profile.get('sisProfile', {}).get('emailAddress'),
        'expected_graduation_term': lambda profile: profile.get('sisProfile', {}).get('expectedGraduationTerm', {}).get('name'),
        'first_name': lambda profile: profile.get('firstName'),
        'intended_major': lambda profile: '; '.join(
            [major.get('description') for major in (profile.get('sisProfile', {}).get('intendedMajors') or [])],
        ),
        'intended_majors': lambda profile: '; '.join([major.get('description') for major in profile.get('sisProfile', {}).get('intendedMajors')]),
        'last_name': lambda profile: profile.get('lastName'),
        'level_by_units': lambda profile: profile.get('sisProfile', {}).get('level', {}).get('description'),
        'majors': lambda profile: '; '.join(
            [plan.get('description') for plan in profile.get('sisProfile', {}).get('plans', []) if plan.get('status') == 'Active'],
        ),
        'minors': lambda profile: '; '.join(
            [plan.get('description') for plan in profile.get('sisProfile', {}).get('plansMinor', []) if plan.get('status') == 'Active'],
        ),
        'phone': lambda profile: profile.get('sisProfile', {}).get('phoneNumber'),
        'program_status': lambda profile: '; '.join(list(set([plan.get('status') for plan in profile.get('sisProfile', {}).get('plans', [])]))),
        'sid': lambda profile: profile.get('sid'),
        'subplans': lambda profile: '; '.join(
            [plan['subplan'] for plan in profile.get('sisProfile', {}).get('plans', []) if plan.get('subplan') and plan.get('status') == 'Active'],
        ),
        f'term_gpa_{term_id_last}': lambda profile: profile.get('termGpa', {}).get(term_id_last),
        f'term_gpa_{term_id_previous}': lambda profile: profile.get('termGpa', {}).get(term_id_previous),
        'terms_in_attendance': lambda profile: profile.get('sisProfile', {}).get('termsInAttendance'),
        'transfer': lambda profile: 'Yes' if profile.get('sisProfile', {}).get('transfer') else '',
        'units_completed': lambda profile: profile.get('sisProfile', {}).get('cumulativeUnits'),
        'units_in_progress': lambda profile: profile.get('enrolledUnits', {}),
    }

    def _construct_csv_row():
        return dict((fieldname, getters[fieldname](profile)) for fieldname in fieldnames)
    if current_user.is_admin or 'COENG' in dept_codes_where_advising(current_user.departments):
        # Only admins and CoE advisors can access CoE-related data.
        getters['coe_status'] = lambda profile: get_coe_status(profile) or ''
    term_gpas = get_term_gpas_by_sid(sids)
    term_units = get_term_units_by_sid(term_id, sids)

    students = [{'sid': s['sid'], 'profile': json.loads(s['profile'])} for s in get_student_profiles(sids=sids)]
    if 'coe_status' in fieldnames:
        # We are going to need CoE-related data.
        profiles_by_sid = dict((student['sid'], student.get('profile')) for student in students)
        merge_coe_student_profile_data(profiles_by_sid)
    if 'cohorts' in fieldnames:
        # We are going to need cohorts.
        cohorts = CohortFilter.get_cohorts(user_id=current_user.get_id())
    if 'curated_groups' in fieldnames:
        # We are going to need curated_groups.
        curated_groups = CuratedGroup.get_curated_groups_owned_by(uids=[current_user.uid])
    if is_requesting_course_activity:
        # We are going to need enrollment data.
        enrollments_for_term = data_loch.get_enrollments_for_term(term_id, sids)
        enrollments_for_term_by_sid = dict((enrollments['sid'], json.loads(enrollments['enrollment_term'])) for enrollments in enrollments_for_term)
    rows = []
    for student in students:
        profile = student.get('profile')
        sid = profile['sid']
        profile['termGpa'] = term_gpas.get(sid, {})
        profile['enrolledUnits'] = term_units.get(sid, '0')
        if is_requesting_course_activity and sid in enrollments_for_term_by_sid:
            enrollments_for_term = enrollments_for_term_by_sid[sid]
            for enrollment in enrollments_for_term['enrollments']:
                is_waitlisted = next((u for u in enrollment.get('sections', []) if u.get('enrollmentStatus') == 'W'), False)
                rows.append({
                    **_construct_csv_row(),
                    **{
                        'Class Name': f"{enrollment['displayName']}{' (waitlisted)' if is_waitlisted else ''}",
                        'Units': enrollment['units'],
                        'Mid-point Grade': enrollment.get('midtermGrade'),
                        'Final Grade': enrollment['grade'] or enrollment['gradingBasis'],
                    },
                })
        elif len(fieldnames):
            rows.append(_construct_csv_row())

    benchmark('end')
    header_label_lookup = get_students_csv_header_labels(current_term_id())
    if is_requesting_course_activity:
        fieldnames.extend(['Class Name', 'Units', 'Mid-point Grade', 'Final Grade'])
    return response_with_csv_download(
        rows=sorted(rows, key=lambda r: (_norm(r, 'last_name'), _norm(r, 'first_name'), _norm(r, 'sid'))),
        filename_prefix='cohort',
        fieldnames=fieldnames,
        header_label_lookup=header_label_lookup,
    )
