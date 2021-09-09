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
from boac.api.util import can_edit_degree_progress, can_read_degree_progress, normalize_accent_color
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_template import DegreeProgressTemplate
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/degree/category/create', methods=['POST'])
@can_edit_degree_progress
def create_category():
    params = request.get_json()
    category_type = get_param(params, 'categoryType')
    course_units_lower = get_param(params, 'unitsLower')
    course_units_upper = get_param(params, 'unitsUpper')
    description = get_param(params, 'description')
    name = get_param(params, 'name')
    parent_category_id = get_param(params, 'parentCategoryId')
    position = get_param(params, 'position')
    template_id = get_param(params, 'templateId')
    # Categories are mapped to degree_progress_unit_requirements
    value = get_param(request.get_json(), 'unitRequirementIds')
    unit_requirement_ids = list(filter(None, value.split(','))) if isinstance(value, str) else value

    if not category_type or not name or not _is_valid_position(position) or not template_id:
        raise BadRequestError("Insufficient data: categoryType, name, position and templateId are required.'")
    if category_type == 'Category' and parent_category_id:
        raise BadRequestError('Categories cannot have parents.')
    if category_type in ('Course Requirement', 'Subcategory') and not parent_category_id:
        raise BadRequestError("The parentCategoryId param is required when categoryType equals 'Subcategory'.")
    if parent_category_id:
        parent = _get_degree_category(parent_category_id)
        parent_type = parent.category_type
        if parent_type == 'Course Requirement' or (parent_type == 'Subcategory' and category_type == 'Category'):
            raise BadRequestError(f'Type {category_type} not allowed, based on parent type: {parent_type}.')
        if position != parent.position:
            raise BadRequestError(f'Category position ({position}) must match its parent ({parent.position}).')

    category = DegreeProgressCategory.create(
        category_type=category_type,
        course_units_lower=course_units_lower,
        course_units_upper=course_units_upper,
        description=description,
        name=name,
        parent_category_id=parent_category_id,
        position=position,
        template_id=template_id,
        unit_requirement_ids=unit_requirement_ids,
    )
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(template_id, current_user.get_id())
    return tolerant_jsonify(category.to_api_json())


@app.route('/api/degree/category/<category_id>')
@can_read_degree_progress
def get_degree_category(category_id):
    return tolerant_jsonify(_get_degree_category(category_id))


@app.route('/api/degree/category/<category_id>', methods=['DELETE'])
@can_edit_degree_progress
def delete_degree_category(category_id):
    category = _get_degree_category(category_id)
    DegreeProgressCategory.delete(category.id)
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(category.template_id, current_user.get_id())
    return tolerant_jsonify({'message': f'Template {category_id} deleted'}), 200


@app.route('/api/degree/category/<category_id>/recommend', methods=['POST'])
@can_edit_degree_progress
def recommend_category(category_id):
    params = request.get_json()
    is_recommended = get_param(params, 'isRecommended')
    if is_recommended is None:
        raise BadRequestError('Parameter \'isRecommended\' is required')

    accent_color = normalize_accent_color(get_param(params, 'accentColor'))
    grade = get_param(params, 'grade')
    note = get_param(params, 'note')
    units_lower = get_param(params, 'unitsLower')
    units_upper = get_param(params, 'unitsUpper')

    category = DegreeProgressCategory.recommend(
        accent_color=accent_color,
        category_id=category_id,
        course_units_lower=units_lower,
        course_units_upper=units_upper,
        grade=grade,
        is_recommended=is_recommended,
        note=(note or '').strip() or None,
    )
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(category.template_id, current_user.get_id())
    return tolerant_jsonify(category.to_api_json())


@app.route('/api/degree/category/<category_id>/update', methods=['POST'])
@can_edit_degree_progress
def update_category(category_id):
    params = request.get_json()
    units_lower = get_param(params, 'unitsLower')
    units_upper = get_param(params, 'unitsUpper')
    description = get_param(params, 'description')
    name = get_param(params, 'name')
    parent_category_id = get_param(params, 'parentCategoryId')
    # Courses can be mapped to degree_progress_unit_requirements
    value = get_param(request.get_json(), 'unitRequirementIds')
    unit_requirement_ids = list(filter(None, value.split(','))) if isinstance(value, str) else value

    category = DegreeProgressCategory.update(
        category_id=category_id,
        course_units_lower=units_lower,
        course_units_upper=units_upper,
        description=description,
        parent_category_id=parent_category_id,
        name=name,
        unit_requirement_ids=unit_requirement_ids,
    )
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(category.template_id, current_user.get_id())
    return tolerant_jsonify(category.to_api_json())


def _get_degree_category(category_id):
    category = DegreeProgressCategory.find_by_id(category_id)
    if not category:
        raise ResourceNotFoundError(f'No category found with id={category_id}.')
    return category


def _is_valid_position(position):
    return position and (0 < position < 4)
