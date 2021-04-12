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

from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.api.util import can_edit_degree_progress, can_read_degree_progress, get_list_from_http_post
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param
from boac.models.degree_progress_category import DegreeProgressCategory
from flask import current_app as app, request
from flask_cors import cross_origin


@app.route('/api/degree/category/create', methods=['POST'])
@can_edit_degree_progress
def create_category():
    params = request.get_json()
    category_type = get_param(params, 'categoryType')
    course_units = get_param(params, 'courseUnits')
    name = get_param(params, 'name')
    parent_category_id = get_param(params, 'parentCategoryId')
    position = get_param(params, 'position')
    template_id = get_param(params, 'templateId')
    unit_requirement_ids = get_list_from_http_post('unitRequirementIds')

    if not category_type or not name or not _is_valid_position(position) or not template_id:
        raise BadRequestError("Insufficient data: categoryType, name, position and templateId are required.'")
    if category_type == 'Subcategory' and not parent_category_id:
        raise BadRequestError("The parentCategoryId param is required when categoryType equals 'Subcategory'.")
    if parent_category_id:
        parent = _get_degree_category(parent_category_id)
        parent_type = parent.category_type
        if parent_type == 'Course' or (parent_type == 'Subcategory' and category_type == 'Category'):
            raise BadRequestError(f'Type {category_type} not allowed, based on parent type: {parent_type}.')
        if parent.position != position:
            raise BadRequestError(f'Category position ({position}) must match its parent ({parent.position}).')

    category = DegreeProgressCategory.create(
        category_type=category_type,
        course_units=course_units,
        description=None,
        name=name,
        parent_category_id=parent_category_id,
        position=position,
        template_id=template_id,
        unit_requirement_ids=unit_requirement_ids,
    )
    return tolerant_jsonify(category.to_api_json())


@app.route('/api/degree/category/<category_id>')
@can_read_degree_progress
def get_degree_category(category_id):
    return tolerant_jsonify(_get_degree_category(category_id))


@app.route('/api/degree/category/<category_id>', methods=['DELETE'])
@can_edit_degree_progress
@cross_origin(allow_headers=['Content-Type'])
def delete_degree_category(category_id):
    DegreeProgressCategory.delete(category_id)
    return tolerant_jsonify({'message': f'Template {category_id} deleted'}), 200


def _get_degree_category(category_id):
    category = DegreeProgressCategory.find_by_id(category_id)
    if not category:
        raise ResourceNotFoundError(f'No category found with id={category_id}.')
    return category


def _is_valid_position(position):
    return position and (0 < position < 4)
