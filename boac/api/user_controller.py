from boac.api import errors
import boac.api.util as api_util
from boac.externals import canvas
from boac.lib.analytics import merge_analytics_for_user
from boac.lib.berkeley import sis_term_id_for_name
from boac.lib.http import tolerant_jsonify
from boac.lib.merged import merge_sis_enrollments, merge_sis_profile
from boac.models.team_member import TeamMember
from flask import current_app as app
from flask_login import current_user, login_required


@app.route('/api/profile')
def user_profile():
    canvas_profile = False
    if current_user.is_active:
        uid = current_user.get_id()
        canvas_response = canvas.get_user_for_uid(uid)
        if canvas_response:
            canvas_profile = canvas_response
        elif canvas_response is None:
            canvas_profile = {
                'error': 'Unable to reach bCourses',
            }
    else:
        uid = False
    return tolerant_jsonify({
        'uid': uid,
        'canvas_profile': canvas_profile,
    })


@app.route('/api/user/<uid>/analytics')
@login_required
def user_analytics(uid):
    canvas_profile = canvas.get_user_for_uid(uid)
    if canvas_profile is False:
        raise errors.ResourceNotFoundError('No Canvas profile found for user')
    elif not canvas_profile:
        raise errors.InternalServerError('Unable to reach bCourses')
    canvas_id = canvas_profile['id']

    user_courses = canvas.get_student_courses_in_term(uid)
    courses_api_feed = api_util.canvas_courses_api_feed(user_courses)

    cohort_data = TeamMember.query.filter_by(member_uid=uid).first()
    if cohort_data and len(user_courses):
        term_id = sis_term_id_for_name(user_courses[0].get('term', {}).get('name'))
        merge_sis_enrollments(courses_api_feed, cohort_data.member_csid, term_id)

    merge_analytics_for_user(courses_api_feed, canvas_id)

    if cohort_data:
        sis_profile = merge_sis_profile(cohort_data.member_csid)
        cohort_data = cohort_data.to_api_json()
    else:
        sis_profile = False

    return tolerant_jsonify({
        'uid': uid,
        'canvasProfile': canvas_profile,
        'cohortData': cohort_data,
        'courses': courses_api_feed,
        'sisProfile': sis_profile,
    })
