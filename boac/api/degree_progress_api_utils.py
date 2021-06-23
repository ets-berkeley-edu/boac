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
from boac.lib.background import bg_execute
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.cache_utils import fetch, store
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_template import DegreeProgressTemplate
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement
from flask import current_app as app
from flask_login import current_user


def clone_degree_template(template_id, name=None, sid=None):
    template = DegreeProgressTemplate.find_by_id(template_id)
    if template_id and not template:
        raise ResourceNotFoundError(f'No template found with id={template_id}.')
    if name:
        validate_template_upsert(name=name, template_id=template_id)

    created_by = current_user.get_id()
    advisor_dept_codes = dept_codes_where_advising(current_user)
    return clone(template, created_by, advisor_dept_codes, name=name, sid=sid)


def create_batch_degree_checks(template_id, sids):
    created_by = current_user.get_id()
    cache_key = get_cache_key()
    existing_status = fetch(cache_key)
    if not (existing_status is None or int(existing_status) == 1):
        raise BadRequestError('Existing batch degree check job in progress.')
    advisor_dept_codes = dept_codes_where_advising(current_user)

    def _create(db_session):
        template = fetch_degree_template(template_id)
        if template_id and not template:
            raise ResourceNotFoundError(f'No template found with id={template_id}.')
        completed = 0
        store(cache_key, 0)
        for sid in sids:
            if fetch(cache_key) is None:
                app.logger.info('Batch degree check canceled.')
                break
            clone(template, created_by, advisor_dept_codes, sid=sid, db_session=db_session)
            completed += 1
            store(cache_key, completed / len(sids))

    bg_execute(_create)
    return 'started'


def clone(template, created_by, advisor_dept_codes, name=None, sid=None, db_session=None):
    clone = DegreeProgressTemplate.create(
        advisor_dept_codes=advisor_dept_codes,
        created_by=created_by,
        degree_name=name or template.degree_name,
        parent_template_id=template.id if sid else None,
        student_sid=sid,
        db_session=db_session,
    )
    unit_requirements_by_source_id = {}
    for unit_requirement in template.unit_requirements:
        source_id = unit_requirement.id
        unit_requirements_by_source_id[source_id] = DegreeProgressUnitRequirement.create(
            created_by=created_by,
            min_units=unit_requirement.min_units,
            name=unit_requirement.name,
            template_id=clone.id,
            db_session=db_session,
        )

    def _create_category(category_, parent_id):
        unit_requirement_ids = []
        for u in category_['unitRequirements']:
            source_id_ = u['id']
            cross_reference = unit_requirements_by_source_id[source_id_]
            unit_requirement_ids.append(cross_reference.id)
        return DegreeProgressCategory.create(
            category_type=category_['categoryType'],
            name=category_['name'],
            position=category_['position'],
            template_id=clone.id,
            course_units_lower=category_['unitsLower'],
            course_units_upper=category_['unitsUpper'],
            description=category_['description'],
            parent_category_id=parent_id,
            unit_requirement_ids=unit_requirement_ids,
            db_session=db_session,
        )
    for category in DegreeProgressCategory.get_categories(template_id=template.id):
        c = _create_category(category_=category, parent_id=None)
        for course in category['courseRequirements']:
            _create_category(category_=course, parent_id=c.id)
        for subcategory in category['subcategories']:
            s = _create_category(category_=subcategory, parent_id=c.id)
            for course in subcategory['courseRequirements']:
                _create_category(category_=course, parent_id=s.id)

    # TODO: Unit requirements?
    return DegreeProgressTemplate.find_by_id(clone.id)


def fetch_degree_template(template_id):
    template = DegreeProgressTemplate.find_by_id(template_id)
    if not template:
        raise ResourceNotFoundError(f'No template found with id={template_id}.')
    return template


def get_cache_key():
    user_id = current_user.get_id()
    return f'degree_progress_batch/{user_id}'


def validate_template_upsert(name, template_id=None):
    if not name:
        raise BadRequestError('\'name\' is required.')
    # Name must be unique across non-deleted templates
    template = DegreeProgressTemplate.find_by_name(name=name, case_insensitive=True)
    if template and (template_id is None or template_id != template.id):
        raise BadRequestError(f'A degree named <strong>{name}</strong> already exists. Please choose a different name.')
    return template
