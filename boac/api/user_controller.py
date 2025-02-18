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

import re

from boac.api import errors
from boac.api.util import (
    admin_required,
    advisor_or_peer_advisor_required,
    advisor_required,
    authorized_users_api_feed,
    get_current_user_profile, is_peer_advisor, is_peer_advisor_manager,
)
from boac.lib import util
from boac.lib.http import response_with_csv_download, tolerant_jsonify
from boac.lib.util import has_any_membership_role, to_bool_or_none
from boac.merged import calnet
from boac.merged.user_session import UserSession
from boac.models.authorized_user import AuthorizedUser
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.university_dept import UniversityDept
from boac.models.university_dept_member import UniversityDeptMember
from flask import current_app as app, request
from flask_login import current_user, login_required, login_user


@app.route('/api/profile/my')
def my_profile():
    return tolerant_jsonify(get_current_user_profile())


@app.route('/api/user/calnet_profile/by_csid/<csid>')
@advisor_required
def calnet_profile_by_csid(csid):
    return tolerant_jsonify(calnet.get_calnet_user_for_csid(app, csid))


@app.route('/api/user/calnet_profile/by_uid/<uid>')
@advisor_required
def calnet_profile_by_uid(uid):
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, uid))


@app.route('/api/user/calnet_profile/by_user_id/<user_id>')
@advisor_required
def calnet_profile_by_user_id(user_id):
    user = AuthorizedUser.find_by_id(user_id, include_deleted=True)
    if user:
        return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, user.uid))
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


@app.route('/api/user/session_keep_alive')
@login_required
def session_keep_alive():
    return tolerant_jsonify(current_user.to_api_json())


@app.route('/api/users', methods=['POST'])
@admin_required
def all_users():
    params = request.get_json()
    users, total_user_count = AuthorizedUser.get_users(
        dept_code=util.get(params, 'deptCode', None),
        role=util.get(params, 'role', None) or None,
        status=util.get(params, 'status'),
    )
    return tolerant_jsonify(authorized_users_api_feed(
        users,
        sort_by=util.get(params, 'sortBy', 'lastName'),
        sort_descending=to_bool_or_none(util.get(params, 'sortDescending', False)),
    ))


@app.route('/api/users/admins', methods=['POST'])
@admin_required
def get_admin_users():
    params = request.get_json()
    users = AuthorizedUser.get_admin_users(status=util.get(params, 'status'))
    return tolerant_jsonify(authorized_users_api_feed(
        users,
        sort_by=util.get(params, 'sortBy'),
        sort_descending=to_bool_or_none(util.get(params, 'sortDescending')),
    ))


@app.route('/api/users/autocomplete', methods=['POST'])
@admin_required
def user_search():
    users = []
    snippet = request.get_json().get('snippet', '').strip()
    if snippet:
        search_by_uid = re.match(r'\d+', snippet)
        uids = AuthorizedUser.get_uids_like(snippet if search_by_uid else None)
        calnet_users = calnet.get_calnet_users_for_uids(app, uids)
        users = list(calnet_users.values())
        if not search_by_uid:
            any_ = r'.*'
            pattern = re.compile(any_ + any_.join(snippet.split()) + any_, re.IGNORECASE)
            users = list(filter(lambda u: u.get('name') and pattern.match(u['name']), users))
    api_json = []
    for user in users:
        name, uid = user['name'], user['uid']
        api_json.append({
            'name': f'{name} ({uid})' if name else uid,
            'uid': uid,
        })
    return tolerant_jsonify(api_json)


@app.route('/api/users/peer_advising', methods=['POST'])
@admin_required
def get_peer_advising_users():
    params = request.get_json()
    peer_advising_department_id = util.get(params, 'peerAdvisingDepartmentId', None)
    role = util.get(params, 'role', None) or None
    sort_by = util.get(params, 'sortBy', 'lastName')
    sort_descending = to_bool_or_none(util.get(params, 'sortDescending', False))

    users, total_user_count = AuthorizedUser.get_peer_advising_users(
        peer_advising_department_id=peer_advising_department_id,
        role=role,
        status=util.get(params, 'status'),
    )
    return tolerant_jsonify(authorized_users_api_feed(users, sort_by=sort_by, sort_descending=sort_descending))


