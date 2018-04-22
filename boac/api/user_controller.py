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
from boac.api.errors import BadRequestError
import boac.api.util as api_util
from boac.externals import canvas
from boac.externals.cal1card_photo_api import get_cal1card_photo
from boac.lib import util
from boac.lib.analytics import merge_analytics_for_user
from boac.lib.berkeley import is_department_advisor, sis_term_id_for_name
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.merged import member_details
from boac.merged.sis_enrollments import merge_sis_enrollments
from boac.merged.sis_profile import merge_sis_profile
from boac.models.cohort_filter import CohortFilter
from boac.models.normalized_cache_student_major import NormalizedCacheStudentMajor
from boac.models.student import Student
from boac.models.student_group import StudentGroup
from flask import current_app as app, request, Response
from flask_login import current_user, login_required


@app.route('/api/profile')
def user_profile():
    uid = current_user.get_id()
    profile = calnet.get_calnet_user_for_uid(app, uid)
    if current_user.is_active:
        # All BOAC views require group and cohort lists
        authorized_user_id = current_user.id
        groups = StudentGroup.get_groups_by_owner_id(authorized_user_id)
        groups = [_decorate_student_group(group) for group in groups]
        profile.update({
            'departmentMemberships': [api_util.department_membership_to_json(m) for m in current_user.department_memberships],
            'myCohorts': CohortFilter.all_owned_by(uid, include_alerts=True),
            'myGroups': groups,
            'personalization': {
                'showAthletics': current_user.is_admin or is_department_advisor('UWASC', current_user),
            },
        })
    else:
        profile.update({
            'departmentMemberships': None,
            'myCohorts': None,
            'myGroups': None,
            'personalization': None,
        })
    return tolerant_jsonify(profile)


@app.route('/api/students/all')
def all_students():
    order_by = request.args['orderBy'] if 'orderBy' in request.args else None
    return tolerant_jsonify(Student.get_all(order_by=order_by, is_active_asc=True))


@app.route('/api/students', methods=['POST'])
@login_required
def get_students():
    params = request.get_json()
    gpa_ranges = util.get(params, 'gpaRanges')
    group_codes = util.get(params, 'groupCodes')
    levels = util.get(params, 'levels')
    majors = util.get(params, 'majors')
    unit_ranges = util.get(params, 'unitRanges')
    in_intensive_cohort = util.to_bool_or_none(util.get(params, 'inIntensiveCohort'))
    is_inactive_asc = util.get(params, 'isInactive')
    order_by = util.get(params, 'orderBy', None)
    offset = util.get(params, 'offset', 0)
    limit = util.get(params, 'limit', 50)
    results = Student.get_students(
        gpa_ranges=gpa_ranges,
        group_codes=group_codes,
        levels=levels,
        majors=majors,
        unit_ranges=unit_ranges,
        in_intensive_cohort=in_intensive_cohort,
        is_active_asc=None if is_inactive_asc is None else not is_inactive_asc,
        order_by=order_by,
        offset=offset,
        limit=limit,
    )
    member_details.merge_all(results['students'])
    return tolerant_jsonify({
        'members': results['students'],
        'totalMemberCount': results['totalStudentCount'],
    })


@app.route('/api/students/search', methods=['POST'])
@login_required
def search_for_students():
    params = request.get_json()
    search_phrase = util.get(params, 'searchPhrase', '').strip()
    if not len(search_phrase):
        raise BadRequestError('Invalid or empty search input')
    order_by = util.get(params, 'orderBy', None)
    offset = util.get(params, 'offset', 0)
    limit = util.get(params, 'limit', 50)
    results = Student.search_for_students(
        search_phrase=search_phrase,
        order_by=order_by,
        offset=offset,
        limit=limit,
    )
    member_details.merge_all(results['students'])
    return tolerant_jsonify({
        'students': results['students'],
        'totalStudentCount': results['totalStudentCount'],
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
            merge_analytics_for_user(enrollment['canvasSites'], uid, student.sid, canvas_id, term_id)
        merge_analytics_for_user(term['unmatchedCanvasSites'], uid, student.sid, canvas_id, term_id)

    return tolerant_jsonify({
        'sid': student.sid if student else None,
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


def _decorate_student_group(group):
    decorated = api_util.decorate_student_groups(current_user_id=current_user.get_id(), groups=[group.to_api_json()])
    return decorated[0] if len(decorated) else None
