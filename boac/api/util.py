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

from functools import wraps

from boac.lib.berkeley import get_dept_codes
from boac.merged import calnet
from flask import current_app as app, request
from flask_login import current_user

"""Utility module containing standard API-feed translations of data objects."""


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        auth_key = app.config['API_KEY']
        login_ok = current_user.is_authenticated and current_user.is_admin
        api_key_ok = auth_key and (request.headers.get('App-Key') == auth_key)
        if login_ok or api_key_ok:
            return func(*args, **kw)
        else:
            app.logger.warn(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_required


def add_alert_counts(alert_counts, students):
    students_by_sid = {student['sid']: student for student in students}
    for alert_count in alert_counts:
        student = students_by_sid.get(alert_count['sid'], None)
        if student:
            student.update({
                'alertCount': alert_count['alertCount'],
            })
    return students


def authorized_users_api_feed(users, sort_by='lastName'):
    if not users:
        return []
    profiles = []
    for user in users:
        profile = calnet.get_calnet_user_for_uid(app, user.uid)
        profile.update({
            'is_admin': user.is_admin,
            'departments': {},
        })
        for m in user.department_memberships:
            profile['departments'].update({
                m.university_dept.dept_code: {
                    'isAdvisor': m.is_advisor,
                    'isDirector': m.is_director,
                },
            })
        profiles.append(profile)
    return sorted(profiles, key=lambda p: p.get(sort_by) or '')


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
    return sorted(students, key=lambda s: (s['lastName'], s['firstName']))


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


def can_current_user_view_dept(dept_code):
    return current_user.is_admin or dept_code in get_dept_codes(current_user)


def is_current_user_asc_affiliated():
    return 'UWASC' in get_dept_codes(current_user)
