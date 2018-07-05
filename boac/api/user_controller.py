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
import boac.api.util as api_util
from boac.api.util import decorate_cohort
from boac.externals import data_loch
from boac.externals.cal1card_photo_api import get_cal1card_photo
from boac.lib import util
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.merged.student import get_student_and_terms
from boac.models.alert import Alert
from boac.models.cohort_filter import CohortFilter
from boac.models.student_group import StudentGroup
from flask import current_app as app, Response
from flask_login import current_user, login_required


@app.route('/api/profile')
def user_profile():
    uid = current_user.get_id()
    profile = calnet.get_calnet_user_for_uid(app, uid)
    if current_user.is_active:
        # All BOAC views require group and cohort lists
        authorized_user_id = current_user.id
        alert_counts = Alert.current_alert_counts_for_viewer(current_user.id)
        groups = StudentGroup.get_groups_by_owner_id(authorized_user_id)
        groups = [g.to_api_json() for g in groups]
        for group in groups:
            api_util.add_alert_counts(alert_counts, group['students'])
            group['students'] = api_util.sort_students_by_name(group['students'])
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
            'myCohorts': [decorate_cohort(c, include_alerts_for_uid=uid, include_students=False) for c in my_cohorts],
            'myGroups': groups,
            'isAdmin': current_user.is_admin,
            'departments': departments,
        })
    else:
        profile.update({
            'myCohorts': None,
            'myGroups': None,
            'isAdmin': False,
            'departments': None,
        })
    return tolerant_jsonify(profile)


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
    majors = [row['major'] for row in data_loch.get_majors()]
    return tolerant_jsonify(majors)


@app.route('/api/user/<uid>/photo')
@login_required
def user_photo(uid):
    if util.app_in_demo_mode():
        raise errors.ResourceNotFoundError('Photos are not served in demo mode.')
    photo = get_cal1card_photo(uid)
    if photo:
        return Response(photo, mimetype='image/jpeg')
    else:
        raise errors.ResourceNotFoundError('No photo was found for the requested id.')
