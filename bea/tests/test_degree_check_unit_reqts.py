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
import random

from bea.config.bea_test_config import BEATestConfig
from bea.models.degree_progress.degree_check import DegreeCheck
from bea.models.degree_progress.degree_check_perms import DegreeCheckPerms
from bea.test_utils import boa_degree_progress_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
import pytest

test = BEATestConfig()
test.degree_check(opts={'enrolled': True})
template = next(filter(lambda t: 'Unit Fulfillment' in t.name, test.degree_templates))

random.shuffle(test.default_cohort.members)
student = test.default_cohort.members[0]
degree_check = DegreeCheck({}, template, student)
nessie_utils.set_student_term_enrollments([student])
unassigned_courses = student.enrollment_data.degree_progress_courses(degree_check)
course = unassigned_courses[0]
course_copy_0 = course.generate_course_copy()
course_copy_1 = course.generate_course_copy()

cat_0 = degree_check.categories[0]
cat_1 = degree_check.categories[1]
cat_2 = degree_check.categories[2]
cat_3 = degree_check.categories[3]
sub_cat_1 = cat_1.sub_categories[0]
sub_cat_3 = cat_3.sub_categories[0]
req_course_1 = sub_cat_1.course_reqts[0]


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
class TestUnassignedCourse:

    def test_no_unit_reqts_editing(self):
        self.degree_check_page.click_edit_unassigned_course(course)
        self.degree_check_page.when_present(self.degree_check_page.COURSE_NOTE_INPUT, 1)
        assert not self.degree_check_page.is_present(self.degree_check_page.COL_REQT_COURSE_UNITS_REQT_SELECT)


@pytest.mark.usefixtures('page_objects')
class TestCourseAssignedToCatWithUnits:

    def test_assign_completed_course(self):
        boa_degree_progress_utils.set_degree_sis_course_id(degree_check, course)
        self.degree_check_page.click_cancel_course_edit()
        self.degree_check_page.assign_completed_course(course, cat_0)

    def test_inherit_category_unit_fulfillment(self):
        self.degree_check_page.verify_assigned_course_fulfillment(course)

    def test_no_unit_fulfillment_override_flag(self):
        assert not self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_updates_unit_fulfillment_totals(self):
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course)

    def test_updates_unit_fulfillment_details(self):
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[0], course),
                                 utils.formatted_units(float(course.units)))

    def test_unit_fulfillment_edit_updates_totals(self):
        course.unit_reqts = [degree_check.unit_reqts[2]]
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[2], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[2], course),
                                 utils.formatted_units(float(course.units)))
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[0], course)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[0], course)

    def test_unit_fulfillment_override_flag(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_add_unit_fulfillment(self):
        course.unit_reqts = degree_check.unit_reqts
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course)
        assert not self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[2], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[0], course),
                                 utils.formatted_units(float(course.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course),
                                 utils.formatted_units(float(course.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[2], course),
                                 utils.formatted_units(float(course.units)))

    def test_added_units_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_remove_unit_fulfillment(self):
        course.unit_reqts = [degree_check.unit_reqts[1]]
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[0], course)
        assert not self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[1], course)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[2], course)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[0], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course),
                                 utils.formatted_units(float(course.units)))
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[2], course)

    def test_removed_units_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)


@pytest.mark.usefixtures('page_objects')
class TestCourseUnassignedFromCat:

    def test_unassign_course(self):
        self.degree_check_page.unassign_course(course, cat_0)

    def test_updates_unit_fulfillment_totals(self):
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[1], course)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[1], course)


@pytest.mark.usefixtures('page_objects')
class TestCourseAssignedToSubCatWithUnits:

    def test_assign_course(self):
        self.degree_check_page.assign_completed_course(course, sub_cat_1)

    def test_shows_sub_cat_parent_fulfillment(self):
        self.degree_check_page.verify_assigned_course_fulfillment(course)

    def test_no_fulfill_override_flag(self):
        assert not self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_updates_unit_fulfillment_totals(self):
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course),
                                 utils.formatted_units(float(course.units)))

    def test_unit_fulfillment_removal_updates_totals(self):
        course.unit_reqts = []
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[1], course)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[1], course)

    def test_unit_fulfillment_removal_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_add_unit_fulfillment(self):
        course.unit_reqts = degree_check.unit_reqts
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[2], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[0], course),
                                 utils.formatted_units(float(course.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course),
                                 utils.formatted_units(float(course.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[2], course),
                                 utils.formatted_units(float(course.units)))

    def test_added_units_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_edit_unit_fulfillment(self):
        course.unit_reqts = [degree_check.unit_reqts[2]]
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[0], course)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[1], course)
        assert not self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[2], course)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[0], course)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[1], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[2], course),
                                 utils.formatted_units(float(course.units)))

    def test_edit_units_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)


@pytest.mark.usefixtures('page_objects')
class TestCourseReassignedToCourseWithUnits:

    def test_reassign_course(self):
        self.degree_check_page.reassign_course(course, sub_cat_1, req_course_1)

    def test_shows_course_reqt_unit_fulfillment(self):
        self.degree_check_page.verify_assigned_course_fulfillment(course)

    def test_no_unit_fulfillment_override_flag(self):
        assert not self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_updates_unit_fulfillment_totals(self):
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[2], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course),
                                 utils.formatted_units(float(course.units)))
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[2], course)

    def test_edit_unit_fulfillment(self):
        course.unit_reqts = [degree_check.unit_reqts[0]]
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[1], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[0], course),
                                 utils.formatted_units(float(course.units)))
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[1], course)

    def test_edit_units_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_remove_unit_fulfillment(self):
        course.unit_reqts = []
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[0], course)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[0], course)

    def test_removed_units_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)

    def test_add_unit_fulfillment(self):
        course.unit_reqts = degree_check.unit_reqts
        self.degree_check_page.edit_assigned_course(course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[2], course)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[0], course),
                                 utils.formatted_units(float(course.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course),
                                 utils.formatted_units(float(course.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[2], course),
                                 utils.formatted_units(float(course.units)))

    def test_added_units_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course)


