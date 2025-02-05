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
import re

from bea.config.bea_test_config import BEATestConfig
from bea.models.degree_progress.degree_check import DegreeCheck
from bea.models.degree_progress.degree_check_perms import DegreeCheckPerms
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest

test = BEATestConfig()
test.degree_check(opts={'enrolled': True})
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

nessie_utils.set_student_profiles([student])
nessie_utils.set_student_term_enrollments([student])
in_progress_courses = student.enrollment_data.degree_progress_in_prog_courses(degree_check)
unassigned_courses = student.enrollment_data.degree_progress_courses(degree_check)
completed_course_0 = unassigned_courses[0]
completed_course_1 = unassigned_courses[1]
completed_course_2 = unassigned_courses[2]
completed_course_3 = unassigned_courses[3]
completed_course_4 = unassigned_courses[4]
cat_copy = completed_course_4.generate_course_copy()
sub_cat_copy = completed_course_4.generate_course_copy()


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
class TestDegreeCheckRequirement:

    def test_mark_ignored_or_completed(self):
        self.degree_check_page.click_edit_course_reqt(course_reqt_3)
        self.degree_check_page.click_ignore_reqt()
        self.degree_check_page.click_save_reqt_edit()
        assert self.degree_check_page.is_visible_course_reqt_name_struck(course_reqt_3)

    def test_un_mark_ignored_or_completed(self):
        self.degree_check_page.click_edit_course_reqt(course_reqt_3)
        self.degree_check_page.click_ignore_reqt()
        self.degree_check_page.click_save_reqt_edit()
        assert not self.degree_check_page.is_visible_course_reqt_name_struck(course_reqt_3)


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseInProgress:

    def test_in_progress_list(self):
        if in_progress_courses:
            self.degree_check_page.when_present(self.degree_check_page.IN_PROGRESS_COURSE, utils.get_short_timeout())
            visible = self.degree_check_page.in_progress_course_ccns()
            visible.sort()
            expected = [f'{c.term_id}-{c.ccn}' for c in in_progress_courses]
            expected.sort()
            utils.assert_equivalence(visible, expected)

    def test_in_progress_course_names(self):
        for course in in_progress_courses:
            wl = '(WAITLISTED)' if course.is_wait_listed else ''
            expected = f'{course.name}{wl}'.replace(' ', '')
            visible = re.sub(r'\s+', '', self.degree_check_page.in_progress_course_code(course))
            utils.assert_equivalence(visible, expected)

    def test_in_progress_course_units(self):
        for course in in_progress_courses:
            utils.assert_equivalence(self.degree_check_page.in_progress_course_units(course),
                                     utils.formatted_units(float(course.units)))


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseUnassigned:

    def test_unassigned_list(self):
        self.degree_check_page.when_present(self.degree_check_page.UNASSIGNED_COURSE, utils.get_short_timeout())
        visible = self.degree_check_page.unassigned_course_ccns()
        visible.sort()
        expected = [f'{c.term_id}-{c.ccn}' for c in unassigned_courses]
        expected.sort()
        utils.assert_equivalence(visible, expected)

    def test_unassigned_course_names(self):
        for course in unassigned_courses:
            utils.assert_equivalence(self.degree_check_page.unassigned_course_code(course), course.name)

    def test_unassigned_course_units(self):
        for course in unassigned_courses:
            utils.assert_equivalence(self.degree_check_page.unassigned_course_units(course),
                                     utils.formatted_units(float(course.units)))

    def test_unassigned_course_grades(self):
        for course in unassigned_courses:
            utils.assert_equivalence(self.degree_check_page.unassigned_course_grade(course), course.grade)

    def test_unassigned_course_term(self):
        for course in unassigned_courses:
            term = utils.term_sis_id_to_term_name(course.term_id)
            if 'Summer' in term:
                term = ' '.join(['Sum', term.split()[1]])
            elif 'Spring' in term:
                term = ' '.join(['Spr', term.split()[1]])
            utils.assert_equivalence(self.degree_check_page.unassigned_course_term(course), term)

    def test_unassigned_edit_and_cancel(self):
        self.degree_check_page.click_edit_unassigned_course(completed_course_0)
        self.degree_check_page.click_cancel_course_edit()

    def test_unassigned_add_note(self):
        completed_course_0.note = f'Teena wuz here {test.test_id}' * 10
        self.degree_check_page.edit_unassigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.unassigned_course_note(completed_course_0),
                                 completed_course_0.note)

    def test_unassigned_expand_note(self):
        self.degree_check_page.expand_unassigned_course_note(completed_course_0)

    def test_unassigned_hide_note(self):
        self.degree_check_page.click_hide_note()

    def test_unassigned_edit_note(self):
        completed_course_0.note = f'EDITED - {completed_course_0.note}'
        self.degree_check_page.edit_unassigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.unassigned_course_note(completed_course_0),
                                 completed_course_0.note)

    def test_unassigned_remove_note(self):
        completed_course_0.note = ''
        self.degree_check_page.edit_unassigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.unassigned_course_note(completed_course_0), '—')

    def test_unassigned_edit_units_integer(self):
        completed_course_0.units = str(float(completed_course_0.units) + 1)
        self.degree_check_page.edit_unassigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.unassigned_course_units(completed_course_0),
                                 utils.formatted_units(float(completed_course_0.units)))

    def test_unassigned_edited_units_indicator(self):
        assert self.degree_check_page.is_unassigned_course_units_flagged(completed_course_0)

    def test_unassigned_non_number_units_not_allowed(self):
        self.degree_check_page.click_edit_unassigned_course(completed_course_0)
        self.degree_check_page.enter_course_units('A')
        self.degree_check_page.wait_for_units_numeric_error_msg()
        assert not self.degree_check_page.element(self.degree_check_page.COURSE_UPDATE_BUTTON).is_enabled()

    def test_unassigned_decimal_units_allowed(self):
        self.degree_check_page.click_cancel_course_edit()
        completed_course_0.units = str(float(completed_course_0.units) + 0.53)
        self.degree_check_page.edit_unassigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.unassigned_course_units(completed_course_0),
                                 utils.formatted_units(float(completed_course_0.units)))

    def test_unassigned_units_two_digit_integer_max(self):
        self.degree_check_page.click_edit_unassigned_course(completed_course_0)
        self.degree_check_page.enter_course_units('100')
        self.degree_check_page.wait_for_units_numeric_error_msg()
        assert not self.degree_check_page.element(self.degree_check_page.COURSE_UPDATE_BUTTON).is_enabled()


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseAssignedToCourseReqt:

    def test_assignment_updates_reqt_row_with_course_name(self):
        self.degree_check_page.click_cancel_course_edit()
        completed_course_0.note = f'Teena wuz here again {test.test_id}' * 10
        self.degree_check_page.edit_unassigned_course(completed_course_0)
        self.degree_check_page.assign_completed_course(completed_course_0, course_reqt_1)

    def test_assignment_updates_reqt_row_with_course_units(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(completed_course_0).split()[0],
                                 utils.formatted_units(float(completed_course_0.units)))

    def test_assignment_updates_reqt_row_with_course_grade(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(completed_course_0),
                                 completed_course_0.grade)

    def test_assignment_updates_reqt_row_with_course_note(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(completed_course_0),
                                 completed_course_0.note)

    def test_assignment_removes_unassigned_course(self):
        visible_unassigned = self.degree_check_page.unassigned_course_ccns()
        assert f'{completed_course_0.term_id}-{completed_course_0.ccn}' not in visible_unassigned

    def test_no_dupe_assignment_to_same_reqt(self):
        self.degree_check_page.click_unassigned_course_select(unassigned_courses[-1])
        assert not self.degree_check_page.is_present(self.degree_check_page.assignment_reqt_option(course_reqt_1))

    def test_assigned_edit_and_cancel(self):
        self.degree_check_page.click_edit_assigned_course(completed_course_0)
        self.degree_check_page.click_cancel_course_edit()

    def test_assigned_remove_note(self):
        completed_course_0.note = ''
        self.degree_check_page.edit_assigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(completed_course_0), '—')

    def test_assigned_add_note(self):
        completed_course_0.note = f'Nota bene {test.test_id}'
        self.degree_check_page.edit_assigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(completed_course_0),
                                 completed_course_0.note)

    def test_assigned_expand_note(self):
        self.degree_check_page.expand_assigned_course_note(completed_course_0)

    def test_assigned_hide_note(self):
        self.degree_check_page.click_hide_note()

    def test_assigned_edit_note(self):
        completed_course_0.note = f'EDITED - {completed_course_0.note}'
        self.degree_check_page.edit_assigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(completed_course_0),
                                 completed_course_0.note)

    def test_assigned_edit_units_integer(self):
        completed_course_0.units = str(float(completed_course_0.units) + 1)
        self.degree_check_page.edit_assigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(completed_course_0).split()[0],
                                 utils.formatted_units(float(completed_course_0.units)))

    def test_assigned_edited_units_indicator(self):
        assert self.degree_check_page.is_assigned_course_units_flagged(completed_course_0)

    def test_assigned_non_number_units_not_allowed(self):
        self.degree_check_page.click_edit_assigned_course(completed_course_0)
        self.degree_check_page.enter_course_units('A')
        self.degree_check_page.wait_for_units_numeric_error_msg()
        assert not self.degree_check_page.element(self.degree_check_page.COURSE_UPDATE_BUTTON).is_enabled()

    def test_assigned_decimal_units_allowed(self):
        self.degree_check_page.click_cancel_course_edit()
        completed_course_0.units = str(float(completed_course_0.units) + 0.53)
        self.degree_check_page.edit_assigned_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(completed_course_0).split()[0],
                                 utils.formatted_units(float(completed_course_0.units)))

    def test_assigned_units_two_digit_integer_max(self):
        self.degree_check_page.click_edit_assigned_course(completed_course_0)
        self.degree_check_page.enter_course_units('100')
        self.degree_check_page.wait_for_units_numeric_error_msg()
        assert not self.degree_check_page.element(self.degree_check_page.COURSE_UPDATE_BUTTON).is_enabled()


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseUnAssignedFromCourseReqt:

    def test_un_assigning_reverts_course_reqt_name(self):
        self.degree_check_page.load_page(degree_check)
        self.degree_check_page.when_present(self.degree_check_page.assigned_course_row(completed_course_0),
                                            utils.get_short_timeout())
        self.degree_check_page.unassign_course(completed_course_0, course_reqt_1)

    def test_un_assigning_reverts_course_reqt_units(self):
        if course_reqt_1.units and course_reqt_1.units != '0':
            units = utils.formatted_units(float(course_reqt_1.units))
        else:
            units = '—'
        utils.assert_equivalence(self.degree_check_page.visible_course_reqt_units(course_reqt_1), units)

    def test_un_assigning_removes_course_reqt_grade(self):
        assert not self.degree_check_page.visible_course_reqt_grade(course_reqt_1)

    def test_un_assigning_removes_course_reqt_note(self):
        assert not self.degree_check_page.visible_course_reqt_note(course_reqt_1)

    def test_un_assigning_restores_course_to_unassigned_list(self):
        assert self.degree_check_page.is_present(self.degree_check_page.unassigned_course_row(completed_course_0))


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseJunked:

    def test_junked_course_name(self):
        self.degree_check_page.wish_to_cornfield(completed_course_0)

    def test_junked_course_units(self):
        utils.assert_equivalence(self.degree_check_page.junk_course_units(completed_course_0).split()[0],
                                 utils.formatted_units(float(completed_course_0.units)))

    def test_junked_course_grade(self):
        utils.assert_equivalence(self.degree_check_page.junk_course_grade(completed_course_0),
                                 completed_course_0.grade)

    def test_junked_course_edit_but_cancel(self):
        self.degree_check_page.click_edit_junk_course(completed_course_0)
        self.degree_check_page.click_cancel_course_edit()

    def test_junked_course_add_note(self):
        completed_course_0.note = f'This course no longer sparks joy {test.test_id}'
        self.degree_check_page.edit_junk_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.junk_course_note(completed_course_0),
                                 completed_course_0.note)

    def test_junked_course_expand_note(self):
        self.degree_check_page.expand_junk_course_note(completed_course_0)

    def test_junked_course_hide_note(self):
        self.degree_check_page.click_hide_note()

    def test_junked_edit_units(self):
        completed_course_0.units = '6'
        self.degree_check_page.edit_junk_course(completed_course_0)
        utils.assert_equivalence(self.degree_check_page.junk_course_units(completed_course_0).split()[0],
                                 utils.formatted_units(float(completed_course_0.units)))

    def test_junked_edited_units_flag(self):
        assert self.degree_check_page.is_junk_course_units_flagged(completed_course_0)

    def test_junk_assigned_to_course_reqt(self):
        self.degree_check_page.assign_completed_course(completed_course_0, course_reqt_1)

    def test_re_junk_assigned_course(self):
        self.degree_check_page.wish_to_cornfield(completed_course_0, course_reqt_1)

    def test_de_assign_junked_course(self):
        self.degree_check_page.unassign_course(completed_course_0)


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseReassignedToCourseReqt:

    def test_reassigned_course_updates_new_course_reqt_name(self):
        self.degree_check_page.assign_completed_course(completed_course_0, course_reqt_1)
        self.degree_check_page.reassign_course(completed_course_0, course_reqt_1, course_reqt_2)

    def test_reassigned_course_updates_new_course_reqt_units(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(completed_course_0).split()[0],
                                 utils.formatted_units(float(completed_course_0.units)))

    def test_reassigned_course_not_on_unassigned_list(self):
        visible_unassigned = self.degree_check_page.unassigned_course_ccns()
        assert f'{completed_course_0.term_id}-{completed_course_0.ccn}' not in visible_unassigned


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseAssignedToCategory:

    def test_assign_course_to_cat_with_no_subcat_and_no_course(self):
        completed_course_1.note = f'Teena wuz here too {test.test_id}'
        self.degree_check_page.edit_unassigned_course(completed_course_1)
        self.degree_check_page.assign_completed_course(completed_course_1, cat_no_subs_no_courses)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(completed_course_1).split()[0],
                                 utils.formatted_units(float(completed_course_1.units)))
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(completed_course_1),
                                 completed_course_1.grade)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(completed_course_1),
                                 completed_course_1.note)
        assert f'{completed_course_1.term_id}-{completed_course_1.ccn}' not in self.degree_check_page.unassigned_course_ccns()

    def test_assign_course_to_cat_with_course_but_no_subcat(self):
        self.degree_check_page.assign_completed_course(completed_course_2, cat_with_courses_no_subs)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(completed_course_2).split()[0],
                                 utils.formatted_units(float(completed_course_2.units)))
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(completed_course_2),
                                 completed_course_2.grade)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(completed_course_2), '—')
        assert f'{completed_course_2.term_id}-{completed_course_2.ccn}' not in self.degree_check_page.unassigned_course_ccns()

    def test_cannot_assign_course_to_cat_with_subcat(self):
        self.degree_check_page.click_unassigned_course_select(completed_course_3)
        assert not self.degree_check_page.element(
            self.degree_check_page.assignment_reqt_option(cat_with_subs)).is_enabled()

    def test_assign_course_to_subcat_with_no_course(self):
        self.degree_check_page.hit_escape()
        self.degree_check_page.assign_completed_course(completed_course_3, sub_cat_no_courses)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(completed_course_3).split()[0],
                                 utils.formatted_units(float(completed_course_3.units)))
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(completed_course_3),
                                 completed_course_3.grade)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(completed_course_3), '—')
        assert f'{completed_course_3.term_id}-{completed_course_3.ccn}' not in self.degree_check_page.unassigned_course_ccns()

    def test_assign_course_to_subcat_with_course(self):
        self.degree_check_page.assign_completed_course(completed_course_4, sub_cat_with_courses)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(completed_course_4).split()[0],
                                 utils.formatted_units(float(completed_course_4.units)))
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(completed_course_4),
                                 completed_course_4.grade)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(completed_course_4), '—')
        assert f'{completed_course_4.term_id}-{completed_course_4.ccn}' not in self.degree_check_page.unassigned_course_ccns()


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseReassignedFromCategory:

    def test_move_from_category_to_sub_category(self):
        self.degree_check_page.reassign_course(completed_course_1, cat_no_subs_no_courses, sub_cat_no_courses)

    def test_move_from_sub_category_to_category(self):
        self.degree_check_page.reassign_course(completed_course_1, sub_cat_no_courses, cat_no_subs_no_courses)

    def test_move_from_category_to_course_reqt(self):
        self.degree_check_page.reassign_course(completed_course_1, cat_no_subs_no_courses, course_reqt_1)

    def test_move_from_course_reqt_to_sub_category(self):
        self.degree_check_page.reassign_course(completed_course_1, course_reqt_1, sub_cat_no_courses)

    def test_move_from_sub_category_to_course_reqt(self):
        self.degree_check_page.reassign_course(completed_course_1, sub_cat_no_courses, course_reqt_1)

    def test_move_from_course_reqt_to_category(self):
        self.degree_check_page.reassign_course(completed_course_1, course_reqt_1, cat_no_subs_no_courses)


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseUnassignedFromCategory:

    def test_un_assign_from_category(self):
        self.degree_check_page.unassign_course(completed_course_1, cat_no_subs_no_courses)

    def test_unassigned_course_restored_to_unassigned_list(self):
        assert f'{completed_course_1.term_id}-{completed_course_1.ccn}' in self.degree_check_page.unassigned_course_ccns()


