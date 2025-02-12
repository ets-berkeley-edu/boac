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

from bea.config.bea_test_config import BEATestConfig
from bea.models.degree_progress.degree_check import DegreeCheck
from bea.models.degree_progress.degree_check_perms import DegreeCheckPerms
from bea.models.degree_progress.degree_completed_course import DegreeCompletedCourse
from bea.test_utils import boa_degree_progress_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest

test = BEATestConfig()
test.degree_check()
student = test.default_cohort.members[0]
nessie_utils.set_student_term_enrollments([student])

template = next(filter(lambda t: 'Course Workflows' in t.name, test.degree_templates))
degree_check = DegreeCheck({}, template, student)

cats_with_courses = list(filter(lambda ca: ca.course_reqts, degree_check.categories))
course_reqt_1 = cats_with_courses[0].course_reqts[0]
course_reqt_2 = cats_with_courses[-1].course_reqts[-1]
cat_no_subs_no_courses = next(filter(lambda ca: not ca.sub_categories and not ca.course_reqts, degree_check.categories))
cat_with_courses_no_subs = next(filter(lambda ca: ca.course_reqts and not ca.sub_categories, degree_check.categories))
cats_with_subs = list(filter(lambda ca: ca.sub_categories, degree_check.categories))
cat_with_subs = cats_with_subs[0]
sub_cats_no_courses = []
sub_cats_with_courses = []
for cat in cats_with_subs:
    for sub_cat in cat.sub_categories:
        if sub_cat.course_reqts:
            sub_cats_with_courses.append(sub_cat)
        else:
            sub_cats_no_courses.append(sub_cat)
sub_cat_no_courses = sub_cats_no_courses[0]
sub_cat_with_courses = sub_cats_with_courses[0]
course_reqt_3 = sub_cat_with_courses.course_reqts[-1]

app.logger.info(f'Top level category course requirements: {course_reqt_1.name} and {course_reqt_2.name}')
app.logger.info(f'Top level category with no subcategories and no courses: {cat_no_subs_no_courses.name}')
app.logger.info(f'Top level category with no subcategories but with courses: {cat_with_courses_no_subs.name}')
app.logger.info(f'Top level category with subcategory: {cat_with_subs}')
app.logger.info(f'Subcategory with no courses: {sub_cat_no_courses.name}')
app.logger.info(f'Subcategory with courses: {sub_cat_with_courses.name}')

transfer_course_reqt = degree_check.get_transfer_courses()[0]
transfer_course = DegreeCompletedCourse.generate_transfer_course(degree_check, transfer_course_reqt)

manual_course_0 = DegreeCompletedCourse({
    'color': 'green',
    'grade': 'A++',
    'is_manual': True,
    'name': f'BEA 101 {test.test_id}',
    'note': f'Course level note {test.test_id}',
    'units': '1',
    'unit_reqts': [degree_check.unit_reqts[0]],
})
manual_course_1 = DegreeCompletedCourse({
    'is_manual': True,
    'name': f'BEA 1A {test.test_id}',
    'units': '4.35',
})
manual_course_2 = DegreeCompletedCourse({
    'is_manual': True,
    'name': f'BEA 1B {test.test_id}',
    'units': '4',
})
manual_course_3 = DegreeCompletedCourse({
    'is_manual': True,
    'name': f'BEA 1C {test.test_id}',
    'units': '4',
})
manual_course_4 = DegreeCompletedCourse({
    'is_manual': True,
    'name': f'BEA COPIES 1A {test.test_id}',
    'units': '4',
})
manual_course_5 = DegreeCompletedCourse({
    'is_manual': True,
    'name': f'BEA COPIES 1B {test.test_id}',
    'units': '4',
})


