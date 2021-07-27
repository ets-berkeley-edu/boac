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

from boac.api.degree_progress_api_utils import clone_degree_template, create_batch_degree_checks
from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.api.util import can_edit_degree_progress, can_read_degree_progress
from boac.externals.data_loch import get_basic_student_data, get_sid_by_uid
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, is_int, to_bool_or_none, to_int_or_none
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_course import ACCENT_COLOR_CODES, DegreeProgressCourse
from boac.models.degree_progress_course_unit_requirement import DegreeProgressCourseUnitRequirement
from boac.models.degree_progress_note import DegreeProgressNote
from boac.models.degree_progress_template import DegreeProgressTemplate
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/degree/check/batch', methods=['POST'])
@can_edit_degree_progress
def batch_degree_checks():
    params = request.get_json()
    sids = get_param(params, 'sids')
    template_id = get_param(params, 'templateId')
    if not template_id or not sids:
        raise BadRequestError('sids and templateId are required.')
    return tolerant_jsonify(create_batch_degree_checks(template_id=template_id, sids=sids))


@app.route('/api/degree/check/<sid>/create', methods=['POST'])
@can_edit_degree_progress
def create_degree_check(sid):
    params = request.get_json()
    template_id = get_param(params, 'templateId')
    if not template_id or not is_int(sid):
        raise BadRequestError('sid and templateId are required.')
    return tolerant_jsonify(clone_degree_template(template_id=template_id, sid=sid).to_api_json())


@app.route('/api/degree/course/copy', methods=['POST'])
@can_edit_degree_progress
def copy_course():
    params = request.get_json()
    category_id = to_int_or_none(get_param(params, 'categoryId'))
    section_id = to_int_or_none(get_param(params, 'sectionId'))
    sid = get_param(params, 'sid')
    term_id = to_int_or_none(get_param(params, 'termId'))
    if False in [is_int(v) for v in (category_id, section_id, sid, term_id)]:
        raise BadRequestError('category_id, section_id, sid, and term_id are required.')

    category = DegreeProgressCategory.find_by_id(category_id)
    courses = DegreeProgressCourse.get_courses(
        degree_check_id=category.template_id,
        section_id=section_id,
        sid=sid,
        term_id=term_id,
    )
    if not len(courses):
        raise ResourceNotFoundError('Course not found.')

    elif len(courses) == 1 and not courses[0].category_id:
        raise BadRequestError(f'Course {courses[0].id} is unassigned. Use the /assign API instead.')

    else:
        if not _can_accept_course_requirements(category):
            raise BadRequestError(f'A \'Course Requirement\' cannot be added to a {category.category_type}.')

        # Verify that course is not already in the requested category/subcategory.
        for c in DegreeProgressCourse.find_by_category_id(category.id):
            if c.section_id == section_id and c.sid == sid and c.term_id:
                raise BadRequestError(f'Course already belongs to category {category.name}.')
        for child in DegreeProgressCategory.find_by_parent_category_id(category_id):
            if child.id == category_id:
                raise BadRequestError(f'Course already belongs to category {category.name}.')

        # Create a new course instance and a new 'Course Requirement'.
        course = courses[0]
        course = DegreeProgressCourse.create(
            degree_check_id=category.template_id,
            display_name=course.display_name,
            grade=course.grade,
            section_id=course.section_id,
            sid=course.sid,
            term_id=course.term_id,
            unit_requirement_ids=[u.unit_requirement_id for u in course.unit_requirements],
            units=course.units,
        )
        course_requirement = DegreeProgressCategory.create(
            category_type='Placeholder: Course Copy',
            name=course.display_name,
            position=category.position,
            template_id=category.template_id,
            course_units_lower=course.units,
            course_units_upper=course.units,
            parent_category_id=category.id,
            unit_requirement_ids=[u.unit_requirement_id for u in category.unit_requirements],
        )
        DegreeProgressCourse.assign(category_id=course_requirement.id, course_id=course.id)
        return tolerant_jsonify(DegreeProgressCourse.find_by_id(course.id).to_api_json())


@app.route('/api/degree/course/<course_id>', methods=['DELETE'])
@can_edit_degree_progress
def delete_course(course_id):
    course = DegreeProgressCourse.find_by_id(course_id)
    if course:
        # Verify that course is a copy
        matches = DegreeProgressCourse.get_courses(
            degree_check_id=course.degree_check_id,
            section_id=course.section_id,
            sid=course.sid,
            term_id=course.term_id,
        )
        matches = sorted(matches, key=lambda c: c.created_at)
        if matches[0].id == course.id:
            raise BadRequestError('Only copied courses can be deleted.')

        category = DegreeProgressCategory.find_by_id(course.category_id)
        DegreeProgressCourseUnitRequirement.delete(course.id)
        DegreeProgressCourse.delete(course)
        if 'Placeholder' in category.category_type:
            DegreeProgressCategory.delete(category_id=category.id)

        # Update updated_at date of top-level record
        DegreeProgressTemplate.refresh_updated_at(category.template_id)
        return tolerant_jsonify({'message': f'Course {course_id} deleted'}), 200
    else:
        raise ResourceNotFoundError('Course not found.')


