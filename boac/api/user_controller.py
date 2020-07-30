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

import re

from boac.api import errors
from boac.api.util import (
    admin_required,
    advising_data_access_required,
    advisor_required,
    authorized_users_api_feed,
    drop_in_advisors_for_dept_code,
    drop_in_required,
    scheduler_required,
)
from boac.lib import util
from boac.lib.http import response_with_csv_download, tolerant_jsonify
from boac.lib.util import to_bool_or_none
from boac.merged import calnet
from boac.merged.user_session import UserSession
from boac.models.appointment import Appointment
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user_extension import DropInAdvisor, SameDayAdvisor, Scheduler
from boac.models.university_dept import UniversityDept
from boac.models.university_dept_member import UniversityDeptMember
from flask import current_app as app, request
from flask_login import current_user, login_required, login_user


@app.route('/api/profile/my')
def my_profile():
    return tolerant_jsonify(current_user.to_api_json())


@app.route('/api/profile/<uid>')
@login_required
def user_profile(uid):
    if not AuthorizedUser.find_by_uid(uid):
        raise errors.ResourceNotFoundError('Unknown path')
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, uid))


@app.route('/api/user/calnet_profile/by_csid/<csid>')
@advisor_required
def calnet_profile_by_csid(csid):
    return tolerant_jsonify(calnet.get_calnet_user_for_csid(app, csid))


@app.route('/api/user/calnet_profile/by_uid/<uid>')
@advisor_required
def calnet_profile_by_uid(uid):
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, uid))


@app.route('/api/user/by_uid/<uid>')
@advisor_required
def user_by_uid(uid):
    ignore_deleted = to_bool_or_none(util.get(request.args, 'ignoreDeleted'))
    user = _find_user_by_uid(uid, ignore_deleted)
    if user:
        users_feed = authorized_users_api_feed([user])
        return tolerant_jsonify(users_feed[0])
    else:
        raise errors.ResourceNotFoundError('User not found')


@app.route('/api/user/dept_membership/add', methods=['POST'])
@admin_required
def add_university_dept_membership():
    params = request.get_json() or {}
    dept = UniversityDept.find_by_dept_code(params.get('deptCode', None))
    user = AuthorizedUser.find_by_uid(params.get('uid', None))
    membership = UniversityDeptMember.create_or_update_membership(
        university_dept_id=dept.id,
        authorized_user_id=user.id,
        role=params.get('role', None),
        automate_membership=params.get('automateMembership', True),
    )
    return tolerant_jsonify(membership.to_api_json())


@app.route('/api/user/dept_membership/update', methods=['POST'])
@admin_required
def update_university_dept_membership():
    params = request.get_json() or {}
    dept = UniversityDept.find_by_dept_code(params.get('deptCode', None))
    user = AuthorizedUser.find_by_uid(params.get('uid', None))
    membership = UniversityDeptMember.update_membership(
        university_dept_id=dept.id,
        authorized_user_id=user.id,
        role=params.get('role', None),
        automate_membership=params.get('automateMembership', None),
    )
    if not membership:
        raise errors.BadRequestError(f'Failed to update university dept membership: university_dept_id={dept.id} authorized_user_id={user.id}')
    return tolerant_jsonify(membership.to_api_json())


@app.route('/api/user/dept_membership/delete/<university_dept_id>/<authorized_user_id>', methods=['DELETE'])
@admin_required
def delete_university_dept_membership(university_dept_id, authorized_user_id):
    if not UniversityDeptMember.delete_membership(university_dept_id, authorized_user_id):
        raise errors.ResourceNotFoundError(
            f'University dept membership not found: university_dept_id={university_dept_id} authorized_user_id={authorized_user_id}',
        )
    return tolerant_jsonify(
        {'message': f'University dept membership deleted: university_dept_id={university_dept_id} authorized_user_id={authorized_user_id}'},
        status=200,
    )


@app.route('/api/user/drop_in_advising/<dept_code>/enable', methods=['POST'])
@drop_in_required
def enable_drop_in_advising(dept_code):
    drop_in_membership = DropInAdvisor.create_or_update_membership(
        dept_code,
        current_user.user_id,
        is_available=False,
    )
    UserSession.flush_cache_for_id(current_user.user_id)
    return tolerant_jsonify(drop_in_membership.to_api_json())


