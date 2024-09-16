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

from bea.config.bea_test_config import BEATestConfig
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.test_utils import utils
import pytest

test = BEATestConfig()
test.sis_student_data()
group = Cohort({'name': f'SIS Student Terms {test.test_id}'})
next_term_id = utils.get_next_term_sis_id()
prev_term_id = utils.get_prev_term_sis_id()
term_select_opt_ids = [
    utils.get_next_term_sis_id(next_term_id),
    next_term_id,
    prev_term_id,
    utils.get_prev_term_sis_id(prev_term_id),
]
current_term = utils.get_current_term()

term_tcs = [tc for tc in test.test_cases if tc.term and not tc.course]
term_select_tcs = [tc for tc in term_tcs if tc.student.enrollment_data.term_id(tc.term) in term_select_opt_ids]
current_term_tcs = [tc for tc in term_tcs if tc.student.enrollment_data.term_id(tc.term) == current_term.sis_id]


@pytest.mark.usefixtures('page_objects')
class TestCreateGroup:

    def test_login(self):
        self.homepage.dev_auth(test.advisor)

    def test_create_group(self):
        students = list(set([tc.student for tc in term_tcs]))
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
class TestListViewTermData:

    def test_load_group(self, tc):
        self.curated_students_page.when_present(self.curated_students_page.student_link_loc(tc.student),
                                                utils.get_short_timeout())

    def test_list_view_term_units(self, tc):
        term_units = tc.student.enrollment_data.term_units(tc.term)
        visible_term_units = self.curated_students_page.term_units(tc.student)
        if term_units:
            utils.assert_equivalence(visible_term_units, term_units)
        else:
            utils.assert_equivalence(visible_term_units, '0')

    def test_list_view_term_max_units(self, tc):
        term_units_max = tc.student.enrollment_data.term_units_max(tc.term)
        term_units_max_float = tc.student.enrollment_data.term_units_max_float(tc.term)
        visible_max_units = self.curated_students_page.term_units_max(tc.student)
        if term_units_max and term_units_max_float != '20.5':
            utils.assert_equivalence(visible_max_units, term_units_max)
        else:
            utils.assert_equivalence(visible_max_units, None)

    def test_list_view_term_min_units(self, tc):
        term_units_min = tc.student.enrollment_data.term_units_min(tc.term)
        term_units_min_float = tc.student.enrollment_data.term_units_min_float(tc.term)
        visible_min_units = self.curated_students_page.term_units_min(tc.student)
        if term_units_min and term_units_min_float != '0.5':
            utils.assert_equivalence(visible_min_units, term_units_min)
        else:
            utils.assert_equivalence(visible_min_units, None)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=term_select_tcs,
                         ids=[tc.test_case_id for tc in term_select_tcs],
                         scope='class')
class TestListViewTermSelect:

    def test_select_term(self, tc):
        term_sis_id = tc.student.enrollment_data.term_id(tc.term)
        self.curated_students_page.select_term(term_sis_id)

    def test_list_view_term_units(self, tc):
        term_units = tc.student.enrollment_data.term_units(tc.term)
        visible_term_units = self.curated_students_page.term_units(tc.student)
        if term_units:
            utils.assert_equivalence(visible_term_units, term_units)
        else:
            utils.assert_equivalence(visible_term_units, '0')

    def test_list_view_term_max_units(self, tc):
        term_units_max = tc.student.enrollment_data.term_units_max(tc.term)
        term_units_max_float = tc.student.enrollment_data.term_units_max_float(tc.term)
        visible_max_units = self.curated_students_page.term_units_max(tc.student)
        if term_units_max and term_units_max_float != '20.5':
            utils.assert_equivalence(visible_max_units, term_units_max)
        else:
            utils.assert_equivalence(visible_max_units, None)

    def test_list_view_term_min_units(self, tc):
        term_units_min = tc.student.enrollment_data.term_units_min(tc.term)
        term_units_min_float = tc.student.enrollment_data.term_units_min_float(tc.term)
        visible_min_units = self.curated_students_page.term_units_min(tc.student)
        if term_units_min and term_units_min_float != '0.5':
            utils.assert_equivalence(visible_min_units, term_units_min)
        else:
            utils.assert_equivalence(visible_min_units, None)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=term_tcs,
                         ids=[tc.test_case_id for tc in term_tcs],
                         scope='class')
class TestStudentPageTermData:

    def test_student_page_expand_terms(self, tc):
        if f'{tc.student.uid}' not in self.driver.current_url:
            self.student_page.load_page(tc.student)
        self.student_page.expand_all_years()
        self.student_page.wait_for_term_data(tc.student.enrollment_data.term_id(tc.term))

    def test_student_page_term_gpa(self, tc):
        term_sis_id = tc.student.enrollment_data.term_id(tc.term)
        visible_gpa = self.student_page.visible_term_gpa(term_sis_id)
        gpa = tc.student.enrollment_data.term_gpa(tc.term)
        if gpa and float(gpa) != 0:
            utils.assert_equivalence(visible_gpa, gpa)
        else:
            utils.assert_equivalence(visible_gpa, '—')

    def test_student_page_term_units(self, tc):
        term_sis_id = tc.student.enrollment_data.term_id(tc.term)
        if term_sis_id == current_term.sis_id:
            term_units = tc.student.enrollment_data.term_units(tc.term)
            visible_term_units = self.student_page.visible_term_units(term_sis_id)
            if term_units and term_units == '0':
                utils.assert_equivalence(visible_term_units, '—')
            else:
                utils.assert_equivalence(visible_term_units, term_units)

    def test_student_page_term_max_units(self, tc):
        term_sis_id = tc.student.enrollment_data.term_id(tc.term)
        term_units_max = tc.student.enrollment_data.term_units_max(tc.term)
        term_units_max_float = tc.student.enrollment_data.term_units_max_float(tc.term)
        visible_max_units = self.student_page.visible_term_units_max(term_sis_id)
        if term_units_max and term_units_max_float != '20.5':
            utils.assert_equivalence(visible_max_units, term_units_max_float)
        else:
            utils.assert_equivalence(visible_max_units, None)

    def test_student_page_term_min_units(self, tc):
        term_sis_id = tc.student.enrollment_data.term_id(tc.term)
        term_units_min = tc.student.enrollment_data.term_units_min(tc.term)
        term_units_min_float = tc.student.enrollment_data.term_units_min_float(tc.term)
        visible_min_units = self.student_page.visible_term_units_min(term_sis_id)
        if term_units_min and term_units_min_float != '0.5':
            utils.assert_equivalence(visible_min_units, term_units_min_float)
        else:
            utils.assert_equivalence(visible_min_units, None)

    def test_student_page_term_academic_standing(self, tc):
        term_sis_id = tc.student.enrollment_data.term_id(tc.term)
        standings = tc.student.academic_standings
        visible_standing = self.student_page.visible_term_academic_standing(term_sis_id)
        term_standing = None
        if standings:
            for st in standings:
                if st.term.sis_id == term_sis_id:
                    term_standing = st
        if term_standing:
            if term_standing.code == 'GST':
                utils.assert_equivalence(visible_standing, None)
            else:
                expected_standing = f'{term_standing.descrip} ({term_standing.term.name})'
                utils.assert_equivalence(visible_standing, expected_standing)
        else:
            utils.assert_equivalence(visible_standing, None)
