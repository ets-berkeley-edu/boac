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
from bea.models.advisor_role import AdvisorRole
from bea.models.department import Department
from bea.test_utils import utils
from flask import current_app as app
import pytest


@pytest.mark.usefixtures('page_objects')
class TestUserRoleDirector:

    test = BEATestConfig()
    test.user_role_director()
    director_depts = []
    for memb in test.advisor.dept_memberships:
        if memb.advisor_role == AdvisorRole.DIRECTOR:
            director_depts.append(memb)
    student = test.test_students[0]
    all_notes = test.get_test_notes(student, -1)[0]
    app.logger.info(f'{all_notes}')
    for note in all_notes:
        app.logger.info(f'{vars(note)}')

    def test_log_in(self):
        self.homepage.load_page()
        self.homepage.dev_auth(self.test.advisor)

    def test_student_page_download_notes_zip(self):
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        self.student_page.download_notes(self.student)

    def test_student_page_download_notes_file_names(self):
        expected = self.student_page.expected_note_export_file_names(self.student, self.all_notes, self.test.advisor)
        expected.sort()
        actual = self.student_page.note_export_file_names(self.student)
        actual.sort()
        utils.assert_equivalence(actual, expected)

    def test_student_page_download_notes_csv(self):
        for note in self.all_notes:
            self.student_page.verify_note_in_export_csv(self.student, note, self.test.advisor)

    def test_flight_data_recorder_depts(self):
        self.student_page.click_flight_data_recorder_link()
        if len(self.director_depts) > 1:
            expected = [memb.dept.value['name'] for memb in self.director_depts]
            expected.sort()
            options = self.flight_data_recorder_page.dept_select_option_names()
            options.sort()
            utils.assert_equivalence(options, expected)
        else:
            assert not self.flight_data_recorder_page.is_present(self.flight_data_recorder_page.DEPT_SELECT)

    def test_flight_data_recorder_no_non_auth_depts(self):
        non_auth_dept = next(filter(lambda d: d not in [self.director_depts], Department))
        self.flight_data_recorder_page.load_page(non_auth_dept)
        self.flight_data_recorder_page.wait_for_spinner()
        assert not self.flight_data_recorder_page.is_present(self.flight_data_recorder_page.DEPT_SELECT)
        assert not self.flight_data_recorder_page.is_present(self.flight_data_recorder_page.ADVISOR_LINK)
