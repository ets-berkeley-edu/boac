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

from functools import wraps
import json

from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.externals.data_loch import get_admitted_students_by_sids, get_sis_holds, get_student_profiles
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.http import response_with_csv_download
from boac.lib.util import join_if_present
from boac.merged import calnet
from boac.merged.advising_appointment import get_advising_appointments
from boac.merged.advising_note import get_advising_notes
from boac.merged.student import get_academic_standing_by_sid, get_historical_student_profiles, get_term_gpas_by_sid
from boac.models.alert import Alert
from boac.models.authorized_user_extension import DropInAdvisor
from boac.models.curated_group import CuratedGroup
from boac.models.user_login import UserLogin
from dateutil.tz import tzutc
from flask import current_app as app, request
from flask_login import current_user

"""Utility module containing standard API-feed translations of data objects."""


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
        is_authorized = current_user.is_authenticated \
            and (
                current_user.is_admin
                or _has_role_in_any_department(current_user, 'director')
            )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_or_director_required


def advising_data_access_required(func):
    @wraps(func)
    def _advising_data_access_required(*args, **kw):
        is_authorized = (
            current_user.is_authenticated
            and current_user.can_access_advising_data
            and (
                current_user.is_admin
                or _has_role_in_any_department(current_user, 'advisor')
                or _has_role_in_any_department(current_user, 'director')
            )
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
        is_authorized = current_user.is_authenticated \
            and (
                current_user.is_admin
                or _has_role_in_any_department(current_user, 'advisor')
                or _has_role_in_any_department(current_user, 'director')
            )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _advisor_required


def ce3_required(func):
    @wraps(func)
    def _ce3_required(*args, **kw):
        is_authorized = app.config['FEATURE_FLAG_ADMITTED_STUDENTS'] and current_user.is_authenticated \
            and (
                current_user.is_admin
                or _is_advisor_in_department(current_user, 'ZCEEE')
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _ce3_required


def director_advising_data_access_required(func):
    @wraps(func)
    def _director_advising_data_access_required(*args, **kw):
        is_authorized = (
            current_user.is_authenticated
            and current_user.can_access_advising_data
            and (
                current_user.is_admin
                or _has_role_in_any_department(current_user, 'director')
            )
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _director_advising_data_access_required


def drop_in_required(func):
    @wraps(func)
    def _drop_in_required(*args, **kw):
        is_authorized = (
            current_user.is_authenticated
            and current_user.can_access_advising_data
            and (
                current_user.is_admin or _is_drop_in_enabled(current_user)
            )
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _drop_in_required


def scheduler_required(func):
    @wraps(func)
    def _scheduler_required(*args, **kw):
        is_authorized = (
            current_user.is_authenticated
            and current_user.can_access_advising_data
            and (
                current_user.is_admin
                or _is_drop_in_advisor(current_user)
                or _is_drop_in_scheduler(current_user)
                or _is_same_day_scheduler(current_user)
            )
        )
        if is_authorized or _api_key_ok():
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _scheduler_required


def add_alert_counts(alert_counts, students):
    students_by_sid = {student['sid']: student for student in students}
    for alert_count in alert_counts:
        student = students_by_sid.get(alert_count['sid'], None)
        if student:
            student.update({
                'alertCount': alert_count['alertCount'],
            })
    return students


def authorized_users_api_feed(users, sort_by=None, sort_descending=False):
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
            'isAdmin': user.is_admin,
            'isBlocked': user.is_blocked,
            'canAccessAdvisingData': user.can_access_advising_data,
            'canAccessCanvasData': user.can_access_canvas_data,
            'deletedAt': _isoformat(user.deleted_at),
            'departments': [],
        })
        for m in user.department_memberships:
            profile['departments'].append({
                'code': m.university_dept.dept_code,
                'name': m.university_dept.dept_name,
                'role': m.role,
                'automateMembership': m.automate_membership,
            })
        profile['dropInAdvisorStatus'] = [d.to_api_json() for d in user.drop_in_departments]
        profile['sameDayAdvisorStatus'] = [d.to_api_json() for d in user.same_day_departments]
        user_login = UserLogin.last_login(user.uid)
        profile['lastLogin'] = _isoformat(user_login.created_at) if user_login else None
        profiles.append(profile)
    sort_by = sort_by or 'lastName'
    return sorted(profiles, key=lambda p: (p.get(sort_by) is None, p.get(sort_by)), reverse=sort_descending)


def drop_in_advisors_for_dept_code(dept_code):
    dept_code = dept_code.upper()
    advisor_assignments = DropInAdvisor.advisors_for_dept_code(dept_code)
    advisors = []
    for a in advisor_assignments:
        advisor = authorized_users_api_feed([a.authorized_user])[0]
        if advisor['canAccessAdvisingData']:
            advisor['available'] = a.is_available
            advisor['status'] = a.status
            advisors.append(advisor)
    return sorted(advisors, key=lambda u: ((u.get('firstName') or '').upper(), (u.get('lastName') or '').upper(), u.get('id')))


def put_notifications(student):
    sid = student['sid']
    student['notifications'] = {
        'alert': [],
        'hold': [],
        'requirement': [],
    }
    if current_user.can_access_advising_data:
        student['notifications']['appointment'] = []
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
            student['notifications']['note'].append({
                **note,
                **{
                    'message': message.strip() if message else None,
                    'type': 'note',
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
    topics = request.form.get('topics', ())
    return topics if isinstance(topics, list) else list(filter(None, str(topics).split(',')))


def get_my_curated_groups():
    curated_groups = []
    user_id = current_user.get_id()
    for curated_group in CuratedGroup.get_curated_groups_by_owner_id(user_id):
        api_json = curated_group.to_api_json(include_students=False)
        students = [{'sid': sid} for sid in CuratedGroup.get_all_sids(curated_group.id)]
        students_with_alerts = Alert.include_alert_counts_for_students(
            viewer_user_id=user_id,
            group={'students': students},
            count_only=True,
        )
        api_json['alertCount'] = sum(s['alertCount'] for s in students_with_alerts)
        api_json['totalStudentCount'] = len(students)
        curated_groups.append(api_json)
    return curated_groups


def is_unauthorized_domain(domain):
    if domain not in ['default', 'admitted_students']:
        raise BadRequestError(f'Invalid domain: {domain}')
    elif domain == 'admitted_students' and not app.config['FEATURE_FLAG_ADMITTED_STUDENTS']:
        raise ResourceNotFoundError('Unknown path')
    return domain == 'admitted_students' and not current_user.is_admin and 'ZCEEE' not in dept_codes_where_advising(current_user)


def is_unauthorized_search(filter_keys, order_by=None):
    filter_key_set = set(filter_keys)
    asc_keys = {'inIntensiveCohort', 'isInactiveAsc', 'groupCodes'}
    if list(filter_key_set & asc_keys) or order_by in ['group_name']:
        if not current_user.is_admin and 'UWASC' not in dept_codes_where_advising(current_user):
            return True
    coe_keys = {
        'coeAdvisorLdapUids',
        'coeEthnicities',
        'coeGenders',
        'coePrepStatuses',
        'coeProbation',
        'coeUnderrepresented',
        'isInactiveCoe',
    }
    if list(filter_key_set & coe_keys):
        if not current_user.is_admin and 'COENG' not in dept_codes_where_advising(current_user):
            return True
    return False


def response_with_students_csv_download(sids, fieldnames, benchmark):
    rows = []
    getters = {
        'first_name': lambda profile: profile.get('firstName'),
        'last_name': lambda profile: profile.get('lastName'),
        'sid': lambda profile: profile.get('sid'),
        'email': lambda profile: profile.get('sisProfile', {}).get('emailAddress'),
        'phone': lambda profile: profile.get('sisProfile', {}).get('phoneNumber'),
        'majors': lambda profile: ';'.join(
            [plan.get('description') for plan in profile.get('sisProfile', {}).get('plans', []) if plan.get('status') == 'Active'],
        ),
        'intended_majors': lambda profile: ';'.join(
            [major.get('description') for major in profile.get('sisProfile', {}).get('intendedMajors')],
        ),
        'level_by_units': lambda profile: profile.get('sisProfile', {}).get('level', {}).get('description'),
        'minors': lambda profile: ';'.join(
            [plan.get('description') for plan in profile.get('sisProfile', {}).get('plansMinor', []) if plan.get('status') == 'Active'],
        ),
        'subplans': lambda profile: ';'.join([subplan for subplan in profile.get('sisProfile', {}).get('subplans', [])]),
        'terms_in_attendance': lambda profile: profile.get('sisProfile', {}).get('termsInAttendance'),
        'expected_graduation_term': lambda profile: profile.get('sisProfile', {}).get('expectedGraduationTerm', {}).get('name'),
        'units_completed': lambda profile: profile.get('sisProfile', {}).get('cumulativeUnits'),
        'term_gpa': lambda profile: profile.get('termGpa'),
        'cumulative_gpa': lambda profile: profile.get('sisProfile', {}).get('cumulativeGPA'),
        'program_status': lambda profile: ';'.join(
            list(
                set(
                    [
                        plan.get('status') for plan in profile.get('sisProfile', {}).get('plans', [])
                    ],
                ),
            ),
        ),
        'academic_standing': lambda profile: profile.get('academicStanding'),
        'transfer': lambda profile: 'Yes' if profile.get('sisProfile', {}).get('transfer') else '',
        'intended_major': lambda profile: ', '.join([major.get('description') for major in profile.get('sisProfile', {}).get('plans')]),
    }
    academic_standing = get_academic_standing_by_sid(sids, as_dicts=True)
    term_gpas = get_term_gpas_by_sid(sids, as_dicts=True)

    def _get_last_element(results):
        return results[sorted(results)[-1]] if results else None

    def _add_row(student_profile):
        student_profile['academicStanding'] = _get_last_element(academic_standing.get(student_profile['sid']))
        student_profile['termGpa'] = _get_last_element(term_gpas.get(student_profile['sid']))
        row = {}
        for fieldname in fieldnames:
            row[fieldname] = getters[fieldname](student_profile)
        rows.append(row)

    students = get_student_profiles(sids=sids)
    for student in students:
        profile = student.get('profile')
        if profile:
            _add_row(json.loads(profile))
    remaining_sids = list(set(sids) - set([s.get('sid') for s in students]))
    if remaining_sids:
        for profile in get_historical_student_profiles(remaining_sids):
            _add_row(profile)

    benchmark('end')

    return response_with_csv_download(
        rows=sorted(rows, key=lambda r: (_norm(r, 'last_name'), _norm(r, 'first_name'), _norm(r, 'sid'))),
        filename_prefix='cohort',
        fieldnames=fieldnames,
    )


@ce3_required
def response_with_admits_csv_download(sids, fieldnames, benchmark):
    key_aliases = {
        'cs_empl_id': 'sid',
    }

    def _row_for_csv(result):
        return {f: result.get(key_aliases.get(f, f)) for f in fieldnames}
    rows = [_row_for_csv(student) for student in get_admitted_students_by_sids(sids=sids)]
    benchmark('end')

    return response_with_csv_download(
        rows=sorted(rows, key=lambda r: (_norm(r, 'last_name'), _norm(r, 'first_name'), _norm(r, 'cs_empl_id'))),
        filename_prefix='cohort',
        fieldnames=fieldnames,
    )


def _norm(row, key):
    value = row.get(key)
    return value and value.upper()


def _has_role_in_any_department(user, role):
    return next((d for d in user.departments if d['role'] == role), False)


def _is_advisor_in_department(user, dept):
    return next((d for d in user.departments if d['code'] == dept and d['role'] in ('advisor', 'director')), False)


def _is_drop_in_advisor(user):
    return next((d for d in user.drop_in_advisor_departments if d['deptCode'] in app.config['DEPARTMENTS_SUPPORTING_DROP_INS']), False)


def _is_drop_in_enabled(user):
    return next((d for d in user.departments if d['code'] in app.config['DEPARTMENTS_SUPPORTING_DROP_INS']), False)


def _is_drop_in_scheduler(user):
    scheduler_dept = _has_role_in_any_department(current_user, 'scheduler')
    return scheduler_dept and scheduler_dept['code'] in app.config['DEPARTMENTS_SUPPORTING_DROP_INS']


def _is_same_day_advisor(user):
    return next((d for d in user.same_day_advisor_departments if d['deptCode'] in app.config['DEPARTMENTS_SUPPORTING_SAME_DAY_APPTS']), False)


def _is_same_day_enabled(user):
    return next((d for d in user.departments if d['code'] in app.config['DEPARTMENTS_SUPPORTING_SAME_DAY_APPTS']), False)


def _is_same_day_scheduler(user):
    scheduler_dept = _has_role_in_any_department(current_user, 'scheduler')
    return scheduler_dept and scheduler_dept['code'] in app.config['DEPARTMENTS_SUPPORTING_SAME_DAY_APPTS']


def _api_key_ok():
    auth_key = app.config['API_KEY']
    return auth_key and (request.headers.get('App-Key') == auth_key)


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
