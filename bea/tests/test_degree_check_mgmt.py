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
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.models.degree_progress.degree_check import DegreeCheck
from bea.models.degree_progress.degree_check_batch import DegreeCheckBatch
from bea.models.degree_progress.degree_check_perms import DegreeCheckPerms
from bea.models.degree_progress.degree_reqt_units import DegreeReqtUnits
from bea.models.department import Department
from bea.test_utils import boa_degree_progress_utils
from bea.test_utils import boa_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest

test = BEATestConfig()
test.degree_check()
app.logger.info(f'Read/write advisor is UID {test.advisor.uid}; read-only advisor is UID {test.advisor_read_only.uid}')

template = next(filter(lambda t: 'Course Workflows' in t.name, test.degree_templates))
random.shuffle(test.students)
student = test.test_students[0]
nessie_utils.set_student_term_enrollments([student])
batch_students = test.test_students[1:10]
cohorts = []
groups = []
group_members = test.test_students[11:20]
group_1 = Cohort({'name': f'Group 1 {test.test_id}'})
group_2 = Cohort({'name': f'Group 2 {test.test_id}'})

batch_degree_1 = DegreeCheckBatch(template)
degree_check = DegreeCheck({}, template, student)
note_str = f'Teena wuz here {test.test_id} ' * 10


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_advisor_setup(self):
        self.homepage.dev_auth()
        self.pax_manifest_page.load_page()
        if test.advisor.degree_progress_perm != DegreeCheckPerms.WRITE:
            self.pax_manifest_page.set_deg_prog_perm(test.advisor, Department.COE, DegreeCheckPerms.WRITE)
        if test.advisor_read_only.degree_progress_perm != DegreeCheckPerms.READ:
            self.pax_manifest_page.set_deg_prog_perm(test.advisor_read_only, Department.COE, DegreeCheckPerms.READ)
        self.pax_manifest_page.log_out()

    def test_degree_template_setup(self):
        self.homepage.dev_auth(test.advisor)
        self.homepage.click_degree_checks()
        self.degree_template_mgmt_page.create_new_degree(template)
        self.degree_template_page.complete_template(template)


@pytest.mark.usefixtures('page_objects')
class TestDegreeCheckCreation:

    def test_offers_list_of_existing_templates(self):
        self.degree_check_create_page.load_page(student)
        self.degree_check_create_page.select_template(template)

    def test_can_be_canceled(self):
        self.degree_check_create_page.click_cancel_degree()
        self.student_page.when_present(self.student_page.TOGGLE_PERSONAL_DETAILS, utils.get_short_timeout())

    def test_can_be_created(self):
        self.degree_check_create_page.load_page(student)
        self.degree_check_create_page.create_new_degree_check(degree_check)

    def test_copies_template_unit_reqts(self):
        for u_req in degree_check.unit_reqts:
            utils.assert_actual_includes_expected(self.degree_check_page.visible_unit_reqt_name(u_req), u_req.name)
            utils.assert_equivalence(self.degree_check_page.visible_unit_reqt_num(u_req), u_req.unit_count)

    def test_copies_template_categories_and_courses(self):
        for cat in degree_check.categories:
            utils.assert_equivalence(self.degree_check_page.visible_cat_name(cat), cat.name)
            if cat.desc:
                utils.assert_equivalence(self.degree_check_page.visible_cat_desc(cat), cat.desc)
            for sub_cat in cat.sub_categories:
                utils.assert_equivalence(self.degree_check_page.visible_cat_name(sub_cat), sub_cat.name)
                utils.assert_equivalence(self.degree_check_page.visible_cat_desc(sub_cat), sub_cat.desc)
                for sub_course in sub_cat.course_reqts:
                    utils.assert_equivalence(self.degree_check_page.visible_course_reqt_name(sub_course),
                                             sub_course.name)
                    sub_units = sub_course.units if float(sub_course.units) else '—'
                    utils.assert_equivalence(self.degree_check_page.visible_course_reqt_units(sub_course), sub_units)
            for course in cat.course_reqts:
                utils.assert_equivalence(self.degree_check_page.visible_course_reqt_name(course), course.name)
                units = course.units if float(course.units) else '—'
                utils.assert_equivalence(self.degree_check_page.visible_course_reqt_units(course), units)


