"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.errors import ResourceNotFoundError
from boac.api.util import ce3_required
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param
from boac.merged.admitted_student import get_admitted_student_by_sid, query_admitted_students
from flask import current_app as app, request


@app.route('/api/admit/by_sid/<sid>')
@ce3_required
def get_admit_by_sid(sid):
    admit = get_admitted_student_by_sid(sid)
    if not admit:
        raise ResourceNotFoundError('Unknown admit')
    return tolerant_jsonify(admit)


@app.route('/api/admits/all')
@ce3_required
def get_all_admits():
    limit = get_param(request.args, 'limit', 50)
    offset = get_param(request.args, 'offset', 0)
    order_by = get_param(request.args, 'orderBy', None)
    admits = query_admitted_students(
        limit=int(limit),
        offset=int(offset),
        order_by=order_by,
    )
    return tolerant_jsonify(admits)
