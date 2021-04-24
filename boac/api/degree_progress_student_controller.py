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
from boac.models.degree_progress_course import DegreeProgressCourse
from boac.models.degree_progress_note import DegreeProgressNote
from boac.models.degree_progress_template import DegreeProgressTemplate
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/degree/check/<sid>/create', methods=['POST'])
@can_edit_degree_progress
def create_degree_check(sid):
    params = request.get_json()
    template_id = get_param(params, 'templateId')
    if not template_id or not is_int(sid):
        raise BadRequestError("Missing parameters: sid and templateId are required.'")

    degree_check = clone_degree_template(template_id=template_id, sid=sid)
    return tolerant_jsonify(degree_check.to_api_json())


@app.route('/api/degree/course/assign', methods=['POST'])
@can_edit_degree_progress
def assign_course():
    params = request.get_json()
    category_id = get_param(params, 'categoryId')
    section_id = get_param(params, 'sectionId')
    sid = get_param(params, 'sid')
    term_id = get_param(params, 'termId')
    if not section_id or not sid or not term_id:
        raise BadRequestError('Required parameters not found.')

    course = DegreeProgressCourse.assign_category(
        category_id=category_id,
        section_id=section_id,
        sid=sid,
        term_id=term_id,
    )
    return tolerant_jsonify(course.to_api_json())


@app.route('/api/degrees/student/<sid>')
@can_read_degree_progress
def get_degree_checks(sid):
    return tolerant_jsonify(get_degree_checks_json(sid))


@app.route('/api/degree/<degree_check_id>/courses/unassigned')
@can_read_degree_progress
def get_unassigned_courses(degree_check_id):
    degree_check = DegreeProgressTemplate.find_by_id(degree_check_id)
    courses = lazy_load_unassigned_courses(degree_check)
    return tolerant_jsonify([c.to_api_json() for c in courses])


@app.route('/api/degree/course/update', methods=['POST'])
@can_edit_degree_progress
def update_course():
    params = request.get_json()
    note = get_param(params, 'note')
    section_id = get_param(params, 'sectionId')
    sid = get_param(params, 'sid')
    term_id = get_param(params, 'termId')
    units = get_param(params, 'units')
    if not section_id or not sid or not term_id or not units:
        raise BadRequestError("One or more required parameters not found.'")

    degree_check = DegreeProgressCourse.update(
        note=note,
        section_id=section_id,
        sid=sid,
        term_id=term_id,
        units=units,
    )
    return tolerant_jsonify(degree_check.to_api_json())


@app.route('/api/degree/<degree_check_id>/note', methods=['POST'])
@can_edit_degree_progress
def update_degree_note(degree_check_id):
    params = request.get_json()
    body = get_param(params, 'body')
    note = DegreeProgressNote.upsert(
        body=body,
        template_id=degree_check_id,
        updated_by=current_user.get_id(),
    )
    return tolerant_jsonify(note.to_api_json())
