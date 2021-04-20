"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.degree_progress_api_utils import clone_degree_template, lazy_load_unassigned_courses
from boac.api.errors import BadRequestError
from boac.api.util import can_edit_degree_progress, can_read_degree_progress, get_degree_checks_json
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, is_int
from boac.models.degree_progress_template import DegreeProgressTemplate
from flask import current_app as app, request


@app.route('/api/degree/check/<sid>/create', methods=['POST'])
@can_edit_degree_progress
def create_degree_check(sid):
    params = request.get_json()
    template_id = get_param(params, 'templateId')
    if not template_id or not is_int(sid):
        raise BadRequestError("Missing parameters: sid and templateId are required.'")

    degree_check = clone_degree_template(template_id=template_id, sid=sid)
    return tolerant_jsonify(degree_check.to_api_json())


@app.route('/api/degrees/student/<sid>')
@can_read_degree_progress
def get_degree_checks(sid):
    return tolerant_jsonify(get_degree_checks_json(sid))


@app.route('/api/degree/<degree_check_id>/courses/unassigned')
@can_read_degree_progress
def get_unassigned_courses(degree_check_id):
    degree_check = DegreeProgressTemplate.find_by_id(degree_check_id)
    return tolerant_jsonify(lazy_load_unassigned_courses(degree_check))
