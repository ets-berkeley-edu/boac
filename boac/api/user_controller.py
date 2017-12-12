from boac.api import errors
import boac.api.util as api_util
from boac.externals import canvas
from boac.lib.analytics import merge_analytics_for_user
from boac.lib.berkeley import sis_term_id_for_name
from boac.lib.http import tolerant_jsonify
from boac.merged.sis_enrollments import merge_sis_enrollments
from boac.merged.sis_profile import merge_sis_profile
from boac.models.team_member import TeamMember
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/profile')
def user_profile():
    canvas_profile = False
    if current_user.is_active:
        uid = current_user.get_id()
        canvas_profile = load_canvas_profile(uid)
    else:
        uid = False
    return tolerant_jsonify({
        'uid': uid,
        'canvasProfile': canvas_profile,
    })


@app.route('/api/students/all')
def all_students():
    order_by = request.args['orderBy'] if 'orderBy' in request.args else None
    return tolerant_jsonify(TeamMember.get_all_athletes(order_by=order_by))


@app.route('/api/user/<uid>/analytics')
@login_required
def user_analytics(uid):
    canvas_profile = canvas.get_user_for_uid(uid)
    if canvas_profile is False:
        raise errors.ResourceNotFoundError('No Canvas profile found for user')
    elif not canvas_profile:
        raise errors.InternalServerError('Unable to reach bCourses')
    canvas_id = canvas_profile['id']

    team_member = TeamMember.query.filter_by(member_uid=uid).first()
    if team_member:
        sis_profile = merge_sis_profile(team_member.member_csid)
        athletics_profile = team_member.to_api_json()
    else:
        sis_profile = False
        athletics_profile = False

    user_courses = canvas.get_student_courses(uid) or []
    if team_member and sis_profile:
        canvas_courses_feed = api_util.canvas_courses_api_feed(user_courses)
        enrollment_terms = merge_sis_enrollments(canvas_courses_feed, team_member.member_csid, sis_profile.get('matriculation'))
    else:
        enrollment_terms = []

    for term in enrollment_terms:
        term_id = sis_term_id_for_name(term['termName'])
        for enrollment in term['enrollments']:
            merge_analytics_for_user(enrollment['canvasSites'], canvas_id, term_id)
        merge_analytics_for_user(term['unmatchedCanvasSites'], canvas_id, term_id)

    return tolerant_jsonify({
        'uid': uid,
        'athleticsProfile': athletics_profile,
        'canvasProfile': canvas_profile,
        'sisProfile': sis_profile,
        'enrollmentTerms': enrollment_terms,
    })


def load_canvas_profile(uid):
    canvas_profile = False
    canvas_response = canvas.get_user_for_uid(uid)
    if canvas_response:
        canvas_profile = canvas_response
    elif canvas_response is None:
        canvas_profile = {
            'error': 'Unable to reach bCourses',
        }
    return canvas_profile
