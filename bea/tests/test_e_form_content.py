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
from bea.test_utils import utils
import pytest

test = BEATestConfig()
test.e_form_content()
list_tcs = [tc for tc in test.test_cases if isinstance(tc.note, list)]
detail_tcs = [tc for tc in test.test_cases if not isinstance(tc.note, list)]


@pytest.mark.usefixtures('page_objects')
class TestAdvisorLogin:

    def test_log_in(self):
        self.homepage.load_page()
        self.homepage.dev_auth(test.advisor)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=list_tcs,
                         ids=[tc.test_case_id for tc in list_tcs],
                         scope='class')
class TestEFormList:

    def test_load_student_e_forms(self, tc):
        self.student_page.load_page(tc.student)
        self.student_page.show_e_forms()

    def test_e_form_count(self, tc):
        visible = self.student_page.elements(self.student_page.E_FORM_MSG_ROW)
        utils.assert_equivalence(len(visible), len(tc.note))

    def test_e_form_order(self, tc):
        visible = self.student_page.visible_collapsed_note_ids()
        expected = self.student_page.expected_e_form_id_sort_order(tc.note)
        utils.assert_equivalence(visible, expected)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=detail_tcs,
                         ids=[tc.test_case_id for tc in detail_tcs],
                         scope='class')
class TestEFormDetail:

    def test_load_student_e_form(self, tc):
        if tc.student.uid not in self.driver.current_url:
            self.student_page.load_page(tc.student)
        self.student_page.show_e_forms()

    def test_collapsed_date(self, tc):
        show_update_date = tc.note.updated_date and tc.note.updated_date != tc.note.created_date
        expected_date = tc.note.updated_date if show_update_date else tc.note.created_date
        expected = self.student_page.expected_item_short_date_format(expected_date)
        visible = self.student_page.collapsed_e_form_date(tc.note)
        utils.assert_equivalence(visible, expected)

    def test_collapsed_subject(self, tc):
        visible = self.student_page.collapsed_note_subject(tc.note) or ''
        utils.assert_equivalence(visible.strip(), tc.note.subject.strip())

    def test_expanded_created_date(self, tc):
        self.student_page.expand_item(tc.note)
        visible = self.student_page.expanded_e_form_created_date(tc.note)
        expected = self.student_page.expected_item_short_date_format(tc.note.created_date)
        utils.assert_equivalence(visible, expected)

    def test_expanded_updated_date(self, tc):
        visible = self.student_page.expanded_e_form_updated_date(tc.note)
        expected = self.student_page.expected_item_long_date_format(tc.note.updated_date)
        utils.assert_equivalence(visible, expected)

    def test_expanded_term(self, tc):
        utils.assert_equivalence(self.student_page.expanded_e_form_term(tc.note), tc.note.term)

    def test_expanded_course(self, tc):
        utils.assert_equivalence(self.student_page.expanded_e_form_course(tc.note), tc.note.course)

    def test_expanded_form_id(self, tc):
        utils.assert_equivalence(self.student_page.expanded_e_form_id(tc.note), tc.note.form_id)

    def test_expanded_date_initiated(self, tc):
        visible = self.student_page.expanded_e_form_date_init(tc.note)
        expected = tc.note.created_date.strftime('%m/%d/%Y')
        utils.assert_equivalence(visible, expected)

    def test_expanded_form_status(self, tc):
        utils.assert_equivalence(self.student_page.expanded_e_form_status(tc.note), tc.note.status)

    def test_expanded_final_date(self, tc):
        visible = self.student_page.expanded_e_form_date_final(tc.note)
        expected = tc.note.updated_date.strftime('%m/%d/%Y %-l:%M:%S%p')
        utils.assert_equivalence(visible, expected)
