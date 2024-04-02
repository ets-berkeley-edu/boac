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

import datetime
import time

from bea.pages.pagination import Pagination
from bea.pages.user_list_pages import UserListPages
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class ListViewStudentPages(Pagination, UserListPages):

    PLAYER_LINK = By.XPATH, '//a[contains(@href, "/student/")]'
    PLAYER_NAME = By.XPATH, '//h3[contains(@class, "student-name")]'
    PLAYER_SID = By.XPATH, '//div[contains(@id, "student-sid")]'

    def wait_for_players(self):
        Wait(self.driver, utils.get_medium_timeout()).until(ec.presence_of_all_elements_located(self.PLAYER_LINK))

    def wait_for_student_list(self):
        try:
            start = datetime.datetime.now()
            time.sleep(1)
            self.wait_for_players()
            app.logger.info(f'Took {(datetime.datetime.now() - start).total_seconds()} seconds for users to appear')
        except TimeoutError:
            app.logger.info('There are no students listed')

    def list_view_names(self):
        self.wait_for_players()
        return list(map(lambda el: el.text, self.elements(self.PLAYER_NAME)))

    def list_view_sids(self):
        self.wait_for_players()
        time.sleep(utils.get_click_sleep())
        return list(map(lambda el: el.text, self.elements(self.PLAYER_SID)))

    @staticmethod
    def student_row_xpath(student):
        return f'//div[@id="student-{student.uid}]'

    @staticmethod
    def student_link_loc(self, student):
        return By.ID, f'link-to-student-{student.uid}'

    def student_has_inactive_asc_flag(self, student):
        self.is_present((By.XPATH, f'{self.student_row_xpath(student)}//div[contains(text(), "ASC INACTIVE")]'))

    def student_has_inactive_coe_flag(self, student):
        self.is_present((By.XPATH, f'{self.student_row_xpath(student)}//div[contains(text(), "CoE INACTIVE")]'))

    def student_academic_standing(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//div[@class="student-academic-standing"]'
        return self.element(loc).text.strip() if self.is_present(loc) else None

    def student_sports(self, student):
        loc = By.XPATH, f'{self.student_row_xpath(student)}//span[contains(@id, "student-team")]/..'
        return list(map(lambda el: el.get_attribute('innerText'), self.elements(loc)))

    def list_view_uids(self):
        return list(map(lambda el: el.get_attribute('id').split('-')[-1], self.elements(self.PLAYER_LINK)))

    def visible_sids(self, filtered_cohort=None):
        if not (filtered_cohort and len(filtered_cohort.members) == 0):
            self.wait_for_student_list()
        sids = []
        time.sleep(2)
        page_count = self.list_view_page_count()
        page = 1
        if page_count == 1:
            app.logger.info('There is 1 page')
            sids.extend(self.list_view_sids())
        else:
            app.logger.info(f'There are {page_count} pages')
            sids.extend(self.list_view_sids())
            for i in range(page_count - 1):
                start = datetime.datetime.now()
                page += 1
                self.wait_for_page_and_click(self.GO_TO_NEXT_PAGE_LINK)
                self.wait_for_players()
                app.logger.info(f'Page {page} took {(datetime.datetime.now() - start).total_seconds()} seconds to load')
                sids.extend(self.list_view_sids())
        app.logger.info(f'Visible SIDs: {sids}')
        return sids

    def click_student_link(self, student):
        app.logger.info(f'Clicking the link for UID {student.uid}')
        self.wait_for_page_and_click(self.student_link_loc(student))
        Wait(self.driver, utils.get_medium_timeout()).until(ec.visibility_of_element_located(self.STUDENT_NAME_HEADING))

    def compare_visible_sid_sorting_to_expected(self, expected_sids):
        visible_results = self.visible_sids()
        self.verify_list_view_sorting(expected_sids, visible_results)