@app.route('/api/user/create_or_update', methods=['POST'])
@admin_required
def create_or_update_user_profile():
    params = request.get_json()
    user = params.get('user', None)
    departments = user.get('departments') if user else None

    if not user or not user.get('uid') or departments is None:
        raise errors.BadRequestError('Required parameters are missing')

    authorized_user = _update_or_create_authorized_user(user=user)
    _delete_existing_memberships(authorized_user)
    _create_department_memberships(authorized_user, departments)

    if user.get('deletedAt') and not authorized_user.deleted_at:
        AuthorizedUser.delete(authorized_user.uid)
    elif not user.get('deletedAt') and authorized_user.deleted_at:
        AuthorizedUser.un_delete(authorized_user.uid)

    user_id = authorized_user.id
    UserSession.flush_cache_for_id(user_id)
    updated_user = AuthorizedUser.find_by_id(user_id, include_deleted=True)
    api_json = authorized_users_api_feed([updated_user])[0]
    return tolerant_jsonify(api_json)


@app.route('/api/user/demo_mode', methods=['POST'])
@advisor_or_peer_advisor_required
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
@advisor_required
def get_departments():
    def _to_api_json(department):
        return {
            'id': department['id'],
            'deptCode': department['dept_code'],
            'deptName': department['dept_name'],
            'memberCount': department['member_count'],
            'peerAdvisingDepartments': department['peer_advising_departments'],
        }
    exclude_empty = to_bool_or_none(util.get(request.args, 'excludeEmpty')) or False
    departments = UniversityDept.get_all_departments(exclude_empty=exclude_empty)
    department_other = next((d for d in departments if d['dept_name'].lower() == 'other'), None)
    if department_other:
        # Move 'Other' department to the end of the list
        departments.append(departments.pop(departments.index(department_other)))
    return tolerant_jsonify([_to_api_json(d) for d in departments])


def _get_boa_users():
    users = []
    admin_pseudo_department = {'deptCode': 'ADMIN', 'deptName': 'Admins', 'memberships': [{'role': 'Admin'}]}
    for user in authorized_users_api_feed(AuthorizedUser.get_all_active_users()):
        departments = [admin_pseudo_department] if user.get('isAdmin') else user.get('departments')
        for department in departments:
            for membership in department['memberships']:
                department_description = f"{department['deptCode']}: {membership['role']}"
                if 'automateMembership' in membership:
                    department_description += f" (automated={membership['automateMembership'] is True})"
                users.append({
                    'last_name': user.get('lastName') or '',
                    'first_name': user.get('firstName') or '',
                    'uid': user.get('uid'),
                    'title': user.get('title'),
                    'email': user.get('campusEmail') or user.get('email'),
                    'department': f'{{ {department_description} }}',
                    'can_access_advising_data': user.get('canAccessAdvisingData'),
                    'can_access_canvas_data': user.get('canAccessCanvasData'),
                    'is_blocked': user.get('isBlocked'),
                    'last_login': user.get('lastLogin'),
                })
    return users


