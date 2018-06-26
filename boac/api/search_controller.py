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
from boac.api.util import add_alert_counts
from boac.lib import util
from boac.lib.berkeley import is_department_member
from boac.lib.http import tolerant_jsonify
from boac.merged import student_details
from boac.models.alert import Alert
from boac.models.student import Student
from flask import current_app as app, request
from flask_login import current_user, login_required


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
    is_inactive_asc = util.get(params, 'isInactiveAsc')
    order_by = util.get(params, 'orderBy', None)
    offset = util.get(params, 'offset', 0)
    limit = util.get(params, 'limit', 50)
    asc_authorized = current_user.is_admin or is_department_member(current_user, 'UWASC')
    if not asc_authorized and (in_intensive_cohort is not None or is_inactive_asc is not None):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
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
    alert_counts = Alert.current_alert_counts_for_viewer(current_user.id)
    students = results['students']
    add_alert_counts(alert_counts, students)
    student_details.merge_external_students_data(students)
    return tolerant_jsonify({
        'students': students,
        'totalStudentCount': results['totalStudentCount'],
    })


@app.route('/api/students/search', methods=['POST'])
@login_required
def search_for_students():
    params = request.get_json()
    search_phrase = util.get(params, 'searchPhrase', '').strip()
    if not len(search_phrase):
        raise BadRequestError('Invalid or empty search input')
    is_inactive_asc = util.get(params, 'isInactiveAsc')
    order_by = util.get(params, 'orderBy', None)
    offset = util.get(params, 'offset', 0)
    limit = util.get(params, 'limit', 50)
    asc_authorized = current_user.is_admin or is_department_member(current_user, 'UWASC')
    if not asc_authorized and is_inactive_asc is not None:
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    results = Student.search_for_students(
        search_phrase=search_phrase.replace(',', ' '),
        is_active_asc=None if is_inactive_asc is None else not is_inactive_asc,
        order_by=order_by,
        offset=offset,
        limit=limit,
    )
    alert_counts = Alert.current_alert_counts_for_viewer(current_user.id)
    students = results['students']
    add_alert_counts(alert_counts, students)
    student_details.merge_external_students_data(students)
    return tolerant_jsonify({
        'students': students,
        'totalStudentCount': results['totalStudentCount'],
    })
