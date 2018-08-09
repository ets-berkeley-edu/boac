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
from boac.api.util import admin_required, authorized_users_api_feed, can_current_user_view_dept, decorate_cohort
from boac.externals import data_loch
from boac.externals.cal1card_photo_api import get_cal1card_photo
from boac.lib.berkeley import get_dept_codes
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.merged.student import get_student_and_terms, get_student_query_scope
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_cohort import CuratedCohort
from boac.models.university_dept import UniversityDept
from flask import current_app as app, Response
from flask_login import current_user, login_required


@app.route('/api/profile/my')
def my_profile():
    uid = current_user.get_id()
    profile = calnet.get_calnet_user_for_uid(app, uid)
    if current_user.is_active:
        authorized_user_id = current_user.id
        curated_cohorts = CuratedCohort.get_curated_cohorts_by_owner_id(authorized_user_id)
        curated_cohorts = [c.to_api_json(sids_only=True) for c in curated_cohorts]
        departments = {}
        for m in current_user.department_memberships:
            departments.update({
                m.university_dept.dept_code: {
                    'isAdvisor': m.is_advisor,
                    'isDirector': m.is_director,
                },
            })
        my_cohorts = CohortFilter.all_owned_by(uid)
        profile.update({
            'myFilteredCohorts': [decorate_cohort(c, include_students=False) for c in my_cohorts],
            'myCuratedCohorts': curated_cohorts,
            'isAdmin': current_user.is_admin,
            'departments': departments,
        })
    else:
        profile.update({
            'myFilteredCohorts': None,
            'myCuratedCohorts': None,
            'isAdmin': False,
            'departments': None,
        })
    return tolerant_jsonify(profile)


@app.route('/api/profile/<uid>')
@login_required
def user_profile(uid):
    match = next((u for u in AuthorizedUser.query.all() if u.uid == uid), None)
    if not match:
        raise errors.ResourceNotFoundError('Unknown path')
    return tolerant_jsonify(calnet.get_calnet_user_for_uid(app, uid))


@app.route('/api/profiles/all')
@admin_required
def all_user_profiles():
    # This feature is not available in production
    if app.config['DEVELOPER_AUTH_ENABLED']:
        users = AuthorizedUser.query.all()
        return tolerant_jsonify(authorized_users_api_feed(users))
    else:
        raise errors.ResourceNotFoundError('Unknown path')


@app.route('/api/profiles/dept/<dept_code>')
@login_required
def all_user_profiles_of_dept(dept_code):
    dept = UniversityDept.find_by_dept_code(dept_code=dept_code)
    if dept:
        if can_current_user_view_dept(dept_code):
            users = list(filter(lambda user: dept_code in get_dept_codes(user), AuthorizedUser.query.all()))
            return tolerant_jsonify(authorized_users_api_feed(users))
        else:
            raise errors.ForbiddenRequestError(f'{current_user.uid} is not authorized to access {dept_code}')
    else:
        raise errors.ResourceNotFoundError('Unknown path')


@app.route('/api/user/<uid>/analytics')
@login_required
def user_analytics(uid):
    feed = get_student_and_terms(uid)
    if not feed:
        raise errors.ResourceNotFoundError('Unknown student')
    # CalCentral's Student Overview page is advisors' official information source for the student.
    feed['studentProfileLink'] = f'https://calcentral.berkeley.edu/user/overview/{uid}'
    return tolerant_jsonify(feed)


@app.route('/api/majors/relevant')
def relevant_majors():
    majors = [row['major'] for row in data_loch.get_majors(get_student_query_scope())]
    return tolerant_jsonify(majors)


@app.route('/api/user/<uid>/photo')
@login_required
def user_photo(uid):
    photo = get_cal1card_photo(uid)
    if photo:
        return Response(photo, mimetype='image/jpeg')
    else:
        # Status is NO_DATA
        return Response('', status=204)
