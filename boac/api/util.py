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
from boac.lib import util
from boac.models.alert import Alert
from boac.models.athletics import Athletics
from boac.models.authorized_user import AuthorizedUser
from boac.models.student import Student

"""Utility module containing standard API-feed translations of data objects."""


def add_alert_counts(alert_counts, students):
    students_by_sid = {student['sid']: student for student in students}
    for alert_count in alert_counts:
        student = students_by_sid.get(alert_count['sid'], None)
        if student:
            student.update({
                'alertCount': alert_count['alertCount'],
            })
    return students


def canvas_course_api_feed(course):
    return {
        'canvasCourseId': course.get('canvas_course_id'),
        'courseName': course.get('canvas_course_name'),
        'courseCode': course.get('canvas_course_code'),
        'courseTerm': course.get('canvas_course_term'),
    }


def canvas_courses_api_feed(courses):
    if not courses:
        return []
    return [canvas_course_api_feed(course) for course in courses]


def sis_enrollment_class_feed(enrollment):
    return {
        'displayName': enrollment['sis_course_name'],
        'title': enrollment['sis_course_title'],
        'canvasSites': [],
        'sections': [],
    }


def sis_enrollment_section_feed(enrollment):
    section_data = enrollment.get('classSection', {})
    grades = enrollment.get('grades', [])
    grading_basis = enrollment.get('gradingBasis', {}).get('code')
    return {
        'ccn': section_data.get('id'),
        'component': section_data.get('component', {}).get('code'),
        'sectionNumber': section_data.get('number'),
        'enrollmentStatus': enrollment.get('enrollmentStatus', {}).get('status', {}).get('code'),
        'units': enrollment.get('enrolledUnits', {}).get('taken'),
        'gradingBasis': translate_grading_basis(grading_basis),
        'grade': next((grade.get('mark') for grade in grades if grade.get('type', {}).get('code') == 'OFFL'), None),
        'midtermGrade': next((grade.get('mark') for grade in grades if grade.get('type', {}).get('code') == 'MID'), None),
        'primary': False if grading_basis == 'NON' else True,
    }


def sort_students_by_name(students):
    students = sorted(students, key=lambda s: (s['firstName'], s['lastName']))
    return students


def strip_analytics(student_term_data):
    if student_term_data.get('analytics'):
        del student_term_data['analytics']
    # The enrolled units count is the one piece of term data we want to preserve.
    if student_term_data.get('term'):
        student_term_data['term'] = {'enrolledUnits': student_term_data['term'].get('enrolledUnits')}
    return student_term_data


def translate_grading_basis(code):
    bases = {
        'CNC': 'C/NC',
        'EPN': 'P/NP',
        'ESU': 'S/U',
        'GRD': 'Letter',
        'LAW': 'Law',
        'PNP': 'P/NP',
        'SUS': 'S/U',
    }
    return bases.get(code) or code


def is_read_only_cohort(cohort):
    criteria = cohort if isinstance(cohort.filter_criteria, dict) else json.loads(cohort.filter_criteria)
    keys_with_not_none_value = [key for key, value in criteria.items() if value not in [None, []]]
    return keys_with_not_none_value == ['coeAdvisorUid']


def decorate_cohort(cohort, order_by=None, offset=0, limit=50, include_students=True, include_alerts_for_uid=None):
    decorated = {
        'id': cohort.id,
        'code': cohort.id,
        'isReadOnly': is_read_only_cohort(cohort),
        'label': cohort.label,
        'name': cohort.label,
        'owners': [user.uid for user in cohort.owners],
    }
    criteria = cohort if isinstance(cohort.filter_criteria, dict) else json.loads(cohort.filter_criteria)
    gpa_ranges = util.get(criteria, 'gpaRanges', [])
    group_codes = util.get(criteria, 'groupCodes', [])
    levels = util.get(criteria, 'levels', [])
    majors = util.get(criteria, 'majors', [])
    unit_ranges = util.get(criteria, 'unitRanges', [])
    in_intensive_cohort = util.to_bool_or_none(util.get(criteria, 'inIntensiveCohort'))
    is_inactive_asc = util.get(criteria, 'isInactiveAsc')
    results = Student.get_students(
        gpa_ranges=gpa_ranges,
        group_codes=group_codes,
        in_intensive_cohort=in_intensive_cohort,
        is_active_asc=None if is_inactive_asc is None else not is_inactive_asc,
        levels=levels,
        majors=majors,
        unit_ranges=unit_ranges,
        order_by=order_by,
        offset=offset,
        limit=limit,
        sids_only=not include_students,
    )
    team_groups = Athletics.get_team_groups(group_codes) if group_codes else []

    decorated.update({
        'filterCriteria': {
            'gpaRanges': gpa_ranges,
            'groupCodes': group_codes,
            'levels': levels,
            'majors': majors,
            'unitRanges': unit_ranges,
            'inIntensiveCohort': in_intensive_cohort,
            'isInactiveAsc': is_inactive_asc,
        },
        'teamGroups': team_groups,
        'totalStudentCount': results['totalStudentCount'],
    })
    if include_students:
        decorated.update({
            'students': results['students'],
        })
    if include_alerts_for_uid:
        viewer = AuthorizedUser.find_by_uid(include_alerts_for_uid)
        if viewer:
            alert_counts = Alert.current_alert_counts_for_sids(viewer.id, results['sids'])
            decorated.update({
                'alerts': alert_counts,
            })
    return decorated