@pytest.mark.usefixtures('page_objects')
class TestCourseCopyWithUnitsAssignedToCatSansUnits:

    def test_copy_course(self):
        self.degree_check_page.copy_course(course, course_copy_0, cat_2)
        boa_degree_progress_utils.set_degree_sis_course_copy_id(degree_check, course_copy_0)

    def test_shows_category_unit_fulfillment(self):
        self.degree_check_page.verify_assigned_course_fulfillment(course_copy_0)

    def test_no_unit_fulfillment_override_flag(self):
        assert not self.degree_check_page.is_assigned_course_fulfill_flagged(course_copy_0)

    def test_not_included_in_unit_fulfillment_totals(self):
        assert not self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course_copy_0)
        assert not self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course_copy_0)
        assert not self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[2], course_copy_0)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[0], course_copy_0)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[1], course_copy_0)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[2], course_copy_0)

    def test_unit_fulfillment_edit_updates_totals(self):
        course_copy_0.unit_reqts = [degree_check.unit_reqts[2]]
        self.degree_check_page.edit_assigned_course(course_copy_0)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[2], course_copy_0)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[2], course_copy_0),
                                 utils.formatted_units(float(course_copy_0.units)))

    def test_unit_fulfillment_override_flag(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course_copy_0)

    def test_unit_fulfillment_adding_updates_totals(self):
        course_copy_0.unit_reqts = degree_check.unit_reqts
        self.degree_check_page.edit_assigned_course(course_copy_0)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course_copy_0)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course_copy_0)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[0], course_copy_0),
                                 utils.formatted_units(float(course_copy_0.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course_copy_0),
                                 utils.formatted_units(float(course_copy_0.units)))

    def test_unit_fulfillment_addition_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course_copy_0)

    def test_unit_fulfillment_removal_updates_totals(self):
        course_copy_0.unit_reqts = []
        self.degree_check_page.edit_assigned_course(course_copy_0)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[0], course_copy_0)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[1], course_copy_0)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[2], course_copy_0)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[0], course_copy_0)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[1], course_copy_0)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[2], course_copy_0)

    def test_unit_fulfillment_removal_not_flagged(self):
        assert not self.degree_check_page.is_assigned_course_fulfill_flagged(course_copy_0)


@pytest.mark.usefixtures('page_objects')
class TestCourseCopyWithUnitsAssignedToSubCatSansUnits:

    def test_copy_course(self):
        self.degree_check_page.copy_course(course, course_copy_1, sub_cat_3)
        boa_degree_progress_utils.set_degree_sis_course_copy_id(degree_check, course_copy_1)

    def test_shows_sub_category_unit_fulfillment(self):
        self.degree_check_page.verify_assigned_course_fulfillment(course_copy_1)

    def test_shows_no_unit_fulfillment_override(self):
        assert not self.degree_check_page.is_assigned_course_fulfill_flagged(course_copy_1)

    def test_updates_unit_fulfillment_totals(self):
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course_copy_1)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course_copy_1),
                                 utils.formatted_units(float(course_copy_1.units)))

    def test_unit_fulfillment_edits_update_totals(self):
        course_copy_1.unit_reqts = [degree_check.unit_reqts[0]]
        self.degree_check_page.edit_assigned_course(course_copy_1)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course_copy_0)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[1], course_copy_0)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[0], course_copy_1),
                                 utils.formatted_units(float(course_copy_1.units)))
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[1], course_copy_1)

    def test_unit_fulfillment_edits_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course_copy_1)

    def test_unit_fulfillment_removal_updates_totals(self):
        course_copy_1.unit_reqts = []
        self.degree_check_page.edit_assigned_course(course_copy_1)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[0], course_copy_1)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[0], course_copy_1)

    def test_unit_fulfillment_removal_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course_copy_1)

    def test_unit_fulfillment_addition_updates_totals(self):
        course_copy_1.unit_reqts = degree_check.unit_reqts
        self.degree_check_page.edit_assigned_course(course_copy_1)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[0], course_copy_1)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[1], course_copy_1)
        assert self.degree_check_page.are_units_added_to_unit_reqt(degree_check.unit_reqts[2], course_copy_1)
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[0], course_copy_1),
                                 utils.formatted_units(float(course_copy_1.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[1], course_copy_1),
                                 utils.formatted_units(float(course_copy_1.units)))
        utils.assert_equivalence(self.degree_check_page.unit_reqt_course_units(degree_check.unit_reqts[2], course_copy_1),
                                 utils.formatted_units(float(course_copy_1.units)))

    def test_unit_fulfillment_addition_flagged(self):
        assert self.degree_check_page.is_assigned_course_fulfill_flagged(course_copy_1)

    def test_course_copy_deleted(self):
        self.degree_check_page.delete_assigned_course(course_copy_1)

    def test_course_deletion_updates_unit_fulfillment_totals(self):
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[0], course_copy_1)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[1], course_copy_1)
        assert self.degree_check_page.are_units_removed_from_unit_reqt(degree_check.unit_reqts[2], course_copy_1)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[0], course_copy_1)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[1], course_copy_1)
        assert not self.degree_check_page.is_unit_reqt_course_present(degree_check.unit_reqts[2], course_copy_1)
