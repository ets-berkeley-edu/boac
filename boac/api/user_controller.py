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

from boac.api import errors
from boac.api.util import admin_required, advisor_required, authorized_users_api_feed
from boac.lib import util
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.http import response_with_csv_download, tolerant_jsonify
from boac.merged import calnet
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
    return tolerant_jsonify(calnet.get_calnet_user_for_csid(app, csid))


@app.route('/api/user/by_uid/<uid>')
@advisor_required
def user_by_uid(uid):
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, uid))


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
        is_drop_in_advisor=params.get('isDropInAdvisor', False),
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
        is_drop_in_advisor=params.get('isDropInAdvisor', False),
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


@app.route('/api/users/all')
@admin_required
def all_users():
    sort_users_by = util.get(request.args, 'sortUsersBy', None)
    return tolerant_jsonify(_get_boa_users(sort_users_by))


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


def _get_boa_users(sort_user_by=None):
    users = AuthorizedUser.get_all_users()
    return authorized_users_api_feed(users, sort_user_by)


def _get_boa_user_groups(sort_users_by=None):
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
        dept['users'] = authorized_users_api_feed(dept['users'], sort_users_by)
        user_groups.append(dept)
    return sorted(user_groups, key=lambda dept: dept['name'])
