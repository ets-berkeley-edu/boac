"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.api.util import add_alert_counts, is_unauthorized_search, put_notifications
from boac.externals.cal1card_photo_api import get_cal1card_photo
from boac.externals.data_loch import extract_valid_sids, match_students_by_name_or_sid
from boac.lib import util
from boac.lib.http import tolerant_jsonify
from boac.merged.student import get_student_and_terms_by_sid, get_student_and_terms_by_uid, query_students
from boac.models.alert import Alert
from flask import current_app as app, request, Response
from flask_login import current_user, login_required


@app.route('/api/student/by_sid/<sid>')
@login_required
def get_student_by_sid(sid):
    student = get_student_and_terms_by_sid(sid)
    if not student:
        raise ResourceNotFoundError('Unknown student')
    put_notifications(student)
    return tolerant_jsonify(student)


@app.route('/api/student/by_uid/<uid>')
@login_required
def get_student_by_uid(uid):
    student = get_student_and_terms_by_uid(uid)
    if not student:
        raise ResourceNotFoundError('Unknown student')
    put_notifications(student)
    return tolerant_jsonify(student)


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
    params = util.remove_none_values(request.get_json())
    order_by = util.get(params, 'orderBy', None)
    if is_unauthorized_search(list(params.keys()), order_by):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    inactive_asc = util.get(params, 'isInactiveAsc')
    inactive_coe = util.get(params, 'isInactiveCoe')
    results = query_students(
        advisor_ldap_uids=util.get(params, 'advisorLdapUids'),
        coe_prep_statuses=util.get(params, 'coePrepStatuses'),
        coe_probation=util.get(params, 'coeProbation'),
        ethnicities=util.get(params, 'ethnicities'),
        expected_grad_terms=util.get(params, 'expectedGradTerms'),
        genders=util.get(params, 'genders'),
        gpa_ranges=util.get(params, 'gpaRanges'),
        group_codes=util.get(params, 'groupCodes'),
        include_profiles=True,
        is_active_asc=None if inactive_asc is None else not inactive_asc,
        is_active_coe=None if inactive_coe is None else not inactive_coe,
        in_intensive_cohort=util.to_bool_or_none(util.get(params, 'inIntensiveCohort')),
        last_name_range=_get_name_range_boundaries(util.get(params, 'lastNameRange')),
        levels=util.get(params, 'levels'),
        limit=util.get(params, 'limit', 50),
        majors=util.get(params, 'majors'),
        offset=util.get(params, 'offset', 0),
        order_by=order_by,
        transfer=util.to_bool_or_none(util.get(params, 'transfer')),
        underrepresented=util.get(params, 'underrepresented'),
        unit_ranges=util.get(params, 'unitRanges'),
    )
    if results is None:
        raise BadRequestError('Invalid search criteria')
    alert_counts = Alert.current_alert_counts_for_viewer(current_user.get_id())
    students = results['students'] if results else []
    add_alert_counts(alert_counts, students)
    return tolerant_jsonify({
        'students': students,
        'totalStudentCount': results['totalStudentCount'] if results else 0,
    })


@app.route('/api/students/find_by_name_or_sid', methods=['GET'])
@login_required
def find_by_name_or_sid():
    query = request.args.get('q')
    if not query:
        raise BadRequestError('Search query must be supplied')
    limit = request.args.get('limit')
    query_fragments = filter(None, query.upper().split(' '))
    students = match_students_by_name_or_sid(query_fragments, limit=limit)

    def _student_feed(s):
        return {
            'label': f"{s.get('first_name')} {s.get('last_name')} ({s.get('sid')})",
            'sid': s.get('sid'),
            'uid': s.get('uid'),
        }
    return tolerant_jsonify([_student_feed(s) for s in students])


@app.route('/api/students/validate_sids', methods=['POST'])
@login_required
def validate_sids():
    params = request.get_json()
    sids = [sid.strip() for sid in list(params.get('sids'))]
    if sids:
        if next((sid for sid in sids if not sid.isnumeric()), None):
            raise BadRequestError(f'Each SID must be numeric')
        else:
            summary = []
            available_sids = query_students(sids=sids, sids_only=True)['sids']
            unavailable_sids = list(filter(lambda sid: sid not in available_sids, sids))
            # TODO: Remove the following when all advisors have access to all students
            valid_yet_unavailable_sids = [row['sid'] for row in extract_valid_sids(unavailable_sids)]
            for sid in sids:
                summary.append({
                    'sid': sid,
                    'status': 200 if sid in available_sids else (401 if sid in valid_yet_unavailable_sids else 404),
                })
            return tolerant_jsonify(summary)
    else:
        raise BadRequestError('Requires \'sids\' param')


def _get_name_range_boundaries(values):
    if isinstance(values, list) and len(values):
        values = sorted(values, key=lambda v: v.upper())
        return [values[0].upper(), values[-1].upper()]
    else:
        return None