@pytest.mark.usefixtures('page_objects')
class TestDegreeCheckSetup:

    def test_set_advisor_perms(self):
        self.homepage.load_page()
        self.homepage.dev_auth()
        self.pax_manifest_page.load_page()
        self.pax_manifest_page.set_deg_prog_perm(test.advisor, test.dept, DegreeCheckPerms.WRITE)
        self.pax_manifest_page.set_deg_prog_perm(test.advisor_read_only, test.dept, DegreeCheckPerms.READ)

    def test_create_template(self):
        self.pax_manifest_page.log_out()
        self.homepage.dev_auth(test.advisor)
        self.homepage.click_degree_checks()
        self.degree_template_mgmt_page.create_new_degree(template)
        self.degree_template_page.complete_template(template)

    def test_create_student_degree_check(self):
        self.degree_check_create_page.load_page(student)
        self.degree_check_create_page.create_new_degree_check(degree_check)
        self.degree_check_page.load_page(degree_check)


@pytest.mark.usefixtures('page_objects')
class TestTransferCourse:

    def test_created_automatically_with_degree_check(self):
        self.degree_check_page.wait_for_spinner()
        boa_degree_progress_utils.set_degree_manual_course_id(degree_check, transfer_course)
        utils.assert_equivalence(self.degree_check_page.assigned_course_name(transfer_course), transfer_course.name)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(transfer_course), transfer_course.units)
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(transfer_course), transfer_course.grade)

    def test_can_be_edited(self):
        transfer_course.grade = 'A'
        transfer_course.note = f'Note {test.test_id}'
        transfer_course.units = '6'
        self.degree_check_page.edit_assigned_course(transfer_course)
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(transfer_course), transfer_course.grade)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(transfer_course), transfer_course.note)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(transfer_course), transfer_course.units)

    def test_can_be_unassigned(self):
        self.degree_check_page.unassign_course(transfer_course)


@pytest.mark.usefixtures('page_objects')
class TestManualCourseCreation:

    def test_can_be_canceled(self):
        self.degree_check_page.click_create_course(sub_cat_with_courses)
        self.degree_check_page.click_cancel_course_create()

    def test_requires_a_name(self):
        self.degree_check_page.click_create_course(sub_cat_with_courses)
        self.degree_check_page.enter_course_units(manual_course_0.units)
        assert not self.degree_check_page.element(self.degree_check_page.CREATE_COURSE_SAVE_BUTTON).is_enabled()

    def test_does_not_require_units(self):
        self.degree_check_page.enter_course_units('')
        self.degree_check_page.enter_course_name(manual_course_0.name)
        assert self.degree_check_page.element(self.degree_check_page.CREATE_COURSE_SAVE_BUTTON).is_enabled()

    def test_can_be_saved(self):
        self.degree_check_page.click_cancel_course_create()
        self.degree_check_page.create_manual_course(degree_check, manual_course_0, sub_cat_with_courses)

    def test_shows_course_name(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_name(manual_course_0), manual_course_0.name)

    def test_shows_course_units(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(manual_course_0), manual_course_0.units)

    def test_shows_course_grade(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(manual_course_0), manual_course_0.grade)

    def test_shows_course_note(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(manual_course_0), manual_course_0.note)


@pytest.mark.usefixtures('page_objects')
class TestManualCourseEditing:

    def test_can_be_canceled(self):
        self.degree_check_page.click_edit_assigned_course(manual_course_0)
        self.degree_check_page.click_cancel_course_edit()

    def test_requires_a_name(self):
        self.degree_check_page.click_edit_assigned_course(manual_course_0)
        self.degree_check_page.enter_course_name('')
        assert not self.degree_check_page.element(self.degree_check_page.COURSE_UPDATE_BUTTON).is_enabled()

    def test_does_not_require_units(self):
        self.degree_check_page.enter_course_name(manual_course_0.name)
        self.degree_check_page.enter_course_units('')
        assert self.degree_check_page.element(self.degree_check_page.COURSE_UPDATE_BUTTON).is_enabled()

    def test_edits_course_units(self):
        self.degree_check_page.click_cancel_course_edit()
        manual_course_0.units = ''
        self.degree_check_page.edit_assigned_course(manual_course_0)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(manual_course_0), '—')

    def test_edits_course_grade(self):
        manual_course_0.grade = 'F?'
        self.degree_check_page.edit_assigned_course(manual_course_0)
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(manual_course_0), manual_course_0.grade)

    def test_edits_course_color_code(self):
        manual_course_0.color = 'blue'
        self.degree_check_page.edit_assigned_course(manual_course_0)

    def test_edits_course_note(self):
        manual_course_0.note = f'EDITED - {manual_course_0.note}'
        self.degree_check_page.edit_assigned_course(manual_course_0)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(manual_course_0), manual_course_0.note)


