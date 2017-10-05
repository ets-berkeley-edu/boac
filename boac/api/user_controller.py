import re

from boac.api import errors
import boac.api.util as api_util
from boac.externals import canvas
from boac.externals import sis_enrollments_api
from boac.lib.analytics import merge_analytics_for_user
from boac.lib.berkeley import sis_term_id_for_name
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

    user_courses = canvas.get_user_courses(app.canvas_instance, uid)
    courses_api_feed = api_util.canvas_courses_api_feed(user_courses)

    cohort_data = Cohort.query.filter_by(member_uid=uid).first()
    if cohort_data and len(user_courses):
        term_id = sis_term_id_for_name(user_courses[0].get('term', {}).get('name'))
        merge_sis_enrollments(courses_api_feed, cohort_data.member_csid, term_id)

    merge_analytics_for_user(courses_api_feed, canvas_id)

    if cohort_data:
        cohort_data = cohort_data.to_api_json()

    return tolerant_jsonify({
        'uid': uid,
        'canvasProfile': canvas_profile.json(),
        'cohortData': cohort_data,
        'courses': courses_api_feed,
    })


def merge_sis_enrollments(canvas_course_sites, cs_id, term_id):
    # TODO For the moment, we're returning Canvas courses only for the current term as defined in
    # app config. Once we start grabbing multiple terms, we'll need additional sorting logic.
    enrollments = sis_enrollments_api.get_enrollments(cs_id, term_id)
    if enrollments:
        enrollments = enrollments.json().get('apiResponse', {}).get('response', {}).get('studentEnrollments', [])
    else:
        return

    for site in canvas_course_sites:
        site['sisEnrollments'] = []
        sections = canvas.get_course_sections(app.canvas_instance, site['canvasCourseId'])
        if not sections:
            continue
        for section in sections:
            ccn_match = re.match(r'\ASEC:20\d{2}-[BCD]-(\d{5})\Z', section.get('sis_section_id'))
            if ccn_match:
                canvas_ccn = ccn_match.group(1)
            if not canvas_ccn:
                continue
            for enrollment in enrollments:
                sis_ccn = str(enrollment.get('classSection', {}).get('id'))
                if canvas_ccn == sis_ccn:
                    site['sisEnrollments'].append(api_util.sis_enrollment_api_feed(enrollment))
                    break
