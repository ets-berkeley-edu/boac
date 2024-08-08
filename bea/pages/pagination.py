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

from bea.pages.boa_pages import BoaPages
from bea.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class Pagination(BoaPages):

    PAGE_ONE_LINK = By.ID, 'pagination-page-1'
    GO_TO_FIRST_PAGE_LINK = By.ID, 'pagination-first'
    GO_TO_NEXT_PAGE_LINK = By.ID, 'pagination-next'
    GO_TO_LAST_PAGE_LINK = By.ID, 'pagination-last'
    GO_TO_PAGE_LINK = By.XPATH, '//button[starts-with(@id, "pagination-")]'

    def go_to_first_page(self):
        if self.is_present(self.GO_TO_FIRST_PAGE_LINK):
            self.wait_for_element_and_click(self.GO_TO_FIRST_PAGE_LINK)
        Wait(self.driver, utils.get_short_timeout()).until(ec.visibility_of_element_located(self.PAGE_ONE_LINK))

    @staticmethod
    def go_to_page_link(page_number):
        return By.ID, f'pagination-{page_number}'

    def list_view_page_count(self):
        if self.is_present(self.GO_TO_PAGE_LINK):
            if self.is_present(self.GO_TO_LAST_PAGE_LINK):
                self.wait_for_element_and_click(self.GO_TO_LAST_PAGE_LINK)
                time.sleep(1)
                Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.GO_TO_PAGE_LINK))
            pages = list(map(lambda el: el.get_attribute('id').split('-')[-1], self.elements(self.GO_TO_PAGE_LINK)))
            pages = [page for page in pages if page not in ['first', 'prev', 'next', 'last']]
            count = pages[-1]
            self.go_to_first_page()
            return int(count)
        else:
            return 1