@pytest.mark.usefixtures('page_objects')
class TestManualCourseUnassigned:

    def test_unassigned_manual_course(self):
        self.degree_check_page.unassign_course(manual_course_0, sub_cat_with_courses)

    def test_edit_but_cancel(self):
        self.degree_check_page.click_edit_unassigned_course(manual_course_0)
        self.degree_check_page.click_cancel_course_edit()

    def test_edit_requires_a_name(self):
        self.degree_check_page.click_edit_unassigned_course(manual_course_0)
        self.degree_check_page.enter_course_name('')
        assert not self.degree_check_page.element(self.degree_check_page.COURSE_UPDATE_BUTTON).is_enabled()

    def test_edit_does_not_require_units(self):
        self.degree_check_page.enter_course_name(manual_course_0.name)
        self.degree_check_page.enter_course_units('')
        assert self.degree_check_page.element(self.degree_check_page.COURSE_UPDATE_BUTTON).is_enabled()

    def test_edit_name(self):
        manual_course_0.name = f'AGAIN {manual_course_0.name}'
        self.degree_check_page.enter_course_name(manual_course_0.name)
        self.degree_check_page.click_save_course_edit()
        utils.assert_equivalence(self.degree_check_page.unassigned_course_code(manual_course_0), manual_course_0.name)

    def test_edit_units(self):
        manual_course_0.units = '0.35'
        self.degree_check_page.edit_unassigned_course(manual_course_0)
        utils.assert_equivalence(self.degree_check_page.unassigned_course_units(manual_course_0), manual_course_0.units)

    def test_edit_grade(self):
        manual_course_0.grade = 'C#'
        self.degree_check_page.edit_unassigned_course(manual_course_0)
        utils.assert_equivalence(self.degree_check_page.unassigned_course_grade(manual_course_0), manual_course_0.grade)

    def test_edit_color_code(self):
        manual_course_0.color = 'purple'
        self.degree_check_page.edit_unassigned_course(manual_course_0)

    def test_edit_unit_fulfillment(self):
        manual_course_0.unit_reqts = [degree_check.unit_reqts[1]]
        self.degree_check_page.edit_unassigned_course(manual_course_0)

    def test_edit_note(self):
        manual_course_0.note = f'AGAIN {manual_course_0.note}'
        self.degree_check_page.edit_unassigned_course(manual_course_0)
        utils.assert_equivalence(self.degree_check_page.unassigned_course_note(manual_course_0), manual_course_0.note)


@pytest.mark.usefixtures('page_objects')
class TestManualCourseAssignment:

    def test_assign_to_category(self):
        self.degree_check_page.assign_completed_course(manual_course_0, cat_no_subs_no_courses)

    def test_move_from_category_to_subcategory(self):
        self.degree_check_page.reassign_course(manual_course_0, cat_no_subs_no_courses, sub_cat_no_courses)

    def test_move_from_subcategory_to_category(self):
        self.degree_check_page.reassign_course(manual_course_0, sub_cat_no_courses, cat_no_subs_no_courses)

    def test_move_from_category_to_course_reqt(self):
        self.degree_check_page.reassign_course(manual_course_0, cat_no_subs_no_courses, course_reqt_1)

    def test_move_from_course_reqt_to_subcategory(self):
        self.degree_check_page.reassign_course(manual_course_0, course_reqt_1, sub_cat_no_courses)

    def test_move_from_subcategory_to_course_reqt(self):
        self.degree_check_page.reassign_course(manual_course_0, sub_cat_with_courses, course_reqt_2)

    def test_un_assign(self):
        self.degree_check_page.unassign_course(manual_course_0, course_reqt_2)

    def test_wish_to_cornfield(self):
        self.degree_check_page.wish_to_cornfield(manual_course_0)