@app.route('/api/user/drop_in_advising/<dept_code>/disable', methods=['POST'])
@scheduler_required
def disable_drop_in_advising(dept_code):
    user = AuthorizedUser.find_by_id(current_user.get_id())
    _delete_drop_in_advisor_status(user, dept_code)
    UserSession.flush_cache_for_id(user.id)
    return tolerant_jsonify({'message': 'Drop-in advisor status has been disabled'}, status=200)


@app.route('/api/user/same_day_advising/<dept_code>/enable', methods=['POST'])
@drop_in_required
def enable_same_day_advising(dept_code):
    same_day_membership = SameDayAdvisor.create_or_update_membership(
        dept_code,
        current_user.user_id,
        is_available=True,
    )
    UserSession.flush_cache_for_id(current_user.user_id)
    return tolerant_jsonify(same_day_membership.to_api_json())


@app.route('/api/user/same_day_advising/<dept_code>/disable', methods=['POST'])
@scheduler_required
def disable_same_day_advising(dept_code):
    user = AuthorizedUser.find_by_id(current_user.get_id())
    SameDayAdvisor.delete(authorized_user_id=user.id, dept_code=dept_code)
    UserSession.flush_cache_for_id(user.id)
    return tolerant_jsonify({'message': 'Same-day advisor status has been disabled'}, status=200)


@app.route('/api/user/<uid>/drop_in_advising/<dept_code>/available', methods=['POST'])
@scheduler_required
def set_drop_in_advising_available(uid, dept_code):
    return _update_drop_in_availability(uid, dept_code, True)


@app.route('/api/user/<uid>/drop_in_advising/<dept_code>/unavailable', methods=['POST'])
@scheduler_required
def set_drop_in_advising_unavailable(uid, dept_code):
    return _update_drop_in_availability(uid, dept_code, False)


@app.route('/api/user/drop_in_advising/<dept_code>/status', methods=['POST'])
@drop_in_required
def set_drop_in_advising_status(dept_code):
    user = AuthorizedUser.find_by_id(current_user.get_id())
    drop_in_membership = next((d for d in user.drop_in_departments if d.dept_code == dept_code.upper()), None)
    if not drop_in_membership:
        raise errors.ResourceNotFoundError(f'No drop-in advisor membership found: (uid={current_user.get_uid()}, dept_code={dept_code})')
    params = request.get_json()
    if 'status' not in params:
        raise errors.BadRequestError('Missing status')
    if params['status'] and len(params['status']) > 255:
        raise errors.BadRequestError('Invalid status')
    drop_in_membership.update_status(params['status'])
    UserSession.flush_cache_for_id(user.id)
    return tolerant_jsonify(drop_in_membership.to_api_json())


@app.route('/api/users', methods=['POST'])
@admin_required
def all_users():
    params = request.get_json()
    users, total_user_count = AuthorizedUser.get_users(
        blocked=to_bool_or_none(util.get(params, 'blocked')),
        deleted=to_bool_or_none(util.get(params, 'deleted')),
        dept_code=util.get(params, 'deptCode', None),
        role=util.get(params, 'role', None) or None,
    )
    return tolerant_jsonify({
        'users': authorized_users_api_feed(
            users,
            sort_by=util.get(params, 'sortBy', 'lastName'),
            sort_descending=to_bool_or_none(util.get(params, 'sortDescending', False)),
        ),
        'totalUserCount': total_user_count,
    })


@app.route('/api/users/admins', methods=['POST'])
@admin_required
def get_admin_users():
    params = request.get_json()
    ignore_deleted = to_bool_or_none(util.get(params, 'ignoreDeleted'))
    users = AuthorizedUser.get_admin_users(ignore_deleted=True if ignore_deleted is None else ignore_deleted)
    return tolerant_jsonify({
        'users': authorized_users_api_feed(
            users,
            sort_by=util.get(params, 'sortBy'),
            sort_descending=to_bool_or_none(util.get(params, 'sortDescending')),
        ),
        'totalUserCount': len(users),
    })


@app.route('/api/users/autocomplete', methods=['POST'])
@admin_required
def user_search():
    snippet = request.get_json().get('snippet', '').strip()
    if snippet:
        search_by_uid = re.match(r'\d+', snippet)
        if search_by_uid:
            users = AuthorizedUser.users_with_uid_like(snippet, include_deleted=True)
        else:
            users = AuthorizedUser.get_all_active_users(include_deleted=True)
        users = list(calnet.get_calnet_users_for_uids(app, [u.uid for u in users]).values())
        if not search_by_uid:
            any_ = r'.*'
            pattern = re.compile(any_ + any_.join(snippet.split()) + any_, re.IGNORECASE)
            users = list(filter(lambda u: u.get('name') and pattern.match(u['name']), users))
    else:
        users = []

    def _label(user):
        name = user['name']
        return f"{name} ({user['uid']})" if name else user['uid']
    return tolerant_jsonify([{'label': _label(u), 'uid': u['uid']} for u in users])


