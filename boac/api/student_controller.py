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


from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import add_alert_counts, get_dept_codes, is_asc_authorized, is_unauthorized_search
from boac.externals.cal1card_photo_api import get_cal1card_photo
from boac.lib import util
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
    advisor_ldap_uids = util.get(params, 'advisorLdapUids')
    coe_prep_statuses = util.get(params, 'coePrepStatuses')
    ethnicities = util.get(params, 'ethnicities')
    genders = util.get(params, 'genders')
    gpa_ranges = util.get(params, 'gpaRanges')
    group_codes = util.get(params, 'groupCodes')
    levels = util.get(params, 'levels')
    majors = util.get(params, 'majors')
    unit_ranges = util.get(params, 'unitRanges')
    in_intensive_cohort = util.to_bool_or_none(util.get(params, 'inIntensiveCohort'))
    is_inactive_asc = util.get(params, 'isInactiveAsc')
    order_by = util.get(params, 'orderBy', None)
    offset = util.get(params, 'offset', 0)
    limit = util.get(params, 'limit', 50)

    results = query_students(
        include_profiles=True,
        advisor_ldap_uids=advisor_ldap_uids,
        coe_prep_statuses=coe_prep_statuses,
        ethnicities=ethnicities,
        genders=genders,
        gpa_ranges=gpa_ranges,
        group_codes=group_codes,
        levels=levels,
        majors=majors,
        unit_ranges=unit_ranges,
        in_intensive_cohort=in_intensive_cohort,
        is_active_asc=_convert_asc_inactive_arg(is_inactive_asc),
        order_by=order_by,
        offset=offset,
        limit=limit,
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
    is_inactive_asc = util.get(params, 'isInactiveAsc')
    order_by = util.get(params, 'orderBy', None)
    offset = util.get(params, 'offset', 0)
    limit = util.get(params, 'limit', 50)
    results = search_for_students(
        include_profiles=True,
        search_phrase=search_phrase.replace(',', ' '),
        is_active_asc=_convert_asc_inactive_arg(is_inactive_asc),
        order_by=order_by,
        offset=offset,
        limit=limit,
    )
    alert_counts = Alert.current_alert_counts_for_viewer(current_user.id)
    students = results['students']
    add_alert_counts(alert_counts, students)
    return tolerant_jsonify({
        'students': students,
        'totalStudentCount': results['totalStudentCount'],
    })


@app.route('/api/team_groups/all')
@login_required
def get_all_team_groups():
    # TODO: Give unauthorized user a 404 without disrupting COE advisors on the filtered-cohort view.
    data = athletics.all_team_groups() if is_asc_authorized() else []
    return tolerant_jsonify(data)


def _convert_asc_inactive_arg(is_inactive_asc):
    if 'UWASC' in get_dept_codes(current_user):
        is_active_asc = not is_inactive_asc
    else:
        is_active_asc = None if is_inactive_asc is None else not is_inactive_asc
    return is_active_asc
