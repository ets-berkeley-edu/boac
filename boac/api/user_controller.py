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
from boac.externals import data_loch
from boac.externals.cal1card_photo_api import get_cal1card_photo
from boac.lib import util
from boac.lib.analytics import merge_analytics_for_user
from boac.lib.berkeley import sis_term_id_for_name
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.merged.sis_enrollments import merge_sis_enrollments
from boac.merged.sis_profile import merge_sis_profile
from boac.models.alert import Alert
from boac.models.cohort_filter import CohortFilter
from boac.models.normalized_cache_student_major import NormalizedCacheStudentMajor
from boac.models.student import Student
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
            api_util.sort_students_by_name(group['students'])
        departments = {}
        for m in current_user.department_memberships:
            departments.update({
                m.university_dept.dept_code: {
                    'isAdvisor': m.is_advisor,
                    'isDirector': m.is_director,
                },
            })
        profile.update({
            'myCohorts': CohortFilter.all_owned_by(uid, include_alerts=True),
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
    canvas_profile = data_loch.get_user_for_uid(uid)
    if canvas_profile is False:
        raise errors.ResourceNotFoundError('No Canvas profile found for user')
    canvas_id = canvas_profile['canvas_id']

    student = Student.query.filter_by(uid=uid).first()
    if student:
        sis_profile = merge_sis_profile(student.sid)
        athletics_profile = student.to_expanded_api_json()
    else:
        sis_profile = False
        athletics_profile = False

    user_courses = data_loch.get_student_canvas_courses(uid) or []
    if student and sis_profile:
        # CalCentral's Student Overview page is advisors' official information source for the student.
        student_profile_link = f'https://calcentral.berkeley.edu/user/overview/{uid}'
        canvas_courses_feed = api_util.canvas_courses_api_feed(user_courses)
        enrollment_terms = merge_sis_enrollments(canvas_courses_feed, uid, student.sid, sis_profile.get('matriculation'))
    else:
        student_profile_link = None
        enrollment_terms = []

    current_term_id = sis_term_id_for_name(app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])
    has_enrollments_in_current_term = False
    for term in enrollment_terms:
        term_id = sis_term_id_for_name(term['termName'])
        if term_id == current_term_id:
            has_enrollments_in_current_term = True
        for enrollment in term['enrollments']:
            merge_analytics_for_user(enrollment['canvasSites'], canvas_id, term_id)
        merge_analytics_for_user(term['unmatchedCanvasSites'], canvas_id, term_id)

    return tolerant_jsonify({
        'sid': student.sid if student else None,
        'uid': uid,
        'athleticsProfile': athletics_profile,
        'canvasProfile': canvas_profile,
        'sisProfile': sis_profile,
        'studentProfileLink': student_profile_link,
        'enrollmentTerms': enrollment_terms,
        'hasCurrentTermEnrollments': has_enrollments_in_current_term,
    })


@app.route('/api/majors/relevant')
def relevant_majors():
    return tolerant_jsonify(NormalizedCacheStudentMajor.distinct_majors())


@app.route('/api/user/<uid>/photo')
@login_required
def user_photo(uid):
    if util.app_in_demo_mode():
        raise errors.ResourceNotFoundError('Photos are not served in demo mode.')

    student = Student.query.filter_by(uid=uid).first()
    if not student:
        raise errors.ResourceNotFoundError('No student was found for the requested id.')
    photo = get_cal1card_photo(uid)
    if photo:
        return Response(photo, mimetype='image/jpeg')
    else:
        raise errors.ResourceNotFoundError('No photo was found for the requested id.')
