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

from functools import wraps
import json

from boac.api.errors import ResourceNotFoundError
from boac.externals.data_loch import get_sis_holds
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, get_dept_codes
from boac.merged import calnet
from boac.merged.advising_note import get_advising_notes
from boac.models.alert import Alert
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
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
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_required


def feature_flag_edit_notes(func):
    @wraps(func)
    def _feature_flag_edit_notes(*args, **kw):
        if app.config['FEATURE_FLAG_EDIT_NOTES']:
            return func(*args, **kw)
        else:
            raise ResourceNotFoundError('API path not found')
    return _feature_flag_edit_notes


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
        return ()
    profiles = []
    for user in users:
        profile = calnet.get_calnet_user_for_uid(app, user.uid, force_feed=False)
        if not profile:
            continue
        profile['name'] = ((profile.get('firstName') or '') + ' ' + (profile.get('lastName') or '')).strip()
        profile.update({
            'id': user.id,
            'isAdmin': user.is_admin,
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


def current_user_profile():
    profile = get_current_user_status()
    if current_user.is_authenticated:
        profile['id'] = current_user.id
        uid = current_user.get_id()
        profile.update(calnet.get_calnet_user_for_uid(app, uid))
        if current_user.is_active:
            departments = []
            for m in current_user.department_memberships:
                dept_code = m.university_dept.dept_code
                departments.append(
                    {
                        'code': dept_code,
                        'name': BERKELEY_DEPT_CODE_TO_NAME[dept_code] or dept_code,
                        'role': get_dept_role(m),
                        'isAdvisor': m.is_advisor,
                        'isDirector': m.is_director,
                    })
            dept_codes = get_dept_codes(current_user)
            profile['isAsc'] = 'UWASC' in dept_codes
            profile['canViewAsc'] = profile['isAsc'] or current_user.is_admin
            profile['isCoe'] = 'COENG' in dept_codes
            profile['canViewCoe'] = profile['isCoe'] or current_user.is_admin
            profile.update({
                'isAdmin': current_user.is_admin,
                'inDemoMode': current_user.in_demo_mode if hasattr(current_user, 'in_demo_mode') else False,
                'departments': departments,
            })
    return profile


def get_dept_role(department_membership):
    return 'Director' if department_membership.is_director else ('Advisor' if department_membership.is_advisor else None)


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


def put_notifications(student):
    student['notifications'] = {
        'note': [],
        'alert': [],
        'hold': [],
        'requirement': [],
    }
    # The front-end requires 'type', 'message' and 'read'. Optional fields: id, status, createdAt, updatedAt.
    for note in get_advising_notes(student['sid']) or []:
        message = note['body']
        student['notifications']['note'].append({
            **note,
            **{
                'message': message.strip() if message else None,
                'type': 'note',
            },
        })
    for alert in Alert.current_alerts_for_sid(viewer_id=current_user.id, sid=student['sid']):
        student['notifications']['alert'].append({
            **alert,
            **{
                'id': alert['id'],
                'read': alert['dismissed'],
                'type': 'alert',
            },
        })
    for row in get_sis_holds(student['sid']):
        hold = json.loads(row['feed'])
        reason = hold.get('reason', {})
        student['notifications']['hold'].append({
            **hold,
            **{
                'createdAt': hold.get('fromDate'),
                'message': reason.get('description') + '. ' + reason.get('formalDescription'),
                'read': True,
                'type': 'hold',
            },
        })
    degree_progress = student.get('sisProfile', {}).get('degreeProgress', {})
    if degree_progress:
        for key, requirement in degree_progress.get('requirements', {}).items():
            student['notifications']['requirement'].append({
                **requirement,
                **{
                    'type': 'requirement',
                    'message': requirement['name'] + ' ' + requirement['status'],
                    'read': True,
                },
            })


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


def get_current_user_status():
    return {
        'isActive': current_user.is_active,
        'isAdmin': current_user.is_admin if hasattr(current_user, 'is_admin') else False,
        'isAnonymous': current_user.is_anonymous,
        'isAuthenticated': current_user.is_authenticated,
        # TODO: remove the following line; 'inDemoMode' is served by /api/profile/my
        'inDemoMode': current_user.in_demo_mode if hasattr(current_user, 'in_demo_mode') else False,
        'uid': current_user.get_id(),
    }


def get_my_curated_groups():
    curated_groups = []
    user_id = current_user.id
    for curated_group in CuratedGroup.get_curated_groups_by_owner_id(user_id):
        api_json = curated_group.to_api_json()
        students = [{'sid': sid} for sid in CuratedGroup.get_all_sids(curated_group.id)]
        students_with_alerts = Alert.include_alert_counts_for_students(
            viewer_user_id=user_id,
            group={'students': students},
        )
        api_json['alertCount'] = sum(s['alertCount'] for s in students_with_alerts)
        curated_groups.append(api_json)
    return curated_groups


def get_my_cohorts():
    uid = current_user.get_id()
    cohorts = []
    for cohort in CohortFilter.summarize_alert_counts_in_all_owned_by(uid):
        cohort['isOwnedByCurrentUser'] = True
        cohorts.append(cohort)
    return cohorts


def is_asc_authorized():
    return current_user.is_admin or 'UWASC' in get_dept_codes(current_user)


def is_coe_authorized():
    return current_user.is_admin or 'COENG' in get_dept_codes(current_user)


def is_unauthorized_search(filter_keys, order_by):
    filter_key_set = set(filter_keys)
    asc_keys = {'inIntensiveCohort', 'isInactiveAsc', 'groupCodes'}
    if list(filter_key_set & asc_keys) or order_by in ['group_name']:
        if not is_asc_authorized():
            return True
    coe_keys = {'advisorLdapUids', 'coePrepStatuses', 'coeProbation', 'ethnicities', 'genders', 'isInactiveCoe'}
    if list(filter_key_set & coe_keys):
        if not is_coe_authorized():
            return True
    return False
