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

from datetime import datetime

from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.util import get_benchmarker
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_course import DegreeProgressCourse
from boac.models.degree_progress_template import DegreeProgressTemplate
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement
from flask_login import current_user


def clone_degree_template(template_id, name=None, sid=None):
    template = DegreeProgressTemplate.find_by_id(template_id)
    if template_id and not template:
        raise ResourceNotFoundError(f'No template found with id={template_id}.')
    if name:
        validate_template_upsert(name=name, template_id=template_id)

    created_by = current_user.get_id()
    return clone(template, created_by, name=name, sid=sid)


def create_batch_degree_checks(template_id, sids):
    benchmark = get_benchmarker(f'create_batch_degree_checks template_id={template_id}')
    benchmark('begin')
    template = fetch_degree_template(template_id)
    created_by = current_user.get_id()
    results_by_sid = {}
    benchmark(f'creating {len(sids)} clones')
    for sid in sids:
        degree_check = clone(template, created_by, sid=sid)
        results_by_sid[sid] = degree_check.id
    benchmark('end')
    return results_by_sid


def clone(template, created_by, name=None, sid=None):
    template_clone = DegreeProgressTemplate.create(
        advisor_dept_codes=dept_codes_where_advising(current_user),
        created_by=created_by,
        degree_name=name or template.degree_name,
        parent_template_id=template.id if sid else None,
        student_sid=sid,
    )
    unit_requirements_by_source_id = {}
    template_clone_id = template_clone.id
    for unit_requirement in template.unit_requirements:
        source_id = unit_requirement.id
        unit_requirements_by_source_id[source_id] = DegreeProgressUnitRequirement.create(
            created_by=created_by,
            min_units=unit_requirement.min_units,
            name=unit_requirement.name,
            template_id=template_clone_id,
        )

    def _create_category(category_, parent_id):
        unit_requirement_ids = []
        for u in category_['unitRequirements']:
            source_id_ = u['id']
            cross_reference = unit_requirements_by_source_id[source_id_]
            unit_requirement_ids.append(cross_reference.id)
        category_name = category_['name']
        units_lower = category_['unitsLower']
        units_upper = category_['unitsUpper']
        is_satisfied_by_transfer_course = category_['isSatisfiedByTransferCourse']
        now = datetime.now()

        category_created = DegreeProgressCategory.create(
            category_type=category_['categoryType'],
            course_units_lower=units_lower,
            course_units_upper=units_upper,
            description=category_['description'],
            is_satisfied_by_transfer_course=False if sid else is_satisfied_by_transfer_course,
            name=category_name,
            parent_category_id=parent_id,
            position=category_['position'],
            template_id=template_clone_id,
            unit_requirement_ids=unit_requirement_ids,
        )
        if sid and is_satisfied_by_transfer_course:
            transfer_course = DegreeProgressCourse.create(
                accent_color='Purple',
                category_id=category_created.id,
                degree_check_id=template_clone_id,
                display_name=category_name,
                grade='T',
                manually_created_at=now,
                manually_created_by=current_user.user_id,
                section_id=None,
                sid=sid,
                term_id=None,
                units=units_lower or units_upper,
                unit_requirement_ids=unit_requirement_ids,
            )
            DegreeProgressCourse.assign(
                category_id=category_created.id,
                course_id=transfer_course.id,
            )
        return category_created

    categories = DegreeProgressCategory.get_categories(template_id=template.id)
    for category in categories:
        c = _create_category(category_=category, parent_id=None)
        for course in category['courseRequirements']:
            _create_category(category_=course, parent_id=c.id)
        for subcategory in category['subcategories']:
            s = _create_category(category_=subcategory, parent_id=c.id)
            for course in subcategory['courseRequirements']:
                _create_category(category_=course, parent_id=s.id)
    return DegreeProgressTemplate.find_by_id(template_clone_id)


def fetch_degree_template(template_id):
    template = DegreeProgressTemplate.find_by_id(template_id)
    if not template:
        raise ResourceNotFoundError(f'No template found with id={template_id}.')
    return template


def validate_template_upsert(name, template_id=None):
    if not name:
        raise BadRequestError('\'name\' is required.')
    # Name must be unique across non-deleted templates
    template = DegreeProgressTemplate.find_by_name(name=name, case_insensitive=True)
    if template and (template_id is None or template_id != template.id):
        raise BadRequestError(f'A degree named <strong>{name}</strong> already exists. Please choose a different name.')
    return template