@app.route('/api/users/drop_in_advisors/<dept_code>')
@scheduler_required
def drop_in_advisors_for_dept(dept_code):
    return tolerant_jsonify(drop_in_advisors_for_dept_code(dept_code))


@app.route('/api/users/create_or_update', methods=['POST'])
@admin_required
def create_or_update_user_profile():
    params = request.get_json()
    profile = params.get('profile', None)
    memberships = params.get('memberships', None)
    delete_action = to_bool_or_none(util.get(params, 'deleteAction'))

    if not profile or not profile.get('uid') or memberships is None:
        raise errors.BadRequestError('Required parameters are missing')

    authorized_user = _update_or_create_authorized_user(profile, include_deleted=True)
    _delete_existing_memberships(authorized_user)
    _create_department_memberships(authorized_user, memberships)

    if delete_action is True and not authorized_user.deleted_at:
        AuthorizedUser.delete_and_block(authorized_user.uid)
    elif delete_action is False and authorized_user.deleted_at:
        AuthorizedUser.un_delete(authorized_user.uid)

    user_id = authorized_user.id
    UserSession.flush_cache_for_id(user_id)

    updated_user = AuthorizedUser.find_by_id(user_id, include_deleted=True)
    users_json = authorized_users_api_feed([updated_user])
    return tolerant_jsonify(users_json and users_json[0])


@app.route('/api/user/demo_mode', methods=['POST'])
@login_required
def set_demo_mode():
    if app.config['DEMO_MODE_AVAILABLE']:
        in_demo_mode = request.get_json().get('demoMode', None)
        if in_demo_mode is None:
            raise errors.BadRequestError('Parameter \'demoMode\' not found')
        user = AuthorizedUser.find_by_id(current_user.get_id())
        user.in_demo_mode = bool(in_demo_mode)
        current_user.flush_cached()
        login_user(UserSession(user_id=user.id, flush_cached=True), force=True, remember=True)
        return tolerant_jsonify(current_user.to_api_json())
    else:
        raise errors.ResourceNotFoundError('Unknown path')


@app.route('/api/users/csv')
@admin_required
def download_boa_users_csv():
    users = _get_boa_users()
    fieldnames = users[-1].keys()
    return response_with_csv_download(
        rows=sorted(users, key=lambda row: row['last_name'].upper()),
        filename_prefix='boa_users',
        fieldnames=fieldnames,
    )


@app.route('/api/users/departments')
@admin_required
def get_departments():
    exclude_empty = to_bool_or_none(util.get(request.args, 'excludeEmpty', None))
    api_json = []
    for d in UniversityDept.get_all(exclude_empty=exclude_empty):
        api_json.append({
            'id': d.id,
            'code': d.dept_code,
            'name': d.dept_name,
        })
    return tolerant_jsonify(api_json)


@app.route('/api/users/appointment_schedulers')
@advising_data_access_required
def get_appointment_schedulers_for_my_depts():
    return tolerant_jsonify(_get_appointment_scheduler_list(current_user))


@app.route('/api/users/appointment_schedulers/<dept_code>/add', methods=['POST'])
@advising_data_access_required
def add_appointment_scheduler_to_dept(dept_code):
    _verify_membership_and_appointments_enabled(current_user, dept_code)
    params = request.get_json() or {}
    scheduler_uid = params.get('uid', None)
    if not scheduler_uid:
        raise errors.BadRequestError('Scheduler UID missing')
    calnet_user = calnet.get_calnet_user_for_uid(app, scheduler_uid, skip_expired_users=True)
    if not calnet_user or not calnet_user.get('csid'):
        raise errors.BadRequestError('Invalid scheduler UID')
    user = AuthorizedUser.create_or_restore(
        scheduler_uid,
        created_by=current_user.get_uid(),
        is_admin=False,
        is_blocked=False,
        can_access_canvas_data=False,
    )
    Scheduler.create_or_update_membership(
        dept_code,
        user.id,
        drop_in=True,
        same_day=True,
    )
    _create_department_memberships(user, [{'code': dept_code, 'role': 'scheduler', 'automateMembership': False}])
    UserSession.flush_cache_for_id(user.id)
    return tolerant_jsonify(_get_appointment_scheduler_list(current_user, dept_code))


