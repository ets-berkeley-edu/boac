from boac.api import errors
import boac.api.util as api_util
from boac.externals import canvas
from boac.externals.cal1card_photo_api import get_cal1card_photo
from boac.lib import util
from boac.lib.analytics import merge_analytics_for_user
from boac.lib.berkeley import sis_term_id_for_name
from boac.lib.http import tolerant_jsonify
from boac.merged import member_details
from boac.merged.sis_enrollments import merge_sis_enrollments
from boac.merged.sis_profile import merge_sis_profile
from boac.models.normalized_cache_student_major import NormalizedCacheStudentMajor
from boac.models.student import Student
from flask import current_app as app, request, Response
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
    return tolerant_jsonify(Student.get_all(order_by=order_by))


@app.route('/api/students', methods=['POST'])
@login_required
def get_students():
    params = request.get_json()
    gpa_ranges = util.get(params, 'gpaRanges')
    group_codes = util.get(params, 'groupCodes')
    levels = util.get(params, 'levels')
    majors = util.get(params, 'majors')
    unit_ranges_eligibility = util.get(params, 'unitRangesEligibility')
    unit_ranges_pacing = util.get(params, 'unitRangesPacing')
    order_by = util.get(params, 'orderBy', None)
    offset = util.get(params, 'offset', 0)
    limit = util.get(params, 'limit', 50)
    results = Student.get_students(gpa_ranges=gpa_ranges, group_codes=group_codes, levels=levels, majors=majors,
                                   unit_ranges_eligibility=unit_ranges_eligibility,
                                   unit_ranges_pacing=unit_ranges_pacing, order_by=order_by, offset=offset, limit=limit)
    member_details.merge_all(results['students'])
    return tolerant_jsonify({
        'members': results['students'],
        'totalMemberCount': results['totalStudentCount'],
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

    student = Student.query.filter_by(uid=uid).first()
    if student:
        sis_profile = merge_sis_profile(student.sid)
        athletics_profile = student.to_expanded_api_json()
    else:
        sis_profile = False
        athletics_profile = False

    user_courses = canvas.get_student_courses(uid) or []
    if student and sis_profile:
        # CalCentral's Student Overview page is advisors' official information source for the student.
        student_profile_link = 'https://calcentral.berkeley.edu/user/overview/{}'.format(uid)
        canvas_courses_feed = api_util.canvas_courses_api_feed(user_courses)
        enrollment_terms = merge_sis_enrollments(canvas_courses_feed, student.sid, sis_profile.get('matriculation'))
    else:
        student_profile_link = None
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
        'studentProfileLink': student_profile_link,
        'enrollmentTerms': enrollment_terms,
    })


@app.route('/api/majors/relevant')
def relevant_majors():
    return tolerant_jsonify(NormalizedCacheStudentMajor.distinct_majors())


@app.route('/api/user/<uid>/photo')
@login_required
def user_photo(uid):
    photo = get_cal1card_photo(uid)
    if photo:
        return Response(photo, mimetype='image/jpeg')
    else:
        raise errors.ResourceNotFoundError('No photo was found for the requested id.')


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
