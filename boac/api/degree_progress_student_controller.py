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
from boac.api.util import can_edit_degree_progress, can_read_degree_progress, get_degree_checks_json
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, is_int
from boac.models.degree_progress_category import DegreeProgressCategory
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
    template = DegreeProgressTemplate.find_by_id(template_id)
    if template_id and not template:
        raise ResourceNotFoundError(f'No template found with id={template_id}.')

    degree = DegreeProgressTemplate.create(
        advisor_dept_codes=dept_codes_where_advising(current_user),
        created_by=current_user.get_id(),
        degree_name=template.degree_name,
        student_sid=sid,
    )

    def _create_category(c):
        DegreeProgressCategory.create(
            category_type=c['categoryType'],
            name=c['name'],
            position=c['position'],
            template_id=template_id,
            course_units=c['courseUnits'],
            description=c['description'],
            parent_category_id=c['parentCategoryId'],
            unit_requirement_ids=c.get('unitRequirementIds'),
        )
    for category in DegreeProgressCategory.get_categories(template_id=template_id):
        _create_category(c=category)
        for course in category['courses']:
            _create_category(c=course)
        for subcategory in category['subcategories']:
            _create_category(c=subcategory)
            for course in subcategory['courses']:
                _create_category(c=course)

    # TODO: Unit requirements?

    return tolerant_jsonify(DegreeProgressTemplate.find_by_id(degree.id).to_api_json())


@app.route('/api/degrees/student/<sid>')
@can_read_degree_progress
def get_degree_checks(sid):
    return tolerant_jsonify(get_degree_checks_json(sid))
