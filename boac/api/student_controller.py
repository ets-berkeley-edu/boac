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

from itertools import islice

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import add_alert_counts, get_dept_codes, is_asc_authorized, is_unauthorized_search
from boac.externals.cal1card_photo_api import get_cal1card_photo
from boac.externals.data_loch import get_enrolled_primary_sections
from boac.lib import util
from boac.lib.berkeley import current_term_id
from boac.lib.http import tolerant_jsonify
from boac.merged import athletics
from boac.merged.student import get_student_and_terms, query_students, search_for_students
from boac.models.alert import Alert
from flask import current_app as app, request, Response
from flask_login import current_user, login_required


@app.route('/api/student/<uid>/analytics')
@login_required
def user_analytics(uid):
    feed = get_student_and_terms(uid)
    if not feed:
        raise ResourceNotFoundError('Unknown student')
    # CalCentral's Student Overview page is advisors' official information source for the student.
    feed['studentProfileLink'] = f'https://calcentral.berkeley.edu/user/overview/{uid}'
    return tolerant_jsonify(feed)


@app.route('/api/student/<uid>/photo')
@login_required
def user_photo(uid):
    photo = get_cal1card_photo(uid)
    if photo:
        return Response(photo, mimetype='image/jpeg')
    else:
        # Status is NO_DATA
        return Response('', status=204)


@app.route('/api/students', methods=['POST'])
@login_required
def get_students():
    params = request.get_json()
    if is_unauthorized_search(params):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    results = query_students(
        advisor_ldap_uids=util.get(params, 'advisorLdapUids'),
        coe_prep_statuses=util.get(params, 'coePrepStatuses'),
        ethnicities=util.get(params, 'ethnicities'),
        genders=util.get(params, 'genders'),
        gpa_ranges=util.get(params, 'gpaRanges'),
        group_codes=util.get(params, 'groupCodes'),
        include_profiles=True,
        is_active_asc=_convert_asc_inactive_arg(util.get(params, 'isInactiveAsc')),
        in_intensive_cohort=util.to_bool_or_none(util.get(params, 'inIntensiveCohort')),
        last_name_range=_get_name_range_boundaries(util.get(params, 'lastNameRange')),
        levels=util.get(params, 'levels'),
        limit=util.get(params, 'limit', 50),
        majors=util.get(params, 'majors'),
        offset=util.get(params, 'offset', 0),
        order_by=util.get(params, 'orderBy', None),
        underrepresented=util.get(params, 'underrepresented'),
        unit_ranges=util.get(params, 'unitRanges'),
    )
    if results is None:
        raise BadRequestError('Invalid search criteria')
    alert_counts = Alert.current_alert_counts_for_viewer(current_user.id)
    students = results['students'] if results else []
    add_alert_counts(alert_counts, students)
    return tolerant_jsonify({
        'students': students,
        'totalStudentCount': results['totalStudentCount'] if results else 0,
    })


@app.route('/api/students/search', methods=['POST'])
@login_required
def search_students():
    params = request.get_json()
    if is_unauthorized_search(params):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    search_phrase = util.get(params, 'searchPhrase', '').strip()
    if not len(search_phrase):
        raise BadRequestError('Invalid or empty search input')
    student_results = search_for_students(
        include_profiles=True,
        search_phrase=search_phrase.replace(',', ' '),
        is_active_asc=_convert_asc_inactive_arg(util.get(params, 'isInactiveAsc')),
        order_by=util.get(params, 'orderBy', None),
        offset=util.get(params, 'offset', 0),
        limit=util.get(params, 'limit', 50),
    )
    alphanumeric_search_phrase = ''.join(e for e in search_phrase if e.isalnum()).upper()
    if alphanumeric_search_phrase:
        courses = []
        course_rows = get_enrolled_primary_sections(current_term_id(), alphanumeric_search_phrase)
        for row in islice(course_rows, 50):
            courses.append({
                'termId': row['term_id'],
                'sectionId': row['sis_section_id'],
                'courseName': row['sis_course_name'],
                'courseTitle': row['sis_course_title'],
                'instructionFormat': row['sis_instruction_format'],
                'sectionNum': row['sis_section_num'],
            })
    else:
        courses = None
    alert_counts = Alert.current_alert_counts_for_viewer(current_user.id)
    students = student_results['students']
    add_alert_counts(alert_counts, students)
    return tolerant_jsonify({
        'courses': courses,
        'students': students,
        'totalCourseCount': len(course_rows),
        'totalStudentCount': student_results['totalStudentCount'],
    })


@app.route('/api/team_groups/all')
@login_required
def get_all_team_groups():
    if not is_asc_authorized():
        raise ResourceNotFoundError('Unknown path')
    return tolerant_jsonify(athletics.all_team_groups())


def _convert_asc_inactive_arg(is_inactive_asc):
    if 'UWASC' in get_dept_codes(current_user):
        is_active_asc = not is_inactive_asc
    else:
        is_active_asc = None if is_inactive_asc is None else not is_inactive_asc
    return is_active_asc


def _get_name_range_boundaries(values):
    if isinstance(values, list) and len(values):
        values = sorted(values, key=lambda v: v.upper())
        return [values[0].upper(), values[-1].upper()]
    else:
        return None
