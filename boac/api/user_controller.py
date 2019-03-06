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
from boac.api.util import admin_required, authorized_users_api_feed, current_user_profile, get_current_user_status
from boac.lib import util
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.models.authorized_user import AuthorizedUser
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/profile/my')
def my_profile():
    exclude_cohorts = util.to_bool_or_none(request.args.get('excludeCohorts'))
    return tolerant_jsonify(current_user_profile(exclude_cohorts))


@app.route('/api/profile/<uid>')
@login_required
def user_profile(uid):
    match = next((u for u in AuthorizedUser.query.all() if u.uid == uid), None)
    if not match:
        raise errors.ResourceNotFoundError('Unknown path')
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, uid))


@app.route('/api/user/by_csid/<csid>')
@login_required
def calnet_profile(csid):
    return tolerant_jsonify(calnet.get_calnet_user_for_csid(app, csid))


@app.route('/api/user/by_uid/<uid>')
@login_required
def user_by_uid(uid):
    user = AuthorizedUser.find_by_uid(uid)
    if not user:
        raise errors.ResourceNotFoundError('Unknown path')
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, user.uid))


@app.route('/api/users/authorized_groups')
@admin_required
def authorized_user_groups():
    sort_users_by = util.get(request.args, 'sortUsersBy', None)
    depts = {}

    def _put(_dept_code, _user):
        if _dept_code not in depts:
            dept_name = 'Admins' if _dept_code == 'ADMIN' else BERKELEY_DEPT_CODE_TO_NAME.get(_dept_code)
            depts[_dept_code] = {
                'code': _dept_code,
                'name': dept_name,
                'users': [],
            }
        depts[_dept_code]['users'].append(_user)
    for user in AuthorizedUser.query.all():
        if user.is_admin:
            _put('ADMIN', user)
        for m in user.department_memberships:
            _put(m.university_dept.dept_code, user)
    user_groups = []
    for dept_code, dept in depts.items():
        dept['users'] = authorized_users_api_feed(dept['users'], sort_users_by)
        user_groups.append(dept)
    return tolerant_jsonify(user_groups)


@app.route('/api/user/demo_mode', methods=['POST'])
@login_required
def set_demo_mode():
    if app.config['DEVELOPER_AUTH_ENABLED']:
        in_demo_mode = request.get_json().get('demoMode', None)
        if in_demo_mode is None:
            raise errors.BadRequestError('Parameter \'demoMode\' not found')
        user = AuthorizedUser.find_by_id(current_user.id)
        user.in_demo_mode = bool(in_demo_mode)
        return tolerant_jsonify({
            'inDemoMode': user.in_demo_mode,
        })
    else:
        raise errors.ResourceNotFoundError('Unknown path')


@app.route('/api/user/status')
def user_status():
    return tolerant_jsonify(get_current_user_status())