@pytest.mark.usefixtures('page_objects')
class TestDegreeCourseCopied:

    def test_copy_course_to_category(self):
        completed_course_4.units = str(float(completed_course_4.units) + 1)
        completed_course_4.note = 'Stop copying me'
        self.degree_check_page.hit_escape()
        self.degree_check_page.edit_assigned_course(completed_course_4)
        self.degree_check_page.copy_course(completed_course_4, cat_copy, cat_no_subs_no_courses)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(cat_copy).split()[0],
                                 utils.formatted_units(float(cat_copy.units)))
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(cat_copy), cat_copy.grade)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(cat_copy), '—')
        assert self.degree_check_page.is_assigned_course_copy_flagged(cat_copy)
        assert self.degree_check_page.is_present(self.degree_check_page.assigned_course_delete_button(cat_copy))

    def test_copy_course_to_sub_category(self):
        self.degree_check_page.copy_course(completed_course_4, sub_cat_copy, sub_cat_no_courses)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(sub_cat_copy).split()[0],
                                 utils.formatted_units(float(sub_cat_copy.units)))
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(sub_cat_copy), sub_cat_copy.grade)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(sub_cat_copy), '—')
        assert self.degree_check_page.is_assigned_course_copy_flagged(sub_cat_copy)
        assert self.degree_check_page.is_present(self.degree_check_page.assigned_course_delete_button(sub_cat_copy))

    def test_edit_course_copy_but_cancel(self):
        self.degree_check_page.click_edit_assigned_course(sub_cat_copy)
        self.degree_check_page.click_cancel_course_edit()

    def test_course_copy_add_note(self):
        sub_cat_copy.note = 'Note for a copied sub-cat'
        self.degree_check_page.edit_assigned_course(sub_cat_copy)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(sub_cat_copy), sub_cat_copy.note)

    def test_course_copy_edit_note(self):
        sub_cat_copy.note = f'EDITED - {sub_cat_copy.note}'
        self.degree_check_page.edit_assigned_course(sub_cat_copy)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(sub_cat_copy), sub_cat_copy.note)

    def test_course_copy_remove_note(self):
        sub_cat_copy.note = ''
        self.degree_check_page.edit_assigned_course(sub_cat_copy)
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(sub_cat_copy), '—')

    def test_course_copy_edit_units(self):
        sub_cat_copy.units = '9'
        self.degree_check_page.edit_assigned_course(sub_cat_copy)
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(sub_cat_copy).split()[0],
                                 utils.formatted_units(float(sub_cat_copy.units)))

    def test_course_copy_delete_but_cancel(self):
        self.degree_check_page.click_delete_assigned_course(sub_cat_copy)
        self.degree_check_page.cancel_delete_or_discard()

    def test_delete_course_copy(self):
        self.degree_check_page.delete_assigned_course(sub_cat_copy)
        utils.assert_equivalence(self.degree_check_page.assigned_course_name(completed_course_4), completed_course_4.name)

    def test_copy_persists_when_original_unassigned(self):
        self.degree_check_page.unassign_course(completed_course_4, sub_cat_with_courses)
        assert self.degree_check_page.is_present(self.degree_check_page.assigned_course_row(cat_copy))
