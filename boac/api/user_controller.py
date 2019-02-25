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
from boac.api.util import admin_required, authorized_users_api_feed, get_current_user_status, get_my_cohorts, get_my_curated_groups
from boac.lib import util
from boac.lib.berkeley import BERKELEY_DEPT_NAME_TO_CODE, get_dept_codes
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.models.authorized_user import AuthorizedUser
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/profile/my')
def my_profile():
    profile = get_current_user_status()
    if current_user.is_authenticated:
        profile['id'] = current_user.id
        uid = current_user.get_id()
        profile.update(calnet.get_calnet_user_for_uid(app, uid))
        if current_user.is_active:
            departments = {}
            for m in current_user.department_memberships:
                departments.update({
                    m.university_dept.dept_code: {
                        'isAdvisor': m.is_advisor,
                        'isDirector': m.is_director,
                    },
                })
            dept_codes = get_dept_codes(current_user)
            profile['isAsc'] = 'UWASC' in dept_codes
            profile['isCoe'] = 'COENG' in dept_codes
            exclude_cohorts = util.to_bool_or_none(request.args.get('excludeCohorts'))
            if not exclude_cohorts:
                profile.update({
                    'myFilteredCohorts': get_my_cohorts(),
                    'myCuratedCohorts': get_my_curated_groups(),
                })
            profile.update({
                'isAdmin': current_user.is_admin,
                'inDemoMode': current_user.in_demo_mode if hasattr(current_user, 'in_demo_mode') else False,
                'departments': departments,
            })
    return tolerant_jsonify(profile)


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


@app.route('/api/user/<user_id>')
@login_required
def user_by_id(user_id):
    user = AuthorizedUser.find_by_id(user_id)
    if not user:
        raise errors.ResourceNotFoundError('Unknown path')
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, user.uid))


@app.route('/api/users/authorized_groups')
@admin_required
def authorized_user_groups():
    sort_users_by = util.get(request.args, 'sortUsersBy', None)
    depts = {}
    for dept_name, dept_code in {**{'Admins': 'ADMIN'}, **BERKELEY_DEPT_NAME_TO_CODE}.items():
        depts[dept_code] = {
            'code': dept_code,
            'name': dept_name,
            'users': [],
        }
    for user in AuthorizedUser.query.all():
        if user.is_admin:
            depts['ADMIN']['users'].append(user)
        for m in user.department_memberships:
            depts[m.university_dept.dept_code]['users'].append(user)
    user_groups = []
    for dept_code, dept in depts.items():
        dept['users'] = authorized_users_api_feed(dept['users'], sort_users_by)
        user_groups.append(dept)
    return tolerant_jsonify(user_groups)


@app.route('/api/user/demo_mode', methods=['POST'])
@admin_required
def set_demo_mode():
    in_demo_mode = request.get_json().get('demoMode', None)
    if in_demo_mode is None:
        raise errors.BadRequestError('Parameter \'demoMode\' not found')
    user = AuthorizedUser.find_by_id(current_user.id)
    user.in_demo_mode = bool(in_demo_mode)
    return tolerant_jsonify({
        'inDemoMode': user.in_demo_mode,
    })


@app.route('/api/user/status')
def user_status():
    return tolerant_jsonify(get_current_user_status())
