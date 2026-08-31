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

from datetime import datetime

from flask_login import current_user

from boac import db, std_commit
from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.util import get_benchmarker
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_category_unit_requirement import (
    DegreeProgressCategoryUnitRequirement,
)
from boac.models.degree_progress_course import DegreeProgressCourse
from boac.models.degree_progress_course_unit_requirement import (
    DegreeProgressCourseUnitRequirement,
)
from boac.models.degree_progress_template import DegreeProgressTemplate
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement


def clone_degree_template(template_id, name=None, sid=None):
    template = DegreeProgressTemplate.find_by_id(template_id)
    if template_id and not template:
        raise ResourceNotFoundError(f"No template found with id={template_id}.")
    if name:
        validate_template_upsert(name=name, template_id=template_id)

    created_by = current_user.get_id()
    cloned_template = clone(template, created_by, name=name, sid=sid)
    std_commit()
    return cloned_template


def create_batch_degree_checks(template_id, sids):
    benchmark = get_benchmarker(f"create_batch_degree_checks template_id={template_id}")
    benchmark("begin")

    template = fetch_degree_template(template_id)
    created_by = current_user.get_id()

    benchmark(f"creating {len(sids)} clones")

    categories = _get_categories(template)
    links = _get_category_to_ur_links(template)
    transfer_categories = _get_transfer_categories(categories)
    links_by_cat = {}
    for link in links:
        links_by_cat.setdefault(link.category_id, []).append(link)

    results_by_sid = {}

    chunk_size = 100
    try:
        for i in range(0, len(sids), chunk_size):
            chunk = sids[i : i + chunk_size]
            benchmark(f"processing chunk {i // chunk_size + 1} ({len(chunk)} students)")
            chunk_results = _bulk_clone_all(
                template,
                chunk,
                created_by,
                categories,
                links,
                transfer_categories,
                links_by_cat,
                benchmark,
            )
            results_by_sid.update(chunk_results)
            std_commit()
    except Exception:
        db.session.rollback()
        raise

    benchmark("end")
    return results_by_sid


def _fix_category_parents_bulk(categories, category_map):
    """
    Update parent-child relationships for a batch of categories after they have been cloned.

    Build a list of update mappings that translate each category's original parent_category_id to the new cloned ID using category_map.
    Perform a bulk database update to set the correct parent IDs on the cloned categories.
    """
    updates = [
        {
            "id": category_map[c.id],
            "parent_category_id": category_map[c.parent_category_id],
        }
        for c in categories
        if c.parent_category_id
    ]
    if updates:
        db.session.bulk_update_mappings(DegreeProgressCategory, updates)
        db.session.flush()


def _clone_transfer_courses(
    transfer_categories,
    category_map,
    unit_map,
    template_clone,
    sid,
    now,
    category_unit_links,
):
    """Clones transfer-related courses and wires them up to the correct requirements in the new degree check."""
    new_courses = [
        (
            c.id,
            DegreeProgressCourse(
                accent_color="Purple",
                category_id=category_map[c.id],
                degree_check_id=template_clone.id,
                display_name=c.name,
                grade="T",
                manually_created_at=now,
                manually_created_by=current_user.user_id,
                section_id=None,
                sid=sid,
                term_id=None,
                units=(
                    c.course_units.lower
                    if c.course_units and c.course_units.lower is not None
                    else (c.course_units.upper if c.course_units else None)
                ),
            ),
        )
        for c in transfer_categories
    ]

    for _, course in new_courses:
        db.session.add(course)
    db.session.flush()

    course_map = {c_id: course.id for c_id, course in new_courses}

    course_links = [
        {
            "course_id": course_map[c.id],
            "unit_requirement_id": unit_map[link.unit_requirement_id],
        }
        for c in transfer_categories
        for link in category_unit_links.get(c.id, [])
    ]

    if course_links:
        db.session.bulk_insert_mappings(
            DegreeProgressCourseUnitRequirement, course_links,
        )


def clone(
    template,
    created_by,
    name=None,
    sid=None,
    categories=None,
    links=None,
    transfer_categories=None,
):
    """Cloning of a degree progress template and all related entities. Each table is only flushed once for every sid."""
    now = datetime.now()

    categories = categories or _get_categories(template)
    links = links or _get_category_to_ur_links(template)
    transfer_categories = transfer_categories or _get_transfer_categories(categories)

    template_clone = _clone_template(template, created_by, name, sid)
    unit_map = _clone_unit_requirements(template, template_clone, created_by)

    category_map = _clone_categories(categories, template_clone, sid)
    _fix_category_parents_bulk(categories, category_map)
    _apply_category_unit_links(links, category_map, unit_map)

    if sid:
        links_by_cat = {}
        for link in links:
            links_by_cat.setdefault(link.category_id, []).append(link)
        _clone_transfer_courses(
            transfer_categories,
            category_map,
            unit_map,
            template_clone,
            sid,
            now,
            links_by_cat,
        )

    return template_clone


