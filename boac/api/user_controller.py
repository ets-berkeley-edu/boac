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

import re

from boac.api import errors
from boac.api.util import admin_required, advisor_required, authorized_users_api_feed, drop_in_advisors_for_dept_code, scheduler_required
from boac.lib import util
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.http import response_with_csv_download, tolerant_jsonify
from boac.lib.util import to_bool_or_none
from boac.merged import calnet
from boac.merged.user_session import UserSession
from boac.models.authorized_user import AuthorizedUser
from boac.models.drop_in_advisor import DropInAdvisor
from boac.models.university_dept import UniversityDept
from boac.models.university_dept_member import UniversityDeptMember
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/profile/my')
def my_profile():
    return tolerant_jsonify(current_user.to_api_json())


@app.route('/api/profile/<uid>')
@login_required
def user_profile(uid):
    if not AuthorizedUser.find_by_uid(uid):
        raise errors.ResourceNotFoundError('Unknown path')
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, uid))


@app.route('/api/user/by_csid/<csid>')
@advisor_required
def calnet_profile(csid):
    user = calnet.get_calnet_user_for_csid(app, csid)
    uid = user.get('uid', None)
    ignore_deleted = to_bool_or_none(util.get(request.args, 'ignoreDeleted'))
    user = _find_user_by_uid(uid, ignore_deleted)
    if user:
        users_feed = authorized_users_api_feed([user])
        return tolerant_jsonify(users_feed[0])
    else:
        raise errors.ResourceNotFoundError('User not found')


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
        is_advisor=params.get('isAdvisor', False),
        is_director=params.get('isDirector', False),
        is_scheduler=params.get('isScheduler', False),
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
        is_advisor=params.get('isAdvisor', None),
        is_director=params.get('isDirector', None),
        is_scheduler=params.get('isScheduler', False),
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


@app.route('/api/user/<uid>/drop_in_status/<dept_code>/activate', methods=['POST'])
@scheduler_required
def activate_drop_in_status(uid, dept_code):
    return _update_drop_in_status(uid, dept_code, True)


@app.route('/api/user/<uid>/drop_in_status/<dept_code>/deactivate', methods=['POST'])
@scheduler_required
def deactivate_drop_in_status(uid, dept_code):
    return _update_drop_in_status(uid, dept_code, False)


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
    users = AuthorizedUser.query.filter(AuthorizedUser.is_admin).all()
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
    roles_per_dept_code = params.get('rolesPerDeptCode', None)
    if not profile or not profile.get('uid') or roles_per_dept_code is None:
        raise errors.BadRequestError('Required parameters are missing')

    authorized_user = _update_or_create_authorized_user(profile)
    _delete_existing_memberships(authorized_user)
    _create_department_memberships(authorized_user, roles_per_dept_code)
    _create_drop_in_advisor(authorized_user, roles_per_dept_code)

    user_id = authorized_user.id
    UserSession.flush_cache_for_id(user_id)
    users_json = authorized_users_api_feed([AuthorizedUser.find_by_id(user_id)])
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
        app.login_manager.reload_user()
        return tolerant_jsonify(current_user.to_api_json())
    else:
        raise errors.ResourceNotFoundError('Unknown path')


