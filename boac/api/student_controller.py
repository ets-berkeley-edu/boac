"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.api.util import advisor_required, put_notifications
from boac.externals.data_loch import match_students_by_name_or_sid, query_historical_sids
from boac.lib.http import tolerant_jsonify
from boac.merged.student import get_student_and_terms_by_sid, get_student_and_terms_by_uid, query_students
from flask import current_app as app, request
from flask_login import login_required


@app.route('/api/student/by_sid/<sid>')
@advisor_required
def get_student_by_sid(sid):
    student = get_student_and_terms_by_sid(sid)
    if not student:
        raise ResourceNotFoundError('Unknown student')
    put_notifications(student)
    return tolerant_jsonify(student)


@app.route('/api/student/by_uid/<uid>')
@advisor_required
def get_student_by_uid(uid):
    student = get_student_and_terms_by_uid(uid)
    if not student:
        raise ResourceNotFoundError('Unknown student')
    put_notifications(student)
    return tolerant_jsonify(student)


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
@advisor_required
def validate_sids():
    params = request.get_json()
    sids = [sid.strip() for sid in list(params.get('sids'))]
    if sids:
        if next((sid for sid in sids if not sid.isnumeric()), None):
            raise BadRequestError('Each SID must be numeric')
        else:
            summary = []
            available_sids = query_students(sids=sids, sids_only=True)['sids']
            remaining_sids = list(set(sids) - set(available_sids))
            available_sids += [row['sid'] for row in query_historical_sids(remaining_sids)]
            for sid in sids:
                summary.append({
                    'sid': sid,
                    'status': 200 if sid in available_sids else 404,
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