@pytest.mark.usefixtures('page_objects')
class TestManualCourseDeletion:

    def test_setup(self):
        self.degree_check_page.create_manual_course(degree_check, manual_course_1, sub_cat_with_courses)
        self.degree_check_page.unassign_course(manual_course_1, sub_cat_with_courses)
        self.degree_check_page.create_manual_course(degree_check, manual_course_2, sub_cat_with_courses)
        self.degree_check_page.wish_to_cornfield(manual_course_2, sub_cat_with_courses)
        self.degree_check_page.create_manual_course(degree_check, manual_course_3, sub_cat_with_courses)
        self.degree_check_page.reassign_course(manual_course_3, sub_cat_with_courses, course_reqt_2)

    def test_delete_from_unassigned(self):
        self.degree_check_page.delete_unassigned_course(manual_course_1)
        self.degree_check_page.when_not_present(self.degree_check_page.unassigned_course_row(manual_course_1),
                                                utils.get_short_timeout())

    def test_delete_from_cornfield(self):
        self.degree_check_page.delete_junk_course(manual_course_2)
        self.degree_check_page.when_not_present(self.degree_check_page.junk_course_row(manual_course_2),
                                                utils.get_short_timeout())

    def test_delete_from_reqt(self):
        self.degree_check_page.delete_assigned_course(manual_course_3)
        self.degree_check_page.when_not_present(self.degree_check_page.assigned_course_row(manual_course_3),
                                                utils.get_short_timeout())