@app.route('/api/degree/course/<course_id>/assign', methods=['POST'])
@can_edit_degree_progress
def assign_course(course_id):
    params = request.get_json()
    course = DegreeProgressCourse.find_by_id(course_id)
    if course:
        # Get existing category assignment. If it's a placeholder then delete it at end of transaction.
        previous_category = DegreeProgressCategory.find_by_id(course.category_id) if course.category_id else None
        category_id = get_param(params, 'categoryId')
        category = DegreeProgressCategory.find_by_id(category_id) if category_id else None
        if category:
            if category.template_id != course.degree_check_id:
                raise BadRequestError('The category and course do not belong to the same degree_check instance.')
            children = DegreeProgressCategory.find_by_parent_category_id(parent_category_id=category_id)
            if next((c for c in children if c.category_type == 'Subcategory'), None):
                raise BadRequestError('A course cannot be assigned to a category with a subcategory.')
            course = DegreeProgressCourse.assign(category_id=category_id, course_id=course.id)

        else:
            # When user un-assigns a course we delete all copies of that course,.
            for copy_of_course in DegreeProgressCourse.get_courses(
                    degree_check_id=course.degree_check_id,
                    section_id=course.section_id,
                    sid=course.sid,
                    term_id=course.term_id,
            ):
                if copy_of_course.id != course.id:
                    DegreeProgressCourseUnitRequirement.delete(copy_of_course.id)
                    category = DegreeProgressCategory.find_by_id(copy_of_course.category_id)
                    if category and 'Placeholder' in category.category_type:
                        DegreeProgressCategory.delete(category.id)
                    DegreeProgressCourse.delete(copy_of_course)
            ignore = to_bool_or_none(get_param(params, 'ignore'))
            course = DegreeProgressCourse.unassign(course_id=course.id, ignore=ignore)

        # If previous assignment was a "placeholder" category then delete it.
        if previous_category and 'Placeholder' in previous_category.category_type:
            DegreeProgressCategory.delete(previous_category.id)

        # Update updated_at date of top-level record
        DegreeProgressTemplate.refresh_updated_at(course.degree_check_id)
        return tolerant_jsonify(course.to_api_json())
    else:
        raise ResourceNotFoundError('Course not found.')


@app.route('/api/degrees/student/<uid>')
@can_read_degree_progress
def get_degree_checks(uid):
    sid = get_sid_by_uid(uid)
    if sid:
        return tolerant_jsonify(DegreeProgressTemplate.find_by_sid(student_sid=sid))
    else:
        raise ResourceNotFoundError('Student not found')


@app.route('/api/degree/<template_id>/students', methods=['POST'])
@can_edit_degree_progress
def get_students(template_id):
    params = request.get_json()
    sids = get_param(params, 'sids')
    if not sids:
        raise BadRequestError('sids is required.')
    template = DegreeProgressTemplate.find_by_id(template_id)
    if not template:
        raise ResourceNotFoundError('Degree template not found')
    degree_checks = DegreeProgressTemplate.get_student_degree_checks_by_parent_template_id(template_id, sids)
    sids = [d.student_sid for d in degree_checks]
    students = get_basic_student_data(sids)

    def _to_api_json(student):
        return {
            'sid': student['sid'],
            'uid': student['uid'],
            'firstName': student['first_name'],
            'lastName': student['last_name'],
        }
    return tolerant_jsonify([_to_api_json(student) for student in students])


@app.route('/api/degree/course/create', methods=['POST'])
@can_edit_degree_progress
def create_course():
    params = request.get_json()
    degree_check_id = get_param(params, 'degreeCheckId')
    grade = get_param(params, 'grade')
    name = get_param(params, 'name')
    note = get_param(params, 'note')
    sid = get_param(params, 'sid')
    value = get_param(request.get_json(), 'unitRequirementIds')
    unit_requirement_ids = list(filter(None, value.split(','))) if isinstance(value, str) else value
    units = get_param(params, 'units')

    if 0 in map(lambda v: len(str(v).strip()) if v else 0, (grade, name, sid, units)):
        raise BadRequestError('Missing one or more required parameters')
    course = DegreeProgressCourse.create(
        accent_color=_normalize_accent_color(get_param(params, 'accentColor')),
        degree_check_id=degree_check_id,
        display_name=name,
        grade=grade,
        manually_created_by=current_user.get_id(),
        note=note,
        section_id=None,
        sid=sid,
        term_id=None,
        unit_requirement_ids=unit_requirement_ids or (),
        units=units,
    )
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(course.degree_check_id)
    return tolerant_jsonify(course.to_api_json())


@app.route('/api/degree/course/<course_id>/update', methods=['POST'])
@can_edit_degree_progress
def update_course(course_id):
    params = request.get_json()
    note = get_param(params, 'note')
    # Courses are mapped to degree_progress_unit_requirements
    value = get_param(request.get_json(), 'unitRequirementIds')
    unit_requirement_ids = list(filter(None, value.split(','))) if isinstance(value, str) else value
    units = get_param(params, 'units')
    if units is None:
        raise BadRequestError('units parameter is required.')
    course = DegreeProgressCourse.update(
        course_id=course_id,
        note=note,
        unit_requirement_ids=unit_requirement_ids,
        units=units,
    )
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(course.degree_check_id)
    return tolerant_jsonify(course.to_api_json())


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
    # Update updated_at date of top-level record
    DegreeProgressTemplate.refresh_updated_at(degree_check_id)
    return tolerant_jsonify(note.to_api_json())


def _can_accept_course_requirements(category):
    if category.category_type == 'Category':
        # Weird rule alert: A type='Category' can only have course requirements if it has no 'Subcategory'.
        return len(_get_category_children(category.id, 'Subcategory')) == 0
    else:
        return category.category_type == 'Subcategory'


def _get_category_children(category_id, category_type):
    children = DegreeProgressCategory.find_by_parent_category_id(category_id)
    return list(filter(lambda c: c.category_type == category_type, children))


def _normalize_accent_color(color):
    if color:
        capitalized = color.capitalize()
        return capitalized if capitalized in list(ACCENT_COLOR_CODES.keys()) else None
