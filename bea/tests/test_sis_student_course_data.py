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

from bea.config.bea_test_config import BEATestConfig
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.test_utils import utils
import pytest

test = BEATestConfig()
test.sis_student_data()
group = Cohort({'name': f'SIS Student Courses {test.test_id}'})
next_term_id = utils.get_next_term_sis_id()
prev_term_id = utils.get_prev_term_sis_id()
term_select_opt_ids = [
    utils.get_next_term_sis_id(next_term_id),
    next_term_id,
    prev_term_id,
    utils.get_prev_term_sis_id(prev_term_id),
]
current_term = utils.get_current_term()

course_tcs = [tc for tc in test.test_cases if tc.course]
term_select_tcs = [tc for tc in course_tcs if tc.student.enrollment_data.term_id(tc.term) in term_select_opt_ids]
current_term_tcs = [tc for tc in course_tcs if tc.student.enrollment_data.term_id(tc.term) == current_term.sis_id]


@pytest.mark.usefixtures('page_objects')
class TestCreateGroup:

    def test_login(self):
        self.homepage.dev_auth(test.advisor)

    def test_create_group(self):
        students = list(set([tc.student for tc in course_tcs]))
        self.homepage.click_sidebar_create_student_group()
        self.curated_students_page.create_group_with_bulk_sids(group, students)
        self.curated_students_page.wait_for_sidebar_group(group)
        self.curated_students_page.when_visible(self.curated_students_page.group_name_heading_loc(group),
                                                utils.get_medium_timeout())


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=current_term_tcs,
                         ids=[tc.test_case_id for tc in current_term_tcs],
                         scope='class')