def _bulk_clone_all(
    template, sids, created_by, categories, links, transfer_categories, links_by_cat, benchmark,
):
    """Accumulates all rows in memory first, then bulk-inserts per table."""
    now = datetime.now()
    dept_codes = dept_codes_where_advising(current_user.departments)

    # templates
    template_mappings = [
        {
            "advisor_dept_codes": dept_codes,
            "created_by": created_by,
            "degree_name": template.degree_name,
            "parent_template_id": template.id,
            "student_sid": sid,
            "updated_by": created_by,
        }
        for sid in sids
    ]
    db.session.bulk_insert_mappings(
        DegreeProgressTemplate, template_mappings, return_defaults=True,
    )
    db.session.flush()

    sid_to_template_id = {m["student_sid"]: m["id"] for m in template_mappings}

    # unit requirements
    ur_rows, ur_index = [], []
    for sid in sids:
        for ur in template.unit_requirements:
            ur_rows.append(
                DegreeProgressUnitRequirement(
                    created_by=created_by,
                    min_units=ur.min_units,
                    name=ur.name,
                    template_id=sid_to_template_id[sid],
                    updated_by=created_by,
                ),
            )
            ur_index.append((sid, ur.id))
    db.session.bulk_save_objects(ur_rows, return_defaults=True)
    db.session.flush()
    sid_old_ur_to_new = {key: obj.id for key, obj in zip(ur_index, ur_rows)}

    # categories
    cat_rows, cat_index = [], []
    for sid in sids:
        for c in categories:
            cat_rows.append(
                DegreeProgressCategory(
                    accent_color=c.accent_color,
                    category_type=c.category_type,
                    course_units=c.course_units,
                    description=c.description,
                    grade=c.grade,
                    is_satisfied_by_transfer_course=False,
                    name=c.name,
                    parent_category_id=None,
                    template_id=sid_to_template_id[sid],
                    ux_position_x=c.ux_position_x,
                    ux_position_y=c.ux_position_y,
                ),
            )
            cat_index.append((sid, c.id))
    db.session.bulk_save_objects(cat_rows, return_defaults=True)
    db.session.flush()
    benchmark(f"cloned {len(cat_rows)} categories")
    sid_old_cat_to_new = {key: obj.id for key, obj in zip(cat_index, cat_rows)}

    # fix parent relationships + category↔unit links
    parent_updates = [
        {
            "id": sid_old_cat_to_new[(sid, c.id)],
            "parent_category_id": sid_old_cat_to_new[(sid, c.parent_category_id)],
        }
        for sid in sids
        for c in categories
        if c.parent_category_id
    ]
    if parent_updates:
        db.session.bulk_update_mappings(DegreeProgressCategory, parent_updates)

    db.session.bulk_insert_mappings(
        DegreeProgressCategoryUnitRequirement,
        [
            {
                "category_id": sid_old_cat_to_new[(sid, link.category_id)],
                "unit_requirement_id": sid_old_ur_to_new[
                    (sid, link.unit_requirement_id)
                ],
            }
            for sid in sids
            for link in links
        ],
    )

    # transfer courses
    course_rows, course_index = [], []
    for sid in sids:
        for c in transfer_categories:
            units = None
            if c.course_units:
                units = (
                    c.course_units.lower
                    if c.course_units.lower is not None
                    else c.course_units.upper
                )
            course_rows.append(
                DegreeProgressCourse(
                    accent_color="Purple",
                    category_id=sid_old_cat_to_new[(sid, c.id)],
                    degree_check_id=sid_to_template_id[sid],
                    display_name=c.name,
                    grade="T",
                    manually_created_at=now,
                    manually_created_by=current_user.user_id,
                    section_id=None,
                    sid=sid,
                    term_id=None,
                    units=units,
                ),
            )
            course_index.append((sid, c.id))

    if course_rows:
        db.session.bulk_save_objects(course_rows, return_defaults=True)
        db.session.flush()
        sid_old_cat_to_course = {
            key: obj.id for key, obj in zip(course_index, course_rows)
        }

        # course↔unit links
        db.session.bulk_insert_mappings(
            DegreeProgressCourseUnitRequirement,
            [
                {
                    "course_id": sid_old_cat_to_course[(sid, c.id)],
                    "unit_requirement_id": sid_old_ur_to_new[
                        (sid, link.unit_requirement_id)
                    ],
                }
                for sid in sids
                for c in transfer_categories
                for link in links_by_cat.get(c.id, [])
            ],
        )

    return sid_to_template_id


