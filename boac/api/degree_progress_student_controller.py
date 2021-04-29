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

from boac.api.degree_progress_api_utils import clone_degree_template
from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.api.util import can_edit_degree_progress, can_read_degree_progress, get_degree_checks_json
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, is_int
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_course import DegreeProgressCourse
from boac.models.degree_progress_note import DegreeProgressNote
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/degree/check/<sid>/create', methods=['POST'])
@can_edit_degree_progress
def create_degree_check(sid):
    params = request.get_json()
    template_id = get_param(params, 'templateId')
    if not template_id or not is_int(sid):
        raise BadRequestError("Missing parameters: sid and templateId are required.'")
    return tolerant_jsonify(clone_degree_template(template_id=template_id, sid=sid).to_api_json())


@app.route('/api/degree/course/<course_id>/assign', methods=['POST'])
@can_edit_degree_progress
def assign_course(course_id):
    params = request.get_json()
    course = DegreeProgressCourse.find_by_id(course_id)
    if course:
        existing_category = DegreeProgressCategory.find_by_id(course.category_id) if course.category_id else None
        if existing_category and existing_category.position == -1:
            # Transient categories are identified by position=-1 and are deleted when the course is unassigned.
            # In this case, "On Cascade Delete" will cause deletion of the course, which is what we want. The course
            # will be regenerated in "Unassigned Courses" list or this course is a "secondary" instance.
            DegreeProgressCategory.delete(course.category_id)
        else:
            category_id = get_param(params, 'categoryId')
            DegreeProgressCourse.assign_category(category_id=category_id, course_id=course.id)
        return tolerant_jsonify({'message': f'Course ${course.display_name} has been re-assigned'})
    else:
        raise ResourceNotFoundError(f'No course found with id={course_id}.')


@app.route('/api/degrees/student/<sid>')
@can_read_degree_progress
def get_degree_checks(sid):
    return tolerant_jsonify(get_degree_checks_json(sid))


@app.route('/api/degree/course/<course_id>/update', methods=['POST'])
@can_edit_degree_progress
def update_course(course_id):
    params = request.get_json()
    note = get_param(params, 'note')
    units = get_param(params, 'units')
    if not units:
        raise BadRequestError("The required 'units' parameter is missing.'")
    return tolerant_jsonify(DegreeProgressCourse.update(course_id=course_id, note=note, units=units).to_api_json())


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