class TestListViewCourseData:

    def test_load_group(self, tc):
        self.curated_students_page.when_present(self.curated_students_page.student_link_loc(tc.student),
                                                utils.get_short_timeout())

    def test_list_view_course_code(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_code = tc.student.enrollment_data.course_code(tc.course)
        visible_course_code = self.curated_students_page.course_code(tc.student, idx)
        utils.assert_equivalence(visible_course_code, course_code)

    def test_list_view_course_units(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_units = utils.formatted_units(tc.student.enrollment_data.course_units(tc.course))
        visible_course_units = self.curated_students_page.course_units(tc.student, idx)
        utils.assert_equivalence(visible_course_units, course_units)

    def test_list_view_midpoint_grade(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_midpoint_grade = tc.student.enrollment_data.midpoint_grade(tc.course)
        visible_midpoint_grade = self.curated_students_page.course_mid_grade(tc.student, idx)
        if course_midpoint_grade:
            utils.assert_equivalence(visible_midpoint_grade, course_midpoint_grade)
            if course_midpoint_grade in ['D+', 'D', 'D−', 'F', 'NP', 'RD', 'I']:
                assert self.curated_students_page.is_course_mid_flagged(tc.student, idx)
            else:
                assert not self.curated_students_page.is_course_mid_flagged(tc.student, idx)
        else:
            utils.assert_equivalence(visible_midpoint_grade, '—')

    def test_list_view_final_grade(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_final_grade = tc.student.enrollment_data.final_grade(tc.course)
        visible_final_grade = self.curated_students_page.course_final_grade(tc.student, idx)
        if course_final_grade:
            utils.assert_equivalence(visible_final_grade, course_final_grade)
            if course_final_grade in ['D+', 'D', 'D−', 'F', 'NP', 'RD', 'I']:
                assert self.curated_students_page.is_course_final_flagged(tc.student, idx)
            else:
                assert not self.curated_students_page.is_course_final_flagged(tc.student, idx)
        else:
            grading_basis = tc.student.enrollment_data.grading_basis(tc.course)
            if grading_basis == 'NON':
                utils.assert_actual_includes_expected(visible_final_grade, 'No data')
            else:
                utils.assert_equivalence(visible_final_grade, grading_basis)

    def test_list_view_last_activity(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        sites = tc.student.enrollment_data.course_sites(tc.course)
        visible_activity = self.curated_students_page.course_activity(tc.student, idx)
        if sites:
            for site in sites:
                msg = tc.student.enrollment_data.last_activity_day(site)
                utils.assert_actual_includes_expected(visible_activity, msg)
        else:
            utils.assert_equivalence(visible_activity, '—')


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=term_select_tcs,
                         ids=[tc.test_case_id for tc in term_select_tcs],
                         scope='class')
class TestListViewTermSelect:

    def test_select_term(self, tc):
        if not self.curated_students_page.selected_term_sis_id == tc.term_sis_id:
            self.curated_students_page.select_term(tc.term_sis_id)

    def test_list_view_course_code(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_code = tc.student.enrollment_data.course_code(tc.course)
        visible_course_code = self.curated_students_page.course_code(tc.student, idx)
        utils.assert_equivalence(visible_course_code, course_code)

    def test_list_view_course_units(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_units = utils.formatted_units(tc.student.enrollment_data.course_units(tc.course))
        visible_course_units = self.curated_students_page.course_units(tc.student, idx)
        utils.assert_equivalence(visible_course_units, course_units)

    def test_list_view_midpoint_grade(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_midpoint_grade = tc.student.enrollment_data.midpoint_grade(tc.course)
        visible_midpoint_grade = self.curated_students_page.course_mid_grade(tc.student, idx)
        if course_midpoint_grade:
            utils.assert_equivalence(visible_midpoint_grade, course_midpoint_grade)
            if course_midpoint_grade in ['D+', 'D', 'D−', 'F', 'NP', 'RD', 'I']:
                assert self.curated_students_page.is_course_mid_flagged(tc.student, idx)
            else:
                assert not self.curated_students_page.is_course_mid_flagged(tc.student, idx)
        else:
            utils.assert_equivalence(visible_midpoint_grade, '—')

    def test_list_view_final_grade(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_final_grade = tc.student.enrollment_data.final_grade(tc.course)
        visible_final_grade = self.curated_students_page.course_final_grade(tc.student, idx)
        if course_final_grade:
            utils.assert_equivalence(visible_final_grade, course_final_grade)
            if course_final_grade in ['D+', 'D', 'D−', 'F', 'NP', 'RD', 'I']:
                assert self.curated_students_page.is_course_final_flagged(tc.student, idx)
            else:
                assert not self.curated_students_page.is_course_final_flagged(tc.student, idx)
        else:
            grading_basis = tc.student.enrollment_data.grading_basis(tc.course)
            if grading_basis == 'NON':
                utils.assert_actual_includes_expected(visible_final_grade, 'No data')
            else:
                utils.assert_equivalence(visible_final_grade, grading_basis)

    def test_list_view_last_activity(self, tc):
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        sites = tc.student.enrollment_data.course_sites(tc.course)
        visible_activity = self.curated_students_page.course_activity(tc.student, idx)
        if sites:
            for site in sites:
                msg = tc.student.enrollment_data.last_activity_day(site)
                utils.assert_actual_includes_expected(visible_activity, msg)
        else:
            utils.assert_equivalence(visible_activity, '— ')


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=course_tcs,
                         ids=[tc.test_case_id for tc in course_tcs],
                         scope='class')
class TestStudentPageCourseData:

    def test_student_page_expand_terms(self, tc):
        if f'{tc.student.uid}' not in self.driver.current_url:
            self.student_page.load_page(tc.student)
        self.student_page.expand_all_years()
        self.student_page.wait_for_term_data(tc.student.enrollment_data.term_id(tc.term))

    def test_student_page_collapsed_course_code(self, tc):
        course_code = tc.student.enrollment_data.course_code(tc.course)
        visible_course_code = self.student_page.collapsed_course_code(tc.term_sis_id, tc.section_id)
        utils.assert_equivalence(visible_course_code, course_code)

    def test_student_page_collapsed_waitlist_flag(self, tc):
        is_waitlisted = tc.student.enrollment_data.is_course_waitlisted(tc.course)
        visible_wait_list = self.student_page.collapsed_course_wait_list_flag(tc.term_sis_id, tc.section_id)
        if is_waitlisted:
            utils.assert_equivalence(visible_wait_list, 'Waitlisted')
        else:
            utils.assert_equivalence(visible_wait_list, None)

    def test_student_page_collapsed_midpoint_grade(self, tc):
        course_midpoint_grade = tc.student.enrollment_data.midpoint_grade(tc.course)
        visible_midpoint_grade = self.student_page.collapsed_course_midterm_grade(tc.term_sis_id, tc.section_id)
        if course_midpoint_grade:
            utils.assert_equivalence(visible_midpoint_grade, course_midpoint_grade)
        else:
            utils.assert_equivalence(visible_midpoint_grade, '—')

    def test_student_page_collapsed_final_grade(self, tc):
        course_final_grade = tc.student.enrollment_data.final_grade(tc.course)
        visible_final_grade = self.student_page.collapsed_course_final_grade(tc.term_sis_id, tc.section_id)
        if course_final_grade:
            utils.assert_equivalence(visible_final_grade, course_final_grade)
            if course_final_grade in ['D+', 'D', 'D−', 'F', 'NP', 'RD', 'I']:
                assert self.student_page.is_collapsed_course_final_grade_alert(tc.term_sis_id, tc.section_id)
            else:
                assert not self.student_page.is_collapsed_course_final_grade_alert(tc.term_sis_id, tc.section_id)
        else:
            grading_basis = tc.student.enrollment_data.grading_basis(tc.course)
            if grading_basis == 'NON':
                utils.assert_equivalence(visible_final_grade, '—')
            else:
                utils.assert_equivalence(visible_final_grade, grading_basis)

    def test_student_page_collapsed_units(self, tc):
        units_completed = tc.student.enrollment_data.course_units_completed_float(tc.course)
        visible_units = self.student_page.collapsed_course_units(tc.term_sis_id, tc.section_id)
        utils.assert_equivalence(visible_units, units_completed)

    def test_student_page_expand_course(self, tc):
        self.student_page.expand_course_data(tc.term_sis_id, tc.section_id)

    def test_student_page_expanded_course_code(self, tc):
        course_code = tc.student.enrollment_data.course_code(tc.course)
        visible_course_code = self.student_page.expanded_course_code(tc.term_sis_id, tc.section_id)
        utils.assert_equivalence(visible_course_code, course_code)

    def test_student_page_expanded_course_title(self, tc):
        course_title = tc.student.enrollment_data.course_title(tc.course)
        visible_course_title = self.student_page.expanded_course_title(tc.term_sis_id, tc.section_id)
        utils.assert_equivalence(visible_course_title, course_title)

    def test_student_page_expanded_incomplete_alert(self, tc):
        alert = self.student_page.expanded_course_incomplete_alert(tc.term_sis_id, tc.section_id)
        primary_section = tc.student.enrollment_data.course_primary_section(tc.course)
        primary_data = tc.student.enrollment_data.sis_section_data(primary_section)
        incomplete_code = primary_data['incomplete_code']
        if incomplete_code:
            grade = tc.student.enrollment_data.incomplete_grade_outcome(tc.student.enrollment_data.grading_basis(tc.course))
            lapse_date = primary_data['incomplete_lapse_date']
            lapse_date = lapse_date and datetime.strptime(lapse_date, '%Y-%m-%d %H:%M:%S').strftime('%b %-d, %Y')
            if primary_data['incomplete_frozen'] == 'Y':
                expected = f'Frozen incomplete grade will not lapse into {grade}'
                assert expected in alert
            elif primary_data['incomplete_frozen'] == 'N':
                if incomplete_code == 'I':
                    expected = f'Incomplete grade scheduled to become {grade} on {lapse_date}'
                    assert expected in alert
                elif incomplete_code == 'L':
                    expected = f'Formerly an incomplete grade on {lapse_date}'
                    assert expected in alert
                elif incomplete_code == 'R':
                    expected = 'Formerly an incomplete grade'
                    assert expected in alert

    def test_student_page_expanded_course_reqts(self, tc):
        course_reqts = tc.student.enrollment_data.course_reqts(tc.course)
        visible_course_reqts = self.student_page.expanded_course_reqts(tc.term_sis_id, tc.section_id)
        if course_reqts:
            utils.assert_equivalence(visible_course_reqts, course_reqts)
        else:
            utils.assert_equivalence(visible_course_reqts, [])

    def test_student_page_expanded_course_sections(self, tc):
        sections = tc.student.enrollment_data.section_components_and_numbers(tc.course)
        visible_sections = self.student_page.expanded_course_sections(tc.term_sis_id, tc.section_id)
        for section in sections:
            utils.assert_actual_includes_expected(visible_sections, section)

    # TODO - course sites
