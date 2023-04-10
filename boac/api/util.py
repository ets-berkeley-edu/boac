"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.lib.berkeley import dept_codes_where_advising, previous_term_id
from boac.lib.http import response_with_csv_download
from boac.lib.util import get_benchmarker, join_if_present
from boac.merged import calnet
from boac.merged.advising_appointment import get_advising_appointments
from boac.merged.advising_note import get_advising_notes
from boac.merged.sis_terms import current_term_id
from boac.merged.student import get_term_gpas_by_sid, get_term_units_by_sid
from boac.models.alert import Alert
from boac.models.authorized_user_extension import DropInAdvisor
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from boac.models.degree_progress_course import ACCENT_COLOR_CODES
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


def can_access_admitted_students(user):
    return app.config['FEATURE_FLAG_ADMITTED_STUDENTS'] \
        and user.is_authenticated \
        and (current_user.is_admin or _is_advisor_in_department(current_user, 'ZCEEE'))


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


def normalize_accent_color(color):
    if color:
        capitalized = color.capitalize()
        return capitalized if capitalized in list(ACCENT_COLOR_CODES.keys()) else None


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
            'automateDegreeProgressPermission': user.automate_degree_progress_permission,
            'canAccessAdvisingData': user.can_access_advising_data,
            'canAccessCanvasData': user.can_access_canvas_data,
            'canEditDegreeProgress': user.degree_progress_permission == 'read_write' or user.is_admin,
            'canReadDegreeProgress': user.degree_progress_permission in ['read', 'read_write'] or user.is_admin,
            'degreeProgressPermission': user.degree_progress_permission,
            'deletedAt': _isoformat(user.deleted_at),
            'departments': [],
            'isAdmin': user.is_admin,
            'isBlocked': user.is_blocked,
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
    for cohort in CohortFilter.get_cohorts(current_user.get_id()):
        cohort['isOwnedByCurrentUser'] = True
        cohorts.append(cohort)
    return {
        **current_user.to_api_json(),
        'myCohorts': cohorts,
        'myCuratedGroups': get_my_curated_groups(),
        'myDraftNoteCount': 0,
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
    topics = request.form.get('topics', ())
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


def _response_with_students_csv_download(sids, fieldnames, benchmark, term_id):
    term_id_last = previous_term_id(current_term_id())
    term_id_previous = previous_term_id(term_id_last)
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
        f'term_gpa_{term_id_previous}': lambda profile: profile.get('termGpa', {}).get(term_id_previous),
        f'term_gpa_{term_id_last}': lambda profile: profile.get('termGpa', {}).get(term_id_last),
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
        'transfer': lambda profile: 'Yes' if profile.get('sisProfile', {}).get('transfer') else '',
        'intended_major': lambda profile: ', '.join([
                                                    major.get('description') for major
                                                    in (profile.get('sisProfile', {}).get('intendedMajors') or [])]),
        'units_in_progress': lambda profile: profile.get('enrolledUnits', {}),
    }
    term_gpas = get_term_gpas_by_sid(sids)
    term_units = get_term_units_by_sid(term_id, sids)

    def _add_row(student_profile):
        student_profile['termGpa'] = term_gpas.get(student_profile['sid'], {})
        student_profile['enrolledUnits'] = term_units.get(student_profile['sid'], '0')

        row = {}
        for fieldname in fieldnames:
            row[fieldname] = getters[fieldname](student_profile)
        rows.append(row)

    students = get_student_profiles(sids=sids)
    for student in students:
        profile = student.get('profile')
        if profile:
            _add_row(json.loads(profile))

    benchmark('end')

    return response_with_csv_download(
        rows=sorted(rows, key=lambda r: (_norm(r, 'last_name'), _norm(r, 'first_name'), _norm(r, 'sid'))),
        filename_prefix='cohort',
        fieldnames=fieldnames,
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
