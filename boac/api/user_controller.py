from boac.api import errors
from boac.externals import canvas
from boac.lib.analytics import course_analytics_for_user
from boac.lib.http import tolerant_jsonify
from boac.models.cohort import Cohort

from flask import current_app as app
from flask_login import current_user, login_required


@app.route('/api/profile')
def user_profile():
    canvas_profile = False
    if current_user.is_active:
        uid = current_user.get_id()
        canvas_response = canvas.get_user_for_uid(app.canvas_instance, uid)
        if canvas_response:
            canvas_profile = canvas_response.json()
        elif (canvas_response.raw_response is None) or (canvas_response.raw_response.status_code != 404):
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
    canvas_profile = canvas.get_user_for_uid(app.canvas_instance, uid)
    if not canvas_profile:
        if (canvas_profile.raw_response is not None) and (canvas_profile.raw_response.status_code == 404):
            raise errors.ResourceNotFoundError('No Canvas profile found for user')
        else:
            raise errors.InternalServerError('Unable to reach bCourses')
    canvas_id = canvas_profile.json()['id']

    course_analytics_feed = course_analytics_for_user(uid, canvas_id)

    cohort_data = Cohort.query.filter_by(member_uid=uid).first()
    if cohort_data:
        cohort_data = cohort_data.to_api_json()

    return tolerant_jsonify({
        'uid': uid,
        'canvasProfile': canvas_profile.json(),
        'cohortData': cohort_data,
        'courses': course_analytics_feed,
    })