@app.route('/api/users/appointment_schedulers/<dept_code>/remove', methods=['POST'])
@advising_data_access_required
def remove_appointment_scheduler_from_dept(dept_code):
    _verify_membership_and_appointments_enabled(current_user, dept_code)
    params = request.get_json() or {}
    uid = params.get('uid')
    user = uid and AuthorizedUser.find_by_uid(uid)
    if not user:
        raise errors.BadRequestError(f'UID {uid} missing or invalid')
    scheduler_membership = next((d for d in user.department_memberships if d.university_dept.dept_code == dept_code and d.role == 'scheduler'), None)
    if not scheduler_membership:
        raise errors.BadRequestError(f'UID {uid} is not a scheduler for department {dept_code}')
    UniversityDeptMember.delete_membership(
        university_dept_id=scheduler_membership.university_dept_id,
        authorized_user_id=user.id,
    )
    Scheduler.delete(authorized_user_id=user.id, dept_code=dept_code)
    if not len(user.department_memberships):
        AuthorizedUser.delete(uid)
    return tolerant_jsonify(_get_appointment_scheduler_list(current_user, dept_code))


def _verify_membership_and_appointments_enabled(user, dept_code):
    membership = next((d for d in user.departments if d['code'] == dept_code and _is_appointment_enabled(d)), None)
    if not membership:
        raise errors.ForbiddenRequestError('No department membership found or drop-in scheduling not enabled')


def _get_boa_users():
    users = []

    def _put(_dept, _user):
        users.append({
            'last_name': _user.get('lastName') or '',
            'first_name': _user.get('firstName') or '',
            'uid': _user.get('uid'),
            'title': _user.get('title'),
            'email': _user.get('campusEmail') or _user.get('email'),
            'department': _describe_dept_roles(_dept),
            'appointment_roles': _describe_appointment_roles(_dept, _user.get('dropInAdvisorStatus'), _user.get('sameDayAdvisorStatus')),
            'can_access_advising_data': _user.get('canAccessAdvisingData'),
            'can_access_canvas_data': _user.get('canAccessCanvasData'),
            'is_blocked': _user.get('isBlocked'),
            'last_login': _user.get('lastLogin'),
        })

    admin_dept = {
        'code': 'ADMIN',
        'name': 'Admins',
    }
    for user in authorized_users_api_feed(AuthorizedUser.get_all_active_users()):
        if user.get('isAdmin'):
            _put(admin_dept, user)
        for dept in user.get('departments'):
            _put(dept, user)
    return users


def _get_appointment_scheduler_list(advisor, dept_code=None):

    def _distill_scheduler_data(element):
        return {k: element[k] for k in ['uid', 'csid', 'firstName', 'lastName']}

    def _department_data(d):
        scheduler_response = AuthorizedUser.get_users(
            deleted=False,
            dept_code=d['code'],
            role='scheduler',
        )
        scheduler_data = [_distill_scheduler_data(s) for s in authorized_users_api_feed(scheduler_response[0], sort_by='lastName')]

        return {
            'code': d['code'],
            'name': d['name'],
            'schedulers': scheduler_data,
        }

    appointment_enabled_depts = [d for d in advisor.departments if _is_appointment_enabled(d)]

    if dept_code:
        dept_data = next((_department_data(d) for d in appointment_enabled_depts if d['code'] == dept_code), None)
        if not dept_data:
            return {'code': dept_code, 'schedulers': []}
        return dept_data
    else:
        return [_department_data(d) for d in appointment_enabled_depts]


def _is_appointment_enabled(membership):
    return (membership['isDropInEnabled'] or membership['isSameDayEnabled']) and membership['role'] in ('advisor', 'director')


