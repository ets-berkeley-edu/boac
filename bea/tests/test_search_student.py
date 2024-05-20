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
test.search_students()


@pytest.mark.usefixtures('page_objects')
class TestLogin:

    def test_advisor_logs_in(self):
        self.homepage.dev_auth(test.advisor)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize('student', test.test_students, scope='class',
                         ids=[student.uid for student in test.test_students])
class TestSearchStudent:

    def test_search_with_complete_first_name(self, student):
        self.homepage.enter_simple_search_and_hit_enter(student.first_name)
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_partial_first_name(self, student):
        if not student.first_name[0:2] == student.first_name:
            self.homepage.enter_simple_search_and_hit_enter(student.first_name[0:2])
            self.homepage.wait_for_spinner()
            assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_complete_last_name(self, student):
        self.homepage.enter_simple_search_and_hit_enter(student.last_name)
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_partial_last_name(self, student):
        if not student.last_name[0:2] == student.last_name:
            self.homepage.enter_simple_search_and_hit_enter(student.last_name[0:2])
            self.homepage.wait_for_spinner()
            assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_complete_first_and_last_name(self, student):
        self.homepage.enter_simple_search_and_hit_enter(f'{student.first_name} {student.last_name}')
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_complete_last_and_first_name_comma_separated(self, student):
        self.homepage.enter_simple_search_and_hit_enter(f'{student.last_name}, {student.first_name}')
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_partial_first_and_last_name(self, student):
        self.homepage.enter_simple_search_and_hit_enter(f'{student.first_name[0:2]} {student.last_name[0:2]}')
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_partial_last_and_first_name_comma_separated(self, student):
        self.homepage.enter_simple_search_and_hit_enter(f'{student.last_name[0:2]}, {student.first_name[0:2]}')
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_complete_sid(self, student):
        self.homepage.enter_simple_search_and_hit_enter(f'{student.sid}')
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_partial_sid(self, student):
        self.homepage.enter_simple_search_and_hit_enter(f'{student.sid}'[0:4])
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_complete_email(self, student):
        self.homepage.enter_simple_search_and_hit_enter(student.email)
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_with_partial_email(self, student):
        self.homepage.enter_simple_search_and_hit_enter(student.email[0:4])
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)

    def test_search_history(self, student):
        self.homepage.clear_simple_search_input()
        expected = [student.email[0:4],
                    student.email,
                    f'{student.sid}'[0:4],
                    f'{student.sid}',
                    f'{student.last_name[0:2]}, {student.first_name[0:2]}']
        utils.assert_equivalence(self.homepage.visible_search_history(), expected)

    def test_search_using_history_item(self, student):
        self.homepage.select_history_item(self.homepage.visible_search_history()[4])
        self.homepage.wait_for_spinner()
        assert self.search_results_page.is_student_in_search_result(student)