@pytest.mark.usefixtures
class TestCourseEditing:
    cat = next(filter(lambda cat: cat.course_reqts, degree_check.categories))
    reqt = cat.course_reqts[0]
    unassigned_courses = student.enrollment_data.degree_progress_courses(degree_check)
    completed_course_0 = unassigned_courses[0]

    def test_course_reqt_add_big_dot(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.toggle_course_reqt_dot()
        self.degree_check_page.click_save_reqt_edit()
        self.degree_check_page.when_present(self.degree_check_page.is_recommended_loc(self.reqt),
                                            utils.get_short_timeout())

    def test_course_reqt_remove_big_dot(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.toggle_course_reqt_dot()
        self.degree_check_page.click_save_reqt_edit()
        self.degree_check_page.when_not_present(self.degree_check_page.is_recommended_loc(self.reqt),
                                                utils.get_short_timeout())

    def test_course_reqt_add_units_range(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.enter_col_reqt_units('4.5')
        self.degree_check_page.click_save_reqt_edit()
        utils.assert_equivalence(self.degree_check_page.visible_course_reqt_units(self.reqt), '4.5')

    def test_course_reqt_remove_units(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.enter_col_reqt_units('')
        self.degree_check_page.click_save_reqt_edit()
        utils.assert_equivalence(self.degree_check_page.visible_course_reqt_units(self.reqt), '—')

    def test_course_reqt_add_grade(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.enter_reqt_grade('>B')
        self.degree_check_page.click_save_reqt_edit()
        utils.assert_equivalence(self.degree_check_page.visible_course_reqt_grade(self.reqt), '>B')

    def test_course_reqt_remove_grade(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.enter_reqt_grade('')
        self.degree_check_page.click_save_reqt_edit()
        assert not self.degree_check_page.visible_course_reqt_grade(self.reqt)

    def test_course_reqt_add_note(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.enter_recommended_note('a notable note')
        self.degree_check_page.click_save_reqt_edit()
        utils.assert_equivalence(self.degree_check_page.visible_course_reqt_note(self.reqt),
                                 'a notable note')

    def test_course_reqt_remove_note(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.enter_recommended_note('')
        self.degree_check_page.click_save_reqt_edit()
        assert not self.degree_check_page.visible_course_reqt_note(self.reqt)

    def test_course_reqt_add_color(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.select_color_option('red')
        self.degree_check_page.click_save_reqt_edit()

    def test_completed_course_assigned(self):
        self.degree_check_page.click_edit_course_reqt(self.reqt)
        self.degree_check_page.toggle_course_reqt_dot()
        self.degree_check_page.enter_col_reqt_units('4.5')
        self.degree_check_page.enter_reqt_grade('>B')
        self.degree_check_page.enter_recommended_note('a notable note')
        self.degree_check_page.click_save_reqt_edit()
        self.degree_check_page.assign_completed_course(self.completed_course_0, self.reqt)

    def test_overwrites_big_dot(self):
        self.degree_check_page.when_not_present(self.degree_check_page.is_recommended_loc(self.reqt),
                                                utils.get_short_timeout())

    def test_overwrites_reqt_units(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_units(self.completed_course_0),
                                 utils.formatted_units(float(self.completed_course_0.units)))

    def test_overwrites_reqt_grade(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_grade(self.completed_course_0),
                                 self.completed_course_0.grade)

    def test_overwrites_reqt_note(self):
        utils.assert_equivalence(self.degree_check_page.assigned_course_note(self.completed_course_0), '—')

    def test_completed_course_un_assigned(self):
        self.degree_check_page.unassign_course(self.completed_course_0, self.reqt)

    def test_restores_big_dot(self):
        self.degree_check_page.when_present(self.degree_check_page.is_recommended_loc(self.reqt),
                                            utils.get_short_timeout())

    def test_restores_reqt_units(self):
        utils.assert_equivalence(self.degree_check_page.visible_course_reqt_units(self.reqt), '4.5')

    def test_restores_reqt_grade(self):
        utils.assert_equivalence(self.degree_check_page.visible_course_reqt_grade(self.reqt), '>B')

    def test_restores_reqt_note(self):
        utils.assert_equivalence(self.degree_check_page.visible_course_reqt_note(self.reqt),
                                 'a notable note')

    def test_selected(self):
        self.degree_check_page.click_campus_reqt_cbx('American History')
        assert self.degree_check_page.is_campus_reqt_satisfied('American History')

    def test_deselected(self):
        self.degree_check_page.click_campus_reqt_cbx('American History')
        assert not self.degree_check_page.is_campus_reqt_satisfied('American History')

    def test_add_note(self):
        self.degree_check_page.enter_campus_reqt_note('American History', f'{test.test_id} note')


@pytest.mark.usefixtures('page_objects')
class TestDegreeCheckHeader:
    new_reqt = DegreeReqtUnits({'name': f'Another Unit Reqt {test.test_id}', 'unit_count': '12'})

    def test_edit_parent_template(self):
        self.degree_check_page.click_degree_checks()
        self.degree_template_mgmt_page.click_degree_link(template)
        self.degree_template_page.create_unit_reqt(self.new_reqt, template)

    def test_updated_template_message_on_degree_check(self):
        self.degree_check_page.load_page(degree_check)
        self.degree_check_page.when_present(self.degree_check_page.TEMPLATE_UPDATED_MSG, utils.get_short_timeout())

    def test_link_to_parent_template(self):
        assert self.degree_check_page.is_external_link_valid(self.degree_check_page.TEMPLATE_LINK,
                                                             f'{template.name} | BOA')

    def test_updated_template_message_on_degree_history(self):
        self.degree_check_page.click_view_degree_history()
        self.degree_check_page.when_present(self.degree_check_history_page.template_updated_alert_loc(degree_check),
                                            utils.get_short_timeout())

    def test_student_page_link(self):
        self.student_page.load_page(student)
        self.student_page.click_degree_checks_button()

    def test_add_degree_note_but_cancel(self):
        self.degree_check_page.load_page(degree_check)
        self.degree_check_page.click_create_degree_note()
        self.degree_check_page.click_cancel_note()

    def test_create_degree_note(self):
        self.degree_check_page.create_note(note_str)
        utils.assert_equivalence(self.degree_check_page.visible_note_body(), note_str.strip())
        utils.assert_matching_advisor_name(self.degree_check_page.visible_note_update_advisor(), test.advisor)
        utils.assert_actual_includes_expected(
            self.degree_check_page.element(self.degree_check_page.NOTE_UPDATE_DATE).text,
            'today')

    def test_edit_degree_note_but_cancel(self):
        self.degree_check_page.click_edit_degree_note()
        self.degree_check_page.click_cancel_note()

    def test_edit_degree_note(self):
        self.degree_check_page.edit_note(f'EDITED - {note_str}')
        utils.assert_equivalence(self.degree_check_page.visible_note_body(), f'EDITED - {note_str}'.strip())
        utils.assert_matching_advisor_name(self.degree_check_page.visible_note_update_advisor(), test.advisor)
        utils.assert_actual_includes_expected(
            self.degree_check_page.element(self.degree_check_page.NOTE_UPDATE_DATE).text,
            'today')

    def test_print_including_note(self):
        self.degree_check_page.load_page(degree_check)
        assert self.degree_check_page.is_print_note_selected()

    def test_print_excluding_note(self):
        self.degree_check_page.click_print_note_toggle()
        assert not self.degree_check_page.is_print_note_selected()

    def test_create_newer_degree_check(self):
        self.degree_check_page.click_create_new_degree()
        self.degree_check_create_page.when_present(self.degree_check_create_page.DEGREE_TEMPLATE_SELECT,
                                                   utils.get_short_timeout())

    def test_degree_history(self):
        self.degree_check_page.load_page(degree_check)
        self.degree_check_page.click_view_degree_history()
        degrees = boa_degree_progress_utils.get_student_degrees(student)
        expected_names = [d.name for d in degrees]
        expected_names.sort()
        visible_names = self.degree_check_history_page.visible_degree_names()
        visible_names.sort()
        utils.assert_equivalence(visible_names, expected_names)

    def test_degree_history_create_newer_degree_check(self):
        assert self.degree_check_history_page.is_present(self.degree_check_history_page.CREATE_NEW_DEGREE_LINK)


@pytest.mark.usefixtures('page_objects')
class TestReadOnlyAdvisor:

    def test_views_all_degree_templates(self):
        templates = boa_degree_progress_utils.get_degree_templates()
        templates.sort(key=lambda t: t.name)
        names = [t.name for t in templates]
        names.sort()
        dates = [t.created_date.strftime('%b %-d, %Y') for t in templates]
        dates.sort()
        self.homepage.switch_user(test.advisor_read_only)
        self.homepage.click_degree_checks()
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.TEMPLATE_LINK,
                                                    utils.get_short_timeout())
        visible_names = self.degree_template_mgmt_page.visible_template_names()
        visible_names.sort()
        visible_dates = self.degree_template_mgmt_page.visible_template_create_dates()
        visible_dates.sort()
        utils.assert_equivalence(visible_names, names)
        utils.assert_equivalence(visible_dates, dates)

    def test_can_view_degree_template(self):
        self.degree_template_mgmt_page.click_degree_link(template)
        self.degree_template_page.when_present(self.degree_template_page.template_heading(template),
                                               utils.get_short_timeout())

    def test_cannot_edit_degree_template(self):
        assert not self.degree_template_page.is_present(self.degree_template_page.UNIT_REQT_ADD_BUTTON)
        assert not self.degree_template_page.is_present(self.degree_template_page.add_col_reqt_button(1))
        assert not self.degree_template_page.elements(self.degree_template_page.CAT_EDIT_BUTTON)
        assert not self.degree_template_page.elements(self.degree_template_page.CAT_DELETE_BUTTON)

    def test_can_view_degree_check(self):
        self.student_page.load_page(student)
        self.student_page.click_degree_checks_button()
        self.degree_check_page.when_present(self.degree_check_page.degree_check_heading(degree_check),
                                            utils.get_short_timeout())

    def test_cannot_edit_degree_check(self):
        assert not self.degree_check_page.is_present(self.degree_check_page.CREATE_NOTE_BUTTON)
        assert not self.degree_check_page.is_present(self.degree_check_page.CREATE_NEW_DEGREE_LINK)
        assert not self.degree_check_page.elements(self.degree_check_page.ASSIGN_COURSE_BUTTON)
        assert not self.degree_check_page.elements(self.degree_check_page.CAT_EDIT_BUTTON)
        assert not self.degree_check_page.is_present(self.degree_check_page.campus_reqt_cbx('American History'))

    def test_can_view_degree_history(self):
        self.degree_check_page.click_view_degree_history()
        self.degree_check_history_page.wait_for_spinner()
        degrees = boa_degree_progress_utils.get_student_degrees(student)
        expected_names = [d.name for d in degrees]
        expected_names.sort()
        visible_names = self.degree_check_history_page.visible_degree_names()
        visible_names.sort()
        utils.assert_equivalence(visible_names, expected_names)

    def test_sees_no_create_degree_button(self):
        assert not self.degree_check_history_page.is_present(self.degree_check_history_page.CREATE_NEW_DEGREE_LINK)


@pytest.mark.usefixtures('page_objects')
class TestDegreeCheckBatch:

    def test_delete_existing_cohorts_and_groups(self):
        self.homepage.switch_user(test.advisor)
        advisor_cohorts = boa_utils.get_user_filtered_cohorts(test.advisor)
        for c in advisor_cohorts:
            self.filtered_students_page.load_cohort(c)
            self.filtered_students_page.delete_cohort(c)
        advisor_groups = boa_utils.get_user_curated_groups(test.advisor)
        for g in advisor_groups:
            self.curated_students_page.load_page(g)
            self.curated_students_page.delete_group(g)

    def test_no_cohorts_and_no_groups_on_batch(self):
        self.homepage.click_degree_checks()
        self.degree_template_mgmt_page.click_batch_degree_checks()
        self.degree_check_batch_page.when_present(self.degree_check_batch_page.STUDENT_INPUT, utils.get_short_timeout())
        assert not self.degree_check_batch_page.is_present(self.degree_check_batch_page.COHORT_SELECT)
        assert not self.degree_check_batch_page.is_present(self.degree_check_batch_page.GROUP_SELECT)
        assert not self.degree_check_batch_page.element(
            self.degree_check_batch_page.BATCH_DEGREE_SAVE_BUTTON).is_enabled()

    def test_start_batch_but_cancel(self):
        self.degree_check_batch_page.click_cancel_batch_degree_check()
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.BATCH_DEGREE_CHECK_LINK,
                                                    utils.get_short_timeout())

    def test_rename_template(self):
        self.homepage.click_degree_checks()
        self.degree_template_mgmt_page.click_rename_button(template)
        template.name = f'{template.name} - Edited'
        self.degree_template_mgmt_page.enter_new_name(template.name)
        self.degree_template_mgmt_page.click_save_new_name()
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.degree_check_link(template),
                                                    utils.get_short_timeout())

    def test_setup(self):
        self.homepage.load_page()
        self.filtered_students_page.search_and_create_new_student_cohort(test.default_cohort)
        cohorts.append(test.default_cohort)
        for curated in [group_1, group_2]:
            self.homepage.click_sidebar_create_student_group()
            self.curated_students_page.create_group_with_bulk_sids(curated, group_members)
            self.curated_students_page.wait_for_sidebar_group(curated)
            groups.append(curated)
        if student in batch_students:
            batch_students.remove(student)

    def test_add_bulk_sids(self):
        self.homepage.click_degree_checks()
        self.degree_template_mgmt_page.click_batch_degree_checks()
        self.degree_check_batch_page.add_sids_to_batch(batch_degree_1, batch_students)

    def test_add_cohorts(self):
        self.degree_check_batch_page.add_cohorts_to_batch(batch_degree_1, cohorts)

    def test_add_groups(self):
        self.degree_check_batch_page.add_groups_to_batch(batch_degree_1, groups)

    def test_remove_students(self):
        self.degree_check_batch_page.remove_students_from_batch(batch_degree_1, batch_students)

    def test_remove_cohorts(self):
        self.degree_check_batch_page.remove_cohorts_from_batch(batch_degree_1, cohorts)

    def test_remove_groups(self):
        self.degree_check_batch_page.remove_groups_from_batch(batch_degree_1, groups)

    def test_select_degree_tempalte(self):
        self.degree_check_batch_page.select_degree(template)

    def test_pending_degree_check_count(self):
        self.degree_check_batch_page.add_sids_to_batch(batch_degree_1, batch_students)
        self.degree_check_batch_page.add_cohorts_to_batch(batch_degree_1, cohorts)
        self.degree_check_batch_page.add_groups_to_batch(batch_degree_1, groups)
        expected_count = len(boa_utils.unique_students_in_batch(batch_students, cohorts, groups))
        utils.assert_actual_includes_expected(
            self.degree_check_batch_page.element(self.degree_check_batch_page.STUDENT_COUNT_MSG).text,
            str(expected_count))

    def test_save_batch(self):
        self.degree_check_batch_page.click_save_batch_degree_check()
        self.degree_template_mgmt_page.when_present(self.degree_template_mgmt_page.BATCH_SUCCESS_MSG,
                                                    utils.get_medium_timeout())
        students = boa_utils.unique_students_in_batch(batch_students, cohorts, groups)
        expected_msg = f'Success! Degree check {template.name} added to {len(students)} student profiles'
        utils.assert_actual_includes_expected(
            self.degree_template_mgmt_page.element(self.degree_template_mgmt_page.BATCH_SUCCESS_MSG).get_attribute(
                'innerText'),
            expected_msg,
        )

    def test_degree_check_per_student(self):
        batch_student = boa_utils.unique_students_in_batch(batch_students, cohorts, groups)[-1]
        batch_student_degree = DegreeCheck({}, template, batch_student)
        boa_degree_progress_utils.set_degree_check_ids(batch_student_degree)
        self.degree_check_page.load_page(batch_student_degree)
        for u_req in batch_student_degree.unit_reqts:
            utils.assert_actual_includes_expected(self.degree_check_page.visible_unit_reqt_name(u_req), u_req.name)
            utils.assert_equivalence(self.degree_check_page.visible_unit_reqt_num(u_req), u_req.unit_count)
        for cat in batch_student_degree.categories:
            utils.assert_equivalence(self.degree_check_page.visible_cat_name(cat), cat.name)
            if cat.desc:
                utils.assert_equivalence(self.degree_check_page.visible_cat_desc(cat), cat.desc)
            for sub_cat in cat.sub_categories:
                utils.assert_equivalence(self.degree_check_page.visible_cat_name(sub_cat), sub_cat.name)
                utils.assert_equivalence(self.degree_check_page.visible_cat_desc(sub_cat), sub_cat.desc)
                for sub_course in sub_cat.course_reqts:
                    utils.assert_equivalence(self.degree_check_page.visible_course_reqt_name(sub_course),
                                             sub_course.name)
                    sub_units = sub_course.units if float(sub_course.units) else '—'
                    utils.assert_equivalence(self.degree_check_page.visible_course_reqt_units(sub_course), sub_units)
            for course in cat.course_reqts:
                utils.assert_equivalence(self.degree_check_page.visible_course_reqt_name(course), course.name)
                units = course.units if float(course.units) else '—'
                utils.assert_equivalence(self.degree_check_page.visible_course_reqt_units(course), units)

    def test_batch_created(self):
        students = boa_utils.unique_students_in_batch(batch_students, cohorts, groups)
        expected_sids = [s.sid for s in students]
        expected_sids.sort()
        utils.assert_equivalence(boa_degree_progress_utils.get_degree_sids_by_degree_name(batch_degree_1.template.name),
                                 expected_sids)

    def test_no_dupe_degree_checks(self):
        batch_student = boa_utils.unique_students_in_batch(batch_students, cohorts, groups)[0]
        self.degree_check_page.click_degree_checks()
        self.degree_template_mgmt_page.click_batch_degree_checks()
        self.degree_check_batch_page.add_sids_to_batch(batch_degree_1, [batch_student])
        self.degree_check_batch_page.select_degree(batch_degree_1.template)
        self.degree_check_batch_page.when_present(self.degree_check_batch_page.DUPE_DEGREE_CHECK_MSG,
                                                  utils.get_short_timeout())