def _update_drop_in_availability(uid, dept_code, new_availability):
    dept_code = dept_code.upper()
    if uid != current_user.get_uid():
        authorized_to_toggle = current_user.is_admin or dept_code in [d['code'] for d in current_user.departments if d.get('role') == 'scheduler']
        if not authorized_to_toggle:
            raise errors.ForbiddenRequestError(f'Unauthorized to toggle drop-in availability for department {dept_code}')
    drop_in_membership = None
    user = AuthorizedUser.find_by_uid(uid)
    if user:
        drop_in_membership = next((d for d in user.drop_in_departments if d.dept_code == dept_code), None)
    if drop_in_membership:
        if drop_in_membership.is_available is True and new_availability is False:
            Appointment.unreserve_all_for_advisor(uid, current_user.get_id())
        drop_in_membership.update_availability(new_availability)
        UserSession.flush_cache_for_id(user.id)
        return tolerant_jsonify(drop_in_membership.to_api_json())
    else:
        raise errors.ResourceNotFoundError(f'No drop-in advisor membership found: (uid={uid}, dept_code={dept_code})')


def _update_or_create_authorized_user(profile, include_deleted=False):
    user_id = profile.get('id')
    can_access_canvas_data = to_bool_or_none(profile.get('canAccessCanvasData'))
    can_access_advising_data = to_bool_or_none(profile.get('canAccessAdvisingData'))
    is_admin = to_bool_or_none(profile.get('isAdmin'))
    is_blocked = to_bool_or_none(profile.get('isBlocked'))
    if user_id:
        return AuthorizedUser.update_user(
            user_id=user_id,
            can_access_advising_data=can_access_advising_data,
            can_access_canvas_data=can_access_canvas_data,
            is_admin=is_admin,
            is_blocked=is_blocked,
            include_deleted=include_deleted,
        )
    else:
        uid = profile.get('uid')
        if AuthorizedUser.get_id_per_uid(uid, include_deleted=True):
            raise errors.BadRequestError(f'User with UID {uid} is already in the BOA database.')

        calnet_user = calnet.get_calnet_user_for_uid(app, uid, skip_expired_users=True)
        if calnet_user and calnet_user.get('csid', None):
            return AuthorizedUser.create_or_restore(
                uid=uid,
                created_by=current_user.get_uid(),
                is_admin=is_admin,
                is_blocked=is_blocked,
                can_access_advising_data=can_access_advising_data,
                can_access_canvas_data=can_access_canvas_data,
            )
        else:
            raise errors.BadRequestError('Invalid UID')


def _delete_existing_memberships(authorized_user):
    existing_memberships = UniversityDeptMember.get_existing_memberships(authorized_user_id=authorized_user.id)
    for university_dept_id in [m.university_dept.id for m in existing_memberships]:
        UniversityDeptMember.delete_membership(
            university_dept_id=university_dept_id,
            authorized_user_id=authorized_user.id,
        )


def _delete_drop_in_advisor_status(authorized_user, dept_code):
    DropInAdvisor.delete(authorized_user_id=authorized_user.id, dept_code=dept_code)
    Appointment.unreserve_all_for_advisor(authorized_user.uid, current_user.get_id())


def _create_department_memberships(authorized_user, memberships):
    for membership in [m for m in memberships if m['role'] in ('advisor', 'director', 'scheduler')]:
        university_dept = UniversityDept.find_by_dept_code(membership['code'])
        role = membership['role']
        UniversityDeptMember.create_or_update_membership(
            university_dept_id=university_dept.id,
            authorized_user_id=authorized_user.id,
            role=role,
            automate_membership=to_bool_or_none(membership['automateMembership']),
        )
        if role == 'scheduler':
            _delete_drop_in_advisor_status(authorized_user, university_dept.dept_code)
        UserSession.flush_cache_for_id(authorized_user.id)


def _describe_dept_roles(dept):
    s = ''
    if dept.get('role'):
        s += f"{{ {dept.get('code')}: {dept['role']} (automated={dept.get('automateMembership')}) }}"
    return s


def _describe_appointment_roles(dept, drop_in_advisor_statuses, same_day_advisor_statuses):
    s = ''
    if dept:
        s += '{ '
        if dept.get('role') == 'scheduler':
            s += f"{dept.get('code')}: Scheduler (automated={dept.get('automateMembership')}) "
        if next((d for d in drop_in_advisor_statuses if d.get('deptCode') == dept.get('code')), None):
            s += f"{dept.get('code')}: Drop-in Advisor "
        if next((d for d in same_day_advisor_statuses if d.get('deptCode') == dept.get('code')), None):
            s += f"{dept.get('code')}: Same-day Advisor "
        s += '}'
    return s


def _find_user_by_uid(uid, ignore_deleted=True):
    if uid:
        ignore_deleted_ = True if ignore_deleted is None else ignore_deleted
        return AuthorizedUser.find_by_uid(uid, ignore_deleted=ignore_deleted_)
    else:
        return None
