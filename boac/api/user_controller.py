"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.api.util import admin_required, authorized_users_api_feed
from boac.lib.berkeley import BERKELEY_DEPT_NAME_TO_CODE, get_dept_codes
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_cohort import CuratedCohort
from flask import current_app as app
from flask_login import current_user, login_required


@app.route('/api/profile/my')
def my_profile():
    uid = current_user.get_id()
    profile = calnet.get_calnet_user_for_uid(app, uid)
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
        filtered_cohorts = []
        for cohort in CohortFilter.summarize_alert_counts_in_all_owned_by(uid):
            cohort['isOwnedByCurrentUser'] = True
            filtered_cohorts.append(cohort)
        curated_cohorts = []
        user_id = current_user.id
        for cohort in CuratedCohort.get_curated_cohorts_by_owner_id(user_id):
            _curated_cohort_api_json(cohort)
            students = [{'sid': s.sid} for s in cohort.students]
            students_with_alerts = Alert.include_alert_counts_for_students(viewer_user_id=user_id, cohort={'students': students})
            curated_cohorts.append({
                'id': cohort.id,
                'name': cohort.name,
                'alertCount': sum(s['alertCount'] for s in students_with_alerts),
                'studentCount': len(students),
            })
        profile.update({
            'myFilteredCohorts': filtered_cohorts,
            'myCuratedCohorts': curated_cohorts,
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


@app.route('/api/profiles/authorized_user_groups')
@admin_required
def authorized_user_groups():
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
        dept['users'] = authorized_users_api_feed(dept['users'])
        user_groups.append(dept)
    return tolerant_jsonify(user_groups)


def _curated_cohort_api_json(cohort):
    api_json = {
        'id': cohort.id,
        'name': cohort.name,
        'sids': [],
        'studentCount': 0,
    }
    for student in cohort.students:
        api_json['sids'].append(student.sid)
        api_json['studentCount'] += 1
    return api_json
