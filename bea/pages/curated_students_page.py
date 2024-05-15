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

import time

from bea.pages.cohort_and_group_student_pages import CohortAndGroupStudentPages
from bea.pages.curated_modal import CuratedModal
from bea.pages.curated_pages import CuratedPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from selenium.webdriver.common.by import By


class CuratedStudentsPage(CohortAndGroupStudentPages, CuratedModal, CuratedPages):

    GROUP_NOT_FOUND_MSG = By.XPATH, '//span[contains(.,"No curated group found with id: ")]'

    def remove_student_button_loc(self, student):
        return f'{self.student_row_xpath(student)}//button[contains(@id, "remove-student-from-curated-group")]'

    def load_everyone_groups_page(self):
        self.driver.get(f'{boa_utils.get_boa_base_url()}/groups/all')
        self.wait_for_boa_title('Groups')

    @staticmethod
    def group_name_heading_loc(group):
        return By.XPATH, f'//h1[@id="curated-group-name"][contains(., "{group.name}")]'

    @staticmethod
    def linked_cohort_link_loc(cohort):
        return By.XPATH, f'//a[contains(@id, "referencing-cohort-")][contains(., "{cohort.name}")]'

    @staticmethod
    def no_deleting_msg_loc(cohort):
        return By.XPATH, f'//div[@id="cohort-warning-body"][contains(., "{cohort.name}")]'

    def remove_student_by_row_index(self, group, student):
        self.wait_for_student_list()
        self.wait_for_element_and_click(self.remove_student_button_loc(student))
        group.members.remove(student)
        time.sleep(2)
        visible_uids = self.list_view_sids()
        visible_uids.sort()
        expected_uids = list(map(lambda m: m.uid, group.members))
        expected_uids.sort()
        assert visible_uids == expected_uids

    def assert_visible_students_match_expected(self, group):
        visible_sids = self.visible_sids()
        visible_sids.sort()
        member_sids = list(map(lambda m: m.sid, group.members))
        member_sids.sort()
        utils.assert_equivalence(visible_sids, member_sids)
