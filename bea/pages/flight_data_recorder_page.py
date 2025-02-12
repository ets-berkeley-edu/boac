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
import time

from bea.pages.boa_pages import BoaPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class FlightDataRecorderPage(BoaPages):

    def load_page(self, dept):
        app.logger.info(f"Hitting the FDR page for {dept.value['name']}")
        self.driver.get(f"{boa_utils.get_boa_base_url()}/analytics/{dept.value['code']}")

    DEPT_SELECT = By.ID, 'available-department-reports'
    SHOW_HIDE_REPORT_BUTTON = By.ID, 'show-hide-notes-report'
    NOTES_COUNT_BOA = By.XPATH, '//h3[contains(text(), " notes have been created in BOA")]'
    NOTES_COUNT_BOA_AUTHORS = By.ID, 'notes-count-boa-authors'
    NOTES_COUNT_BOA_ATTACHMENTS = By.ID, 'notes-count-boa-with-attachments'
    NOTES_COUNT_BOA_TOPICS = By.ID, 'notes-count-boa-with-topics'
    NOTES_COUNT_SIS = By.ID, 'notes-count-sis'
    NOTES_COUNT_ASC = By.ID, 'notes-count-asc'
    NOTES_COUNT_EI = By.ID, 'notes-count-ei'

    ADVISOR_LINK = By.XPATH, '//a[contains(@id, "directory-link-")]'
    ADVISOR_NON_LINK = By.XPATH, '//span[contains(text(), "Name unavailable (UID:")]'

    def boa_note_count(self):
        return self.el_text_if_exists(self.NOTES_COUNT_BOA, 'notes have been created in BOA')

    def select_dept_report(self, dept):
        app.logger.info(f"Selecting report for {dept.value['code']}")
        self.wait_for_select_and_click_option(self.DEPT_SELECT, dept.value['code'])
        time.sleep(2)

    def dept_select_option_names(self):
        self.when_present(self.DEPT_SELECT, utils.get_short_timeout())
        sel = Select(self.element(self.DEPT_SELECT))
        return [el.text for el in sel.options]

    def toggle_note_report_visibility(self):
        app.logger.info('Clicking the show/hide report button')
        self.wait_for_element_and_click(self.SHOW_HIDE_REPORT_BUTTON)

    def list_view_uids(self):
        time.sleep(2)
        self.when_present(self.ADVISOR_LINK, utils.get_short_timeout())
        link_els = self.elements(self.ADVISOR_LINK)
        uids = [el.get_attribute('id').split('-')[-1] for el in link_els]
        non_link_els = self.elements(self.ADVISOR_NON_LINK)
        non_link_uids = [el.split[-1].replace(')') for el in non_link_els]
        uids.extend(non_link_uids)

    def advisor_role(self, advisor, dept):
        return self.el_text_if_exists((By.ID, f"dept-{dept.value['code']}-{advisor.uid}"))

    def advisor_note_count(self, advisor):
        if self.is_present((By.ID, f'directory-link-{advisor.uid}')):
            xpath = f'//a[@id="directory-link-{advisor.uid}"]'
        else:
            xpath = f'//span[text()="Name unavailable (UID: {advisor.uid})"]'
        return self.el_text_if_exists(
            (By.XPATH, f'{xpath}//ancestor::td/following-sibling::td[@data-label="Notes Created"]/div'))

    def advisor_last_login(self, advisor):
        return self.el_text_if_exists((By.ID, f'user-last-login-{advisor.uid}'))
