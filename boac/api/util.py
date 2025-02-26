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

from datetime import datetime
from functools import wraps
import json

from boac.api.errors import BadRequestError
from boac.externals import data_loch
from boac.externals.data_loch import get_admitted_students_by_sids, get_sis_holds, get_student_profiles
from boac.lib.berkeley import ACADEMIC_STANDING_DESCRIPTIONS, dept_codes_where_advising, previous_term_id, term_name_for_sis_id
from boac.lib.http import response_with_csv_download
from boac.lib.util import get_benchmarker, has_any_membership_role, join_if_present
from boac.merged import calnet
from boac.merged.advising_appointment import get_advising_appointments
from boac.merged.advising_note import get_advising_notes
from boac.merged.sis_terms import current_term_id
from boac.merged.student import get_term_gpas_by_sid, get_term_units_by_sid, merge_coe_student_profile_data
from boac.models.alert import Alert
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from boac.models.degree_progress_course import ACCENT_COLOR_CODES
from boac.models.note import Note
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.university_dept import UniversityDept
from boac.models.user_login import UserLogin
from dateutil.tz import tzutc
from flask import current_app as app, request
from flask_login import current_user


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        is_authorized = current_user.is_authenticated and current_user.is_admin
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_required


def admin_or_director_required(func):
    @wraps(func)
    def _admin_or_director_required(*args, **kw):
        is_authorized = current_user.is_authenticated and (
            current_user.is_admin
            or (current_user.is_authenticated and has_any_membership_role(current_user, 'director'))
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_or_director_required


def peer_advisor_required(func):
    @wraps(func)
    def _authorize(*args, **kw):
        if current_user.is_authenticated and (current_user.is_admin or is_peer_advisor(current_user) or _api_key_ok()):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _authorize


def advisor_or_peer_advisor_required(func):
    @wraps(func)
    def _advisor_required(*args, **kw):
        if (current_user.is_authenticated and (
            current_user.is_admin
            or has_any_membership_role(current_user, 'advisor', 'director')
            or is_peer_advisor(current_user)
            or _api_key_ok()
        )):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _advisor_required


# Checks if the peer_advisor or peer_advisor_manager is in the peer_advising_department in the URL parameter
def peer_advisor_or_peer_advisor_manager_in_department(func):
    @wraps(func)
    def _peer_advisor_or_manager_in_department(*args, **kw):
        # Extract the peer_advising_department_id from the URL params
        peer_advising_department_id = kw.get('peer_advising_department_id') or request.view_args.get(
            'peer_advising_department_id')
        if peer_advising_department_id is None:
            app.logger.error('Department ID missing in URL.')
            return app.login_manager.unauthorized()
        if (current_user.is_authenticated
                and (
                    current_user.is_admin
                    or is_peer_advisor_manager(current_user)
                    or is_peer_advisor(current_user)
                    or _api_key_ok())
                and (
                    PeerAdvisingDepartmentMember.is_user_in_peer_advising_department(
                        user_id=current_user.get_id(),
                        peer_advising_department_id=peer_advising_department_id)
                )):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _peer_advisor_or_manager_in_department


def peer_advisor_or_peer_advisor_manager(func):
    @wraps(func)
    def _peer_advisor_or_peer_advisor_manager(*args, **kw):
        if current_user.is_authenticated and (
                current_user.is_admin
                or is_peer_advisor_manager(current_user)
                or is_peer_advisor(current_user)
                or _api_key_ok()
        ):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _peer_advisor_or_peer_advisor_manager


def peer_advisor_manager_required(func):
    @wraps(func)
    def _advisor_required(*args, **kw):
        if (
            current_user.is_authenticated
            and (
                current_user.is_admin
                or is_peer_advisor_manager(current_user)
                or _api_key_ok()
            )
        ):
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _advisor_required


def advising_data_access_required(func):
    @wraps(func)
    def _advising_data_access_required(*args, **kw):
        is_authorized = (
            current_user.is_authenticated
            and current_user.can_access_advising_data
            and (current_user.is_admin or has_any_membership_role(current_user, 'advisor', 'director'))
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _advising_data_access_required


def advisor_required(func):
    @wraps(func)
    def _advisor_required(*args, **kw):
        if current_user.is_admin or has_any_membership_role(current_user, 'advisor', 'director') or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _advisor_required


def can_access_admitted_students(user):
    return user.is_authenticated and (current_user.is_admin or _is_advisor_in_department(current_user, 'ZCEEE'))


def ce3_required(func):
    @wraps(func)
    def _ce3_required(*args, **kw):
        is_authorized = can_access_admitted_students(current_user)
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _ce3_required


def can_edit_degree_progress(func):
    @wraps(func)
    def _qualifies(*args, **kw):
        if (current_user.is_authenticated and current_user.can_edit_degree_progress) or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _qualifies


def can_read_degree_progress(func):
    @wraps(func)
    def _qualifies(*args, **kw):
        if (current_user.is_authenticated and current_user.can_read_degree_progress) or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _qualifies


def director_advising_data_access_required(func):
    @wraps(func)
    def _director_advising_data_access_required(*args, **kw):
        is_authorized = (
            current_user.is_authenticated
            and current_user.can_access_advising_data
            and (current_user.is_admin or has_any_membership_role(current_user, 'director'))
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _director_advising_data_access_required


def normalize_accent_color(color):
    if color:
        capitalized = color.capitalize()
        return capitalized if capitalized in list(ACCENT_COLOR_CODES.keys()) else None


def add_alert_counts(alert_counts, students):
    students_by_sid = {student['sid']: student for student in students}
    for alert_count in alert_counts:
        student = students_by_sid.get(alert_count['sid'], None)
        if student:
            student.update({
                'alertCount': alert_count['alertCount'],
            })
    return students


def authorized_users_api_feed(users, sort_by='lastName', sort_descending=False):
    if not users:
        return ()
    calnet_users = calnet.get_calnet_users_for_uids(app, [u.uid for u in users])
    profiles = []
    for user in users:
        profile = calnet_users[user.uid]
        if not profile:
            continue
        if not profile.get('name'):
            profile['name'] = ((profile.get('firstName') or '') + ' ' + (profile.get('lastName') or '')).strip()

        profile.update({
            'id': user.id,
            'automateDegreeProgressPermission': user.automate_degree_progress_permission,
            'canAccessAdvisingData': user.can_access_advising_data,
            'canAccessCanvasData': user.can_access_canvas_data,
            'canEditDegreeProgress': user.degree_progress_permission == 'read_write' or user.is_admin,
            'canReadDegreeProgress': user.degree_progress_permission in ['read', 'read_write'] or user.is_admin,
            'createdAt': _isoformat(user.created_at),
            'degreeProgressPermission': user.degree_progress_permission,
            'deletedAt': _isoformat(user.deleted_at),
            'departments': [],
            'isAdmin': user.is_admin,
            'isBlocked': user.is_blocked,
        })
        for m in user.department_memberships:
            profile['departments'].append({
                **m.university_dept.to_api_json(),
                'memberships': [
                    {
                        'automateMembership': m.automate_membership,
                        'role': m.role,
                    },
                ],
            })
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(
            authorized_user_id=user.id,
        )
        for m in memberships:
            peer_advising_dept_membership = {
                'role': m['role_type'],
                'peerAdvisingDepartmentId': m['peer_advising_department_id'],
                'peerAdvisingDepartmentName': m['peer_advising_department_name'],
            }
            university_dept_id = m['university_dept_id']
            university_dept_api_json = next((d for d in profile['departments'] if d['id'] == university_dept_id), None)
            if university_dept_api_json:
                # If the university_dept was added in the 'for user.department_memberships' loop above
                # then we append the peer_advising membership to the existing object.
                university_dept_api_json['memberships'].append(peer_advising_dept_membership)
            else:
                profile['departments'].append({
                    **UniversityDept.find_by_id(university_dept_id).to_api_json(),
                    'memberships': [peer_advising_dept_membership],
                })
        user_login = UserLogin.last_login(user.uid)
        profile['lastLogin'] = _isoformat(user_login.created_at) if user_login else None
        profiles.append(profile)
    return sorted(profiles, key=lambda p: (p.get(sort_by) is None, p.get(sort_by)), reverse=sort_descending)


def put_notifications(student):
    sid = student['sid']
    student['notifications'] = {
        'alert': [],
        'hold': [],
        'requirement': [],
    }
    if current_user.can_access_advising_data:
        student['notifications']['appointment'] = []
        student['notifications']['eForm'] = []
        student['notifications']['note'] = []
        for appointment in get_advising_appointments(sid) or []:
            message = appointment['details']
            student['notifications']['appointment'].append({
                **appointment,
                **{
                    'message': message.strip() if message else None,
                    'type': 'appointment',
                },
            })

        # The front-end requires 'type', 'message' and 'read'. Optional fields: id, status, createdAt, updatedAt.
        for note in get_advising_notes(sid) or []:
            message = note['body']
            note_type = 'eForm' if note.get('eForm') else 'note'
            student['notifications'][note_type].append({
                **note,
                **{
                    'message': message.strip() if message else None,
                    'type': note_type,
                },
            })
    for alert in Alert.current_alerts_for_sid(viewer_id=current_user.get_id(), sid=sid):
        student['notifications']['alert'].append({
            **alert,
            **{
                'id': alert['id'],
                'read': alert['dismissed'],
                'type': 'alert',
            },
        })
    for row in get_sis_holds(sid):
        hold = json.loads(row['feed'])
        reason = hold.get('reason', {})
        student['notifications']['hold'].append({
            **hold,
            **{
                'createdAt': hold.get('fromDate'),
                'message': join_if_present('. ', [reason.get('description'), reason.get('formalDescription')]),
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


def get_current_user_profile():
    cohorts = []
    user_id = current_user.get_id()
    for cohort in CohortFilter.get_cohorts(user_id):
        cohort['isOwnedByCurrentUser'] = True
        cohorts.append(cohort)
    return {
        **current_user.to_api_json(),
        'myCohorts': cohorts,
        'myCuratedGroups': get_my_curated_groups(),
        'myDraftNoteCount': Note.get_draft_note_count(None if current_user.is_admin else current_user.uid),
        'preferences': {
            'admitSortBy': 'last_name',
            'sortBy': 'last_name',
            'termId': current_term_id(),
        },
    }


def get_note_attachments_from_http_post(tolerate_none=False):
    request_files = request.files
    attachments = []
    for index in range(app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE']):
        attachment = request_files.get(f'attachment[{index}]')
        if attachment:
            attachments.append(attachment)
        else:
            break
    if not tolerate_none and not len(attachments):
        raise BadRequestError('request.files is empty')
    byte_stream_bundle = []
    for attachment in attachments:
        filename = attachment.filename and attachment.filename.strip()
        if not filename:
            raise BadRequestError(f'Invalid file in request form data: {attachment}')
        else:
            byte_stream_bundle.append({
                'name': filename.rsplit('/', 1)[-1],
                'byte_stream': attachment.read(),
            })
    return byte_stream_bundle


def get_template_attachment_ids_from_http_post():
    ids = request.form.get('templateAttachmentIds', [])
    return ids if isinstance(ids, list) else list(filter(None, str(ids).split(',')))


def get_note_topics_from_http_post():
    topics = request.form.get('topics', [])
    return topics if isinstance(topics, list) else list(filter(None, str(topics).split(',')))


def get_my_curated_groups():
    benchmark = get_benchmarker('my_curated_groups')
    curated_groups = []
    user_id = current_user.get_id()
    for curated_group in CuratedGroup.get_curated_groups(owner_id=user_id):
        students = [{'sid': sid} for sid in CuratedGroup.get_all_sids(curated_group.id)]
        students_with_alerts = Alert.include_alert_counts_for_students(
            benchmark=benchmark,
            viewer_user_id=user_id,
            group={'students': students},
            count_only=True,
        )
        curated_groups.append({
            **curated_group.to_api_json(include_students=False),
            'alertCount': sum(s['alertCount'] for s in students_with_alerts),
            'sids': [student['sid'] for student in students],
            'totalStudentCount': len(students),
        })
    return curated_groups


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


def is_peer_advisor(user):
    return has_any_membership_role(user, 'peer_advisor')


def is_peer_advisor_manager(user):
    return has_any_membership_role(user, 'peer_advisor_manager')


def is_unauthorized_domain(domain):
    if domain not in ['default', 'admitted_students']:
        raise BadRequestError(f'Invalid domain: {domain}')
    return (domain == 'admitted_students'
            and not current_user.is_admin
            and 'ZCEEE' not in dept_codes_where_advising(current_user.departments))


def is_unauthorized_search(filter_keys, order_by=None):
    filter_key_set = set(filter_keys)
    asc_keys = {'inIntensiveCohort', 'isInactiveAsc', 'groupCodes'}
    if list(filter_key_set & asc_keys) or order_by in ['group_name']:
        if not current_user.is_admin and 'UWASC' not in dept_codes_where_advising(current_user.departments):
            return True
    coe_keys = {
        'coeAcademicStandings',
        'coeAdvisorLdapUids',
        'coeEthnicities',
        'coePrepStatuses',
        'coeUnderrepresented',
        'isInactiveCoe',
    }
    if list(filter_key_set & coe_keys):
        if not current_user.is_admin and 'COENG' not in dept_codes_where_advising(current_user.departments):
            return True
    return False


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


def validate_advising_note_set_date(params):
    set_date = params.get('setDate') or None
    if set_date:
        try:
            datetime.strptime(set_date, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            raise BadRequestError('Invalid set date format')
    return set_date


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
        'academic_standing': lambda profile: _get_academic_standing(profile),
        'cohorts': lambda profile: '; '.join(_get_current_user_cohorts_containing(profile, cohorts)),
        'college_advisor': lambda profile: '; '.join(_get_college_advisors(profile)),
        'cumulative_gpa': lambda profile: profile.get('sisProfile', {}).get('cumulativeGPA'),
        'curated_groups': lambda profile: '; '.join(_get_current_user_curated_groups_containing(profile, curated_groups)),
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
        getters['coe_status'] = lambda profile: _get_coe_status(profile) or ''
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


def _api_key_ok():
    auth_key = app.config['API_KEY']
    return auth_key and (request.headers.get('App-Key') == auth_key)


def _get_academic_standing(profile):
    academic_standing = profile.get('sisProfile', {}).get('academicStanding', {})
    status = academic_standing.get('status')
    if status:
        term_name = academic_standing.get('termName')
        status_name = ACADEMIC_STANDING_DESCRIPTIONS.get(status, status)
        return f"{status_name}{f', {term_name}' if term_name else ''}"
    else:
        return ''


def _get_coe_status(profile):
    status = None
    if profile.get('coeProfile'):
        status = 'active' if profile.get('coeProfile').get('isActiveCoe') else 'inactive'
    return status


def _get_college_advisors(profile):
    values = []
    for advisor in profile.get('advisors', []):
        last_name = advisor['lastName']
        uid = advisor['uid']
        if advisor.get('role', '').lower() == 'college advisor' and (last_name or uid):
            advisor_name = f"{advisor['firstName']} {last_name}" if last_name else f'UID:{uid}'
            values.append(advisor_name)
    return values


def _get_current_user_cohorts_containing(profile, cohorts):
    sid = profile['sid']
    return [cohort['name'] for cohort in cohorts if sid in cohort['sids']]


def _get_current_user_curated_groups_containing(profile, curated_groups):
    sid = profile['sid']
    return [curated_group['name'] for curated_group in curated_groups if sid in curated_group['sids']]


def _is_advisor_in_department(user, dept_code):
    is_advisor_in_department = False
    is_dict = isinstance(user, dict)
    is_authenticated = user['isAuthenticated'] if is_dict else user.is_authenticated
    departments = user['departments'] if is_dict else user.departments
    if is_authenticated:
        for department in departments:
            if dept_code == department['deptCode'] and next((m for m in department['memberships'] if m['role'] in ('advisor', 'director')), False):
                is_advisor_in_department = True
                break
    return is_advisor_in_department


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()


def _norm(row, key):
    value = row.get(key)
    return value and value.upper()