def _get_categories(template):
    """Fetch all categories associated with a template."""
    return DegreeProgressCategory.query.filter_by(
        template_id=template.id,
    ).order_by(
        DegreeProgressCategory.created_at,
        DegreeProgressCategory.id,
    ).all()


def _get_category_to_ur_links(template):
    """Fetch all category-to-unit-requirement links for a template."""
    return (
        db.session.query(
            DegreeProgressCategoryUnitRequirement,
        )
        .join(DegreeProgressCategory)
        .filter(
            DegreeProgressCategory.template_id == template.id,
        )
        .all()
    )


def _get_transfer_categories(categories):
    """Filter categories that can be satisfied by transfer courses."""
    return [c for c in categories if c.is_satisfied_by_transfer_course]


def _clone_template(template, created_by, name, sid):
    """Clone the main template record."""
    template_clone = DegreeProgressTemplate(
        advisor_dept_codes=dept_codes_where_advising(current_user.departments),
        created_by=created_by,
        degree_name=name or template.degree_name,
        parent_template_id=template.id if sid else None,
        student_sid=sid,
        updated_by=created_by,
    )
    db.session.add(template_clone)
    db.session.flush()
    return template_clone


def _clone_unit_requirements(template, template_clone, created_by):
    """Clone unit requirements and build a mapping of old IDs to new IDs."""
    unit_map = {}

    new_units = []
    for ur in template.unit_requirements:
        new_ur = DegreeProgressUnitRequirement(
            created_by=created_by,
            min_units=ur.min_units,
            name=ur.name,
            template_id=template_clone.id,
            updated_by=created_by,
        )
        db.session.add(new_ur)
        new_units.append((ur.id, new_ur))

    db.session.flush()

    for old_id, new_ur in new_units:
        unit_map[old_id] = new_ur.id

    return unit_map


def _clone_categories(categories, template_clone, sid):
    """Clone categories and build a mapping of old IDs to new IDs."""
    category_map = {}
    new_categories = []

    for c in categories:
        new_c = DegreeProgressCategory(
            accent_color=c.accent_color,
            category_type=c.category_type,
            course_units=c.course_units,
            description=c.description,
            grade=c.grade,
            is_satisfied_by_transfer_course=(
                False if sid else c.is_satisfied_by_transfer_course
            ),
            name=c.name,
            parent_category_id=None,
            template_id=template_clone.id,
            ux_position_x=c.ux_position_x,
            ux_position_y=c.ux_position_y,
        )
        db.session.add(new_c)
        new_categories.append((c.id, new_c))

    db.session.flush()

    for old_id, new_c in new_categories:
        category_map[old_id] = new_c.id

    return category_map


def _apply_category_unit_links(links, category_map, unit_map):
    """Recreate category-to-unit-requirement relationships."""
    db.session.bulk_insert_mappings(
        DegreeProgressCategoryUnitRequirement,
        [
            {
                "category_id": category_map[link.category_id],
                "unit_requirement_id": unit_map[link.unit_requirement_id],
            }
            for link in links
        ],
    )


def fetch_degree_template(template_id):
    template = DegreeProgressTemplate.find_by_id(template_id)
    if not template:
        raise ResourceNotFoundError(f"No template found with id={template_id}.")
    return template


def validate_template_not_archived(template_id):
    if template_id:
        template = fetch_degree_template(template_id)
        # Templates specific to a student are not editable when in archived mode.
        if template and template.student_sid and template.archived_at:
            raise BadRequestError("Degree is locked and cannot be edited.")


def validate_template_upsert(name, template_id=None):
    if not name:
        raise BadRequestError("'name' is required.")
    # Name must be unique across non-deleted templates
    template = DegreeProgressTemplate.find_by_name(name=name, case_insensitive=True)
    if template and (template_id is None or template_id != template.id):
        raise BadRequestError(
            f"A degree named <strong>{name}</strong> already exists. Please choose a different name.",
        )
    return template
