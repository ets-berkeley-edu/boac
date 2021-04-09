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

from boac.api.errors import ResourceNotFoundError
from boac.api.util import can_edit_degree_progress, can_read_degree_progress
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param
from boac.models.degree_progress_category import DegreeProgressCategory
from flask import current_app as app, request


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
    category = DegreeProgressCategory.create(
        category_type=category_type,
        course_units=course_units,
        description=None,
        name=name,
        parent_category_id=parent_category_id,
        position=position,
        template_id=template_id,
    )
    return tolerant_jsonify(category.to_api_json())


@app.route('/api/degree/category/<category_id>')
@can_read_degree_progress
def get_degree_category(category_id):
    return tolerant_jsonify(_get_degree_category(category_id))


def _get_degree_category(category_id):
    category = DegreeProgressCategory.find_by_id(category_id)
    if not category:
        raise ResourceNotFoundError(f'No category found with id={category_id}.')
    return category
