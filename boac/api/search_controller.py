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


from boac.api.errors import BadRequestError, ForbiddenRequestError
from boac.api.util import add_alert_counts, is_current_user_asc_affiliated
from boac.lib import util
from boac.lib.berkeley import get_dept_codes
from boac.lib.http import tolerant_jsonify
from boac.merged.student import query_students, search_for_students
from boac.models.alert import Alert
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/students', methods=['POST'])
@login_required
def get_students():
    params = request.get_json()
    advisor_ldap_uid = util.get(params, 'advisorLdapUid')
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
    can_view_asc_data = current_user.is_admin or is_current_user_asc_affiliated()
    is_asc_data_request = in_intensive_cohort is not None or is_inactive_asc is not None
    if is_asc_data_request and not can_view_asc_data:
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    results = query_students(
        include_profiles=True,
        advisor_ldap_uid=advisor_ldap_uid,
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
    alert_counts = Alert.current_alert_counts_for_viewer(current_user.id)
    students = results['students']
    add_alert_counts(alert_counts, students)
    return tolerant_jsonify({
        'students': students,
        'totalStudentCount': results['totalStudentCount'],
    })


@app.route('/api/students/search', methods=['POST'])
@login_required
def search_students():
    params = request.get_json()
    search_phrase = util.get(params, 'searchPhrase', '').strip()
    if not len(search_phrase):
        raise BadRequestError('Invalid or empty search input')
    is_inactive_asc = util.get(params, 'isInactiveAsc')
    order_by = util.get(params, 'orderBy', None)
    offset = util.get(params, 'offset', 0)
    limit = util.get(params, 'limit', 50)
    asc_authorized = current_user.is_admin or 'UWASC' in get_dept_codes(current_user)
    if not asc_authorized and is_inactive_asc is not None:
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
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


def _convert_asc_inactive_arg(is_inactive_asc):
    if is_current_user_asc_affiliated():
        is_active_asc = not is_inactive_asc
    else:
        is_active_asc = None if is_inactive_asc is None else not is_inactive_asc
    return is_active_asc