@pytest.mark.usefixtures('page_objects')
class TestManualCourseCopy:

    cat_copy = manual_course_5.generate_course_copy()
    sub_cat_copy = manual_course_4.generate_course_copy()

    def test_setup(self):
        self.degree_check_page.create_manual_course(degree_check, manual_course_4, sub_cat_with_courses)
        self.degree_check_page.create_manual_course(degree_check, manual_course_5, sub_cat_with_courses)
        self.degree_check_page.reassign_course(manual_course_4, sub_cat_with_courses, cat_no_subs_no_courses)
        self.degree_check_page.reassign_course(manual_course_5, sub_cat_with_courses, sub_cat_no_courses)

    def test_copy_to_category(self):
        self.degree_check_page.unassign_course(manual_course_5, sub_cat_with_courses)
        self.degree_check_page.copy_course(manual_course_5, self.cat_copy, cat_no_subs_no_courses)

    def test_copy_to_category_shows_units(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(self.cat_copy), self.cat_copy.units)

    def test_copy_to_category_shows_grade(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(self.cat_copy), (self.cat_copy.grade or ''))

    def test_copy_to_category_shows_note(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(self.cat_copy), (self.cat_copy.note or '—'))

    def test_copy_to_category_shows_copy_icon(self):
        assert self.degree_check_page.is_assigned_course_copy_flagged(self.cat_copy)

    def test_copy_to_category_has_delete_button(self):
        assert self.degree_check_page.is_present(self.degree_check_page.assigned_course_delete_button(self.cat_copy))

    def test_copy_to_category_has_reassign_button(self):
        assert self.degree_check_page.is_present(self.degree_check_page.assigned_course_select(self.cat_copy))

    def test_copy_to_subcategory(self):
        self.degree_check_page.copy_course(manual_course_4, self.sub_cat_copy, sub_cat_no_courses)

    def test_copy_to_subcategory_shows_units(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(self.sub_cat_copy), self.sub_cat_copy.units)

    def test_copy_to_subcategory_shows_grade(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(self.sub_cat_copy), (self.sub_cat_copy.grade or ''))

    def test_copy_to_subcategory_shows_note(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(self.sub_cat_copy), (self.sub_cat_copy.note or '—'))

    def test_copy_to_subcategory_shows_copy_icon(self):
        assert self.degree_check_page.is_assigned_course_copy_flagged(self.sub_cat_copy)

    def test_copy_to_subcategory_has_delete_button(self):
        assert self.degree_check_page.is_present(self.degree_check_page.assigned_course_delete_button(self.sub_cat_copy))

    def test_copy_to_subcategory_has_reassign_button(self):
        assert self.degree_check_page.is_present(self.degree_check_page.assigned_course_select(self.sub_cat_copy))

    def test_copy_edit_but_cancel(self):
        self.degree_check_page.click_edit_assigned_course(self.sub_cat_copy)
        self.degree_check_page.click_cancel_course_edit()

    def test_copy_edit_name(self):
        self.degree_check_page.click_edit_assigned_course(self.sub_cat_copy)
        self.sub_cat_copy.name = f'EDITED - {self.sub_cat_copy.name}'
        self.degree_check_page.enter_course_name(self.sub_cat_copy.name)
        self.degree_check_page.click_save_course_edit()
        utils.assert_equivalence(self.degree_check_page.assigned_course_name(self.sub_cat_copy), self.sub_cat_copy.name)
        assert self.degree_check_page.is_assigned_course_copy_flagged(self.sub_cat_copy)

    def test_copy_edit_units(self):
        self.sub_cat_copy.units = ''
        self.degree_check_page.edit_assigned_course(self.sub_cat_copy)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(self.sub_cat_copy), '—')

    def test_copy_edit_grade(self):
        self.sub_cat_copy.grade = '£5'
        self.degree_check_page.edit_assigned_course(self.sub_cat_copy)
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(self.sub_cat_copy), self.sub_cat_copy.grade)

    def test_copy_edit_color_code(self):
        self.sub_cat_copy.color = 'blue'
        self.degree_check_page.edit_assigned_course(self.sub_cat_copy)

    def test_copy_edit_unit_fulfillment(self):
        self.sub_cat_copy.unit_reqts = [degree_check.unit_reqts[0]]
        self.degree_check_page.edit_assigned_course(self.sub_cat_copy)

    def test_copy_edit_note(self):
        self.sub_cat_copy.note = f'EDITED - {self.sub_cat_copy.note}'
        self.degree_check_page.edit_assigned_course(self.sub_cat_copy)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(self.sub_cat_copy), self.sub_cat_copy.note)

    def test_copy_edits_do_not_affect_original(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_name(manual_course_4), manual_course_4.name)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(manual_course_4), manual_course_4.units)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(manual_course_4), (manual_course_4.note or '—'))
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(manual_course_4), (manual_course_4.grade or ''))

    def test_copy_delete_but_cancel(self):
        self.degree_check_page.click_delete_assigned_course(self.sub_cat_copy)
        self.degree_check_page.cancel_delete_or_discard()

    def test_copy_delete(self):
        self.degree_check_page.delete_assigned_course(self.sub_cat_copy)

    def test_copy_deletion_does_not_affect_original(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_name(manual_course_4), manual_course_4.name)

    def test_copy_original_un_assignment_does_not_delete_copy(self):
        copy_no_deleting = manual_course_4.generate_course_copy()
        self.degree_check_page.copy_course(manual_course_4, copy_no_deleting, sub_cat_no_courses)
        self.degree_check_page.unassign_course(manual_course_4, cat_no_subs_no_courses)
        assert self.degree_check_page.is_present(self.degree_check_page.assigned_course_row(copy_no_deleting))