def _update_or_create_authorized_user(user):
    user_id = user.get('id')
    automate_degree_progress_permission = user.get('automateDegreeProgressPermission')
    can_access_canvas_data = to_bool_or_none(user.get('canAccessCanvasData'))
    can_access_advising_data = to_bool_or_none(user.get('canAccessAdvisingData'))
    degree_progress_permission = user.get('degreeProgressPermission')
    departments = user.get('departments')
    dept_codes = [d['deptCode'] for d in departments]

    if (automate_degree_progress_permission or degree_progress_permission) and 'COENG' not in dept_codes:
        raise errors.BadRequestError('Degree Progress feature is only available to the College of Engineering.')
    if is_peer_advisor(user):
        if len(departments) > 1:
            raise errors.BadRequestError('Peer Advisor cannot belong to multiple departments.')
        if has_any_membership_role(user, 'advisor', 'director', 'peer_advisor_manager'):
            raise errors.BadRequestError('Peer Advisor cannot play other roles.')
        if can_access_canvas_data or can_access_advising_data:
            raise errors.BadRequestError('Peer Advisors are not allowed to access canvas or advising data.')
    if is_peer_advisor_manager(user) and not can_access_advising_data:
        raise errors.BadRequestError('Peer Advisor Managers must have access to advising data.')

    is_admin = to_bool_or_none(user.get('isAdmin'))
    is_blocked = to_bool_or_none(user.get('isBlocked'))
    if user_id:
        user = AuthorizedUser.update_user(
            automate_degree_progress_permission=automate_degree_progress_permission,
            can_access_advising_data=can_access_advising_data,
            can_access_canvas_data=can_access_canvas_data,
            degree_progress_permission=degree_progress_permission,
            include_deleted=True,
            is_admin=is_admin,
            is_blocked=is_blocked,
            user_id=user_id,
        )
        UserSession.flush_cache_for_id(user_id=user_id)
        return user
    else:
        uid = user.get('uid')
        if AuthorizedUser.get_id_per_uid(uid, include_deleted=True):
            raise errors.BadRequestError(f'User with UID {uid} is already in the BOA database.')

        calnet_user = calnet.get_calnet_user_for_uid(app, uid, skip_expired_users=True)
        if calnet_user and calnet_user.get('csid', None):
            return AuthorizedUser.create_or_restore(
                automate_degree_progress_permission=automate_degree_progress_permission,
                can_access_advising_data=can_access_advising_data,
                can_access_canvas_data=can_access_canvas_data,
                created_by=current_user.uid,
                degree_progress_permission=degree_progress_permission,
                is_admin=is_admin,
                is_blocked=is_blocked,
                uid=uid,
            )
        else:
            raise errors.BadRequestError('Invalid UID')


def _create_department_memberships(authorized_user, departments):
    valid_roles = ('advisor', 'director', 'peer_advisor', 'peer_advisor_manager')
    for department in departments:
        for membership in [m for m in department['memberships'] if m['role'] in valid_roles]:
            role = membership['role']
            university_dept = UniversityDept.find_by_dept_code(department['deptCode'])
            if role in ['advisor', 'director']:
                UniversityDeptMember.create_or_update_membership(
                    automate_membership=to_bool_or_none(membership['automateMembership']),
                    authorized_user_id=authorized_user.id,
                    role=role,
                    university_dept_id=university_dept.id,
                )
            elif role in ['peer_advisor', 'peer_advisor_manager']:
                for peer_advising_dept in PeerAdvisingDepartment.find_by_university_dept_id(university_dept.id):
                    PeerAdvisingDepartmentMember.create_or_update_membership(
                        authorized_user_id=authorized_user.id,
                        peer_advising_department_id=peer_advising_dept.id,
                        role_type=role,
                    )
    UserSession.flush_cache_for_id(authorized_user.id)


def _delete_existing_memberships(authorized_user):
    existing_memberships = UniversityDeptMember.get_existing_memberships(authorized_user_id=authorized_user.id)
    for university_dept_id in [m.university_dept.id for m in existing_memberships]:
        UniversityDeptMember.delete_membership(
            authorized_user_id=authorized_user.id,
            university_dept_id=university_dept_id,
        )
    for m in PeerAdvisingDepartmentMember.get_peer_advising_department_memberships(authorized_user_id=authorized_user.id):
        PeerAdvisingDepartmentMember.delete_membership(
            authorized_user_id=authorized_user.id,
            peer_advising_department_id=m['peer_advising_department_id'],
        )


def _find_user_by_uid(uid, ignore_deleted=True):
    if uid:
        ignore_deleted_ = True if ignore_deleted is None else ignore_deleted
        return AuthorizedUser.find_by_uid(uid, ignore_deleted=ignore_deleted_)
    else:
        return None
