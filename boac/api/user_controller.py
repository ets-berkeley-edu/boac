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
    authorized_user = uid and AuthorizedUser.find_by_uid(uid)
    if authorized_user:
        users_feed = authorized_users_api_feed([authorized_user])
        return tolerant_jsonify(users_feed[0])
    else:
        app.logger.error(f'No user found for CS ID {csid}')
        return tolerant_jsonify(None)


@app.route('/api/user/by_uid/<uid>')
@advisor_required
def user_by_uid(uid):
    user = AuthorizedUser.find_by_uid(uid)
    if user:
        users_feed = authorized_users_api_feed([user])
        return tolerant_jsonify(users_feed[0])
    else:
        app.logger.error(f'No user found for UID {uid}')
        return tolerant_jsonify(None)


@app.route('/api/user/dept_membership/add', methods=['POST'])
@admin_required
def add_university_dept_membership():
    params = request.get_json() or {}
    dept = UniversityDept.find_by_dept_code(params.get('deptCode', None))
    user = AuthorizedUser.find_by_uid(params.get('uid', None))
    membership = UniversityDeptMember.create_or_update_membership(
        university_dept=dept,
        authorized_user=user,
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
        blocked=to_bool_or_none(util.get(params, 'blocked', None)),
        deleted=to_bool_or_none(util.get(params, 'deleted', None)),
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
        users = AuthorizedUser.users_with_uid_like(snippet) if search_by_uid else AuthorizedUser.get_all_active_users()
        users = list(calnet.get_calnet_users_for_uids(app, [u.uid for u in users]).values())
        if not search_by_uid:
            any_ = r'.*'
            pattern = re.compile(any_ + any_.join(snippet.split()) + any_, re.IGNORECASE)
            users = list(filter(lambda u: u.get('name') and pattern.match(u['name']), users))
    else:
        users = []
    return tolerant_jsonify([{'label': u['name'], 'uid': u['uid']} for u in users])


@app.route('/api/users/drop_in_advisors/<dept_code>')
@scheduler_required
def drop_in_advisors_for_dept(dept_code):
    return tolerant_jsonify(drop_in_advisors_for_dept_code(dept_code))


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
    rows = []
    for dept in _get_boa_user_groups():
        for user in dept['users']:
            rows.append(
                {
                    'last_name': user.get('lastName') or '',
                    'first_name': user.get('firstName') or '',
                    'uid': user.get('uid'),
                    'email': user.get('campusEmail') or user.get('email'),
                    'dept_code': dept.get('code'),
                    'dept_name': dept.get('name'),
                },
            )
    return response_with_csv_download(
        rows=sorted(rows, key=lambda row: row['last_name'].upper()),
        filename_prefix='boa_users',
        fieldnames=['last_name', 'first_name', 'uid', 'email', 'dept_code', 'dept_name'],
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


def _user_by_uid(uid):
    user = AuthorizedUser.find_by_uid(uid)
    return user and authorized_users_api_feed([user])[0]
