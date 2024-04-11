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

    PAGE_ONE_LINK = By.XPATH, '(//div[@id="pagination-widget-outer"])[1]//button[@aria-label="Go to page 1"]'
    GO_TO_FIRST_PAGE_LINK = By.XPATH, '(//div[@id="pagination-widget-outer"])[1]//button[@aria-label="Go to first page"]'
    GO_TO_NEXT_PAGE_LINK = By.XPATH, '(//div[@id="pagination-widget-outer"])[1]//button[@aria-label="Go to next page"]'
    GO_TO_LAST_PAGE_LINK = By.XPATH, '(//div[@id="pagination-widget-outer"])[1]//button[@aria-label="Go to last page"]'
    GO_TO_PAGE_LINK = By.XPATH, '(//div[@id="pagination-widget-outer"])[1]//button[contains(@aria-label,"Go to page")]'

    def go_to_first_page(self):
        if self.is_present(self.GO_TO_FIRST_PAGE_LINK):
            self.wait_for_element_and_click(self.GO_TO_FIRST_PAGE_LINK)
        Wait(self.driver, utils.get_short_timeout()).until(ec.visibility_of_element_located(self.PAGE_ONE_LINK))
        self.wait_for_element_attribute(self.PAGE_ONE_LINK, 'aria-checked')

    def list_view_page_count(self):
        if self.is_present(self.GO_TO_LAST_PAGE_LINK):
            self.wait_for_element_and_click(self.GO_TO_LAST_PAGE_LINK)
            time.sleep(1)
            Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.GO_TO_PAGE_LINK))
            count = self.elements(self.GO_TO_PAGE_LINK)[-1].text
            self.go_to_first_page()
            return int(count)
        elif self.elements(self.GO_TO_PAGE_LINK):
            return len(self.elements(self.GO_TO_PAGE_LINK))
        else:
            return 1
