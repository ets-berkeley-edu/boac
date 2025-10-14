"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from dateutil.tz import tzutc
from flask import current_app as app
from flask import request
from flask_login import current_user

from boac.api.auth_utils import is_admin_or_director
from boac.api.decorators import can_edit_degree_progress, can_read_degree_progress
from boac.api.degree_progress_api_utils import clone_degree_template, fetch_degree_template, validate_template_not_archived, validate_template_upsert
from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param
from boac.models.degree_progress_template import DegreeProgressTemplate
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement


@app.route('/api/degree/<template_id>/unit_requirement', methods=['POST'])
@can_edit_degree_progress
def add_unit_requirement(template_id):
    params = request.get_json()
    name = params.get('name')
    min_units = params.get('minUnits')
    if not name or not min_units:
        raise BadRequestError('Unit requirement \'name\' and \'minUnits\' must be provided.')
    validate_template_not_archived(template_id)
    fetch_degree_template(template_id)
    unit_requirement = DegreeProgressUnitRequirement.create(
        created_by=current_user.get_id(),
        min_units=min_units,
        name=name,
        template_id=template_id,
    )
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(template_id, current_user.get_id())
    return tolerant_jsonify(unit_requirement.to_api_json())


@app.route('/api/degree/<template_id>/clone', methods=['POST'])
@can_edit_degree_progress
def clone_template(template_id):
    name = request.get_json().get('name')
    validate_template_not_archived(template_id)
    clone = clone_degree_template(template_id=template_id, name=name)
    return tolerant_jsonify(clone.to_api_json())


@app.route('/api/degree/create', methods=['POST'])
@can_edit_degree_progress
def create_degree():
    params = request.get_json()
    name = get_param(params, 'name', None)
    validate_template_upsert(name=name)
    degree = DegreeProgressTemplate.create(
        advisor_dept_codes=dept_codes_where_advising(current_user.departments),
        created_by=current_user.get_id(),
        degree_name=name,
    )
    return tolerant_jsonify(degree.to_api_json())


@app.route('/api/degree/archive', methods=['POST'])
@can_edit_degree_progress
def archive_template():
    params = request.get_json()
    template_id = params.get('templateId')
    degree_template = fetch_degree_template(template_id) if template_id else None
    if not degree_template:
        raise ResourceNotFoundError('Degree Template not found')
    if degree_template.student_sid and not is_admin_or_director(current_user):
        raise BadRequestError('Degree Template with an associated student cannot be archived.')
    archived_template = DegreeProgressTemplate.archive(template_id)
    return tolerant_jsonify(archived_template.to_api_json())


@app.route('/api/degree/unarchive', methods=['POST'])
@can_edit_degree_progress
def unarchive_template():
    params = request.get_json()
    template_id = params.get('templateId')
    degree_template = fetch_degree_template(template_id) if template_id else None
    if not degree_template:
        raise ResourceNotFoundError('Degree Template not found')
    if not degree_template.archived_at:
        raise BadRequestError('Degree Template is not archived.')
    if degree_template.student_sid and not is_admin_or_director(current_user):
        raise BadRequestError('Degree Template with an associated student cannot be unarchived.')
    restored_template = DegreeProgressTemplate.unarchive(template_id)
    return tolerant_jsonify(restored_template.to_api_json())


@app.route('/api/degree/<template_id>', methods=['DELETE'])
@can_edit_degree_progress
def delete_template(template_id):
    validate_template_not_archived(template_id)
    DegreeProgressTemplate.delete(template_id)
    return tolerant_jsonify({'message': f'Template {template_id} deleted'}), 200


@app.route('/api/degree/unit_requirement/<unit_requirement_id>', methods=['DELETE'])
@can_edit_degree_progress
def delete_unit_requirement(unit_requirement_id):
    unit_requirement = DegreeProgressUnitRequirement.find_by_id(unit_requirement_id)
    if unit_requirement:
        validate_template_not_archived(unit_requirement.template_id)
        DegreeProgressUnitRequirement.delete(unit_requirement_id)
        # Update updated_at date of top-level record
        DegreeProgressTemplate.refresh_updated_at(unit_requirement.template_id, current_user.get_id())

        return tolerant_jsonify({'message': f'Unit requirement {unit_requirement_id} deleted'}), 200
    else:
        raise ResourceNotFoundError(f'No unit_requirement found with id={unit_requirement_id}.')


@app.route('/api/degree/<template_id>')
@can_read_degree_progress
def get_degree_template(template_id):
    template = fetch_degree_template(template_id).to_api_json(include_courses=True)
    parent_template_id = template['parentTemplateId']
    if parent_template_id:
        parent_template = DegreeProgressTemplate.find_by_id(parent_template_id)
        template['parentTemplateUpdatedAt'] = _isoformat(parent_template.updated_at)
    return tolerant_jsonify(template)


@app.route('/api/degree/templates')
@can_read_degree_progress
def get_degree_templates():
    return tolerant_jsonify(DegreeProgressTemplate.get_all_templates())


@app.route('/api/degree/<template_id>/update', methods=['POST'])
@can_edit_degree_progress
def update_degree_template(template_id):
    name = request.get_json().get('name')
    template_id = int(template_id)
    validate_template_not_archived(template_id)
    validate_template_upsert(name=name, template_id=template_id)
    template = DegreeProgressTemplate.update(name=name, template_id=template_id)
    return tolerant_jsonify(template.to_api_json())


@app.route('/api/degree/unit_requirement/<unit_requirement_id>/update', methods=['POST'])
@can_edit_degree_progress
def update_unit_requirement(unit_requirement_id):
    params = request.get_json()
    name = params.get('name')
    min_units = params.get('minUnits')
    if not name or not min_units:
        raise BadRequestError('Unit requirement \'name\' and \'minUnits\' must be provided.')
    unit_requirement = DegreeProgressUnitRequirement.find_by_id(unit_requirement_id)
    if unit_requirement:
        validate_template_not_archived(unit_requirement.template_id)
    unit_requirement = DegreeProgressUnitRequirement.update(
        id_=unit_requirement_id,
        min_units=min_units,
        name=name,
        updated_by=current_user.get_id(),
    )
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(unit_requirement.template_id, current_user.get_id())
    return tolerant_jsonify(unit_requirement.to_api_json())


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