@app.route('/api/users/csv')
@admin_required
def download_boa_users_csv():
    fieldnames = None
    rows = []
    for dept in _get_boa_user_groups():
        for user in dept['users']:
            rows.append(
                {
                    'last_name': user.get('lastName') or '',
                    'first_name': user.get('firstName') or '',
                    'uid': user.get('uid'),
                    'title': user.get('title'),
                    'email': user.get('campusEmail') or user.get('email'),
                    'departments': _describe_dept_roles(user['departments']),
                    'drop_in_advising': _describe_drop_in_advising(user['departments'], user['dropInAdvisorStatus']),
                    'can_access_canvas_data': user.get('canAccessCanvasData'),
                    'is_blocked': user.get('isBlocked'),
                    'last_login': user.get('lastLogin'),
                },
            )
            if not fieldnames:
                fieldnames = rows[-1].keys()
    return response_with_csv_download(
        rows=sorted(rows, key=lambda row: row['last_name'].upper()),
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


def _get_boa_user_groups():
    depts = {}

    def _put(_dept_code, _user):
        if _dept_code not in depts:
            if _dept_code == 'ADMIN':
                dept_name = 'Admins'
            elif _dept_code == 'GUEST':
                dept_name = 'Guest Access'
            elif _dept_code == 'NOTESONLY':
                dept_name = 'Notes Only'
            else:
                dept_name = BERKELEY_DEPT_CODE_TO_NAME.get(_dept_code, _dept_code)
            depts[_dept_code] = {
                'code': _dept_code,
                'name': dept_name,
                'users': [],
            }
        depts[_dept_code]['users'].append(_user)
    for user in AuthorizedUser.get_all_active_users():
        if user.is_admin:
            _put('ADMIN', user)
        if user.can_access_canvas_data:
            for m in user.department_memberships:
                _put(m.university_dept.dept_code, user)
        else:
            _put('NOTESONLY', user)
    user_groups = []
    for dept_code, dept in depts.items():
        users = authorized_users_api_feed(dept['users'])
        dept['users'] = sorted(users, key=lambda p: p.get('lastName') or '')
        user_groups.append(dept)
    return sorted(user_groups, key=lambda group: group['name'])


def _update_drop_in_status(uid, dept_code, active):
    dept_code = dept_code.upper()
    if uid == 'me':
        uid = current_user.get_uid()
    else:
        authorized_to_toggle = current_user.is_admin or dept_code in [d['code'] for d in current_user.departments if d.get('isScheduler')]
        if not authorized_to_toggle:
            raise errors.ForbiddenRequestError(f'Unauthorized to toggle drop-in status for department {dept_code}')
    drop_in_status = None
    user = AuthorizedUser.find_by_uid(uid)
    if user:
        drop_in_status = next((d for d in user.drop_in_departments if d.dept_code == dept_code), None)
    if drop_in_status:
        drop_in_status.update_availability(active)
        UserSession.flush_cache_for_id(user.id)
        return tolerant_jsonify(drop_in_status.to_api_json())
    else:
        raise errors.ResourceNotFoundError(f'No drop-in advisor status found: (uid={uid}, dept_code={dept_code})')


def _update_or_create_authorized_user(profile):
    user_id = profile.get('id')
    can_access_canvas_data = to_bool_or_none(profile.get('canAccessCanvasData'))
    is_admin = to_bool_or_none(profile.get('isAdmin'))
    is_blocked = to_bool_or_none(profile.get('isBlocked'))
    if user_id:
        return AuthorizedUser.update_user(
            user_id=user_id,
            can_access_canvas_data=can_access_canvas_data,
            is_admin=is_admin,
            is_blocked=is_blocked,
        )
    else:
        uid = profile.get('uid')
        calnet_user = calnet.get_calnet_user_for_uid(app, uid, skip_expired_users=True)
        if calnet_user and calnet_user.get('csid', None):
            return AuthorizedUser.create_or_restore(
                uid=uid,
                created_by=current_user.get_uid(),
                is_admin=is_admin,
                is_blocked=is_blocked,
                can_access_canvas_data=can_access_canvas_data,
            )
        else:
            raise errors.BadRequestError('Invalid UID')


def _delete_existing_memberships(authorized_user):
    existing_memberships = UniversityDeptMember.get_existing_memberships(authorized_user_id=authorized_user.id)
    existing_drop_in_dept_codes = [a.dept_code for a in DropInAdvisor.get_all(authorized_user_id=authorized_user.id)]
    for university_dept_id in [m.university_dept.id for m in existing_memberships]:
        UniversityDeptMember.delete_membership(
            university_dept_id=university_dept_id,
            authorized_user_id=authorized_user.id,
        )
    for dept_code in existing_drop_in_dept_codes:
        DropInAdvisor.delete(authorized_user_id=authorized_user.id, dept_code=dept_code)


def _create_department_memberships(authorized_user, user_roles):
    for user_role in [d for d in user_roles if d['role'] in ('advisor', 'director', 'scheduler')]:
        university_dept = UniversityDept.find_by_dept_code(user_role['code'])
        role = user_role['role']
        UniversityDeptMember.create_or_update_membership(
            university_dept_id=university_dept.id,
            authorized_user_id=authorized_user.id,
            is_advisor=role in ['advisor', 'dropInAdvisor'],
            is_director=role == 'director',
            is_scheduler=role == 'scheduler',
            automate_membership=to_bool_or_none(user_role['automateMembership']),
        )


def _create_drop_in_advisor(authorized_user, roles_per_dept_code):
    for user_role in [d for d in roles_per_dept_code if d['role'] == 'dropInAdvisor']:
        university_dept = UniversityDept.find_by_dept_code(user_role['code'])
        DropInAdvisor.create_or_update_status(university_dept=university_dept, authorized_user_id=authorized_user.id)
        UniversityDeptMember.create_or_update_membership(
            university_dept_id=university_dept.id,
            authorized_user_id=authorized_user.id,
            is_advisor=True,
            is_director=False,
            is_scheduler=False,
            automate_membership=to_bool_or_none(user_role['automateMembership']),
        )


def _describe_dept_roles(departments):
    s = '{ '
    for d in list(filter(lambda d: d.get('isAdvisor') or d.get('isDirector'), departments)):
        roles = ['Advisor'] if d.get('isAdvisor') else []
        if d.get('isDirector'):
            roles.append('Director')
        s += f"[ {d.get('code')}: {'; '.join(roles)} (automated={d.get('automateMembership')}) ] "
    s += '}'
    return s


def _describe_drop_in_advising(departments, drop_in_advisor_statuses):
    s = '{ '
    for d in list(filter(lambda d: d['isScheduler'], departments)):
        s += f"[ {d.get('code')}: Scheduler (automated={d.get('automateMembership')}) ] "
    for d in drop_in_advisor_statuses:
        s += f"[ {d.get('detCode')}: Drop-in Advisor ] "
    s += '}'
    return s


def _find_user_by_uid(uid, ignore_deleted=True):
    if uid:
        ignore_deleted_ = True if ignore_deleted is None else ignore_deleted
        return AuthorizedUser.find_by_uid(uid, ignore_deleted=ignore_deleted_)
    else:
        return None
