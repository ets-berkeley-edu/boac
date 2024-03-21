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

from bea.pages.page import Page
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By


class BoaPages(Page):

    SPINNER = (By.ID, 'spinner-when-loading')

    def wait_for_spinner(self):
        time.sleep(1)
        try:
            if self.is_present(BoaPages.SPINNER):
                self.when_not_visible(BoaPages.SPINNER, utils.get_medium_timeout())
        except StaleElementReferenceException as e:
            app.logger.debug(f'{e}')

    # HEADER

    HOME_LINK = (By.ID, 'home-header')
    HEADER_DROPDOWN = (By.ID, 'header-dropdown-under-name__BV_toggle_')
    FLIGHT_DATA_RECORDER_LINK = (By.ID, 'header-menu-analytics')
    FLIGHT_DECK_LINK = (By.ID, 'header-menu-flight-deck')
    PAX_MANIFEST_LINK = (By.ID, 'header-menu-passengers')
    PROFILE_LINK = (By.ID, 'header-menu-profile')
    FEEDBACK_LINK = (By.XPATH, '//a[contains(text(), "Feedback/Help")]')
    LOG_OUT_LINK = (By.XPATH, '//a[contains(text(), "Log Out")]')
    CONFIRM_DELETE_OR_DISCARD = (By.ID, 'are-you-sure-confirm')
    CANCEL_DELETE_OR_DISCARD = (By.ID, 'are-you-sure-cancel')

    def wait_for_boa_title(self, string):
        self.wait_for_title(f'{string} | BOA')

    def click_header_dropdown(self):
        self.wait_for_element_and_click(BoaPages.HEADER_DROPDOWN)

    def open_menu(self):
        if not self.is_present(BoaPages.LOG_OUT_LINK) or not self.element(BoaPages.LOG_OUT_LINK).is_displayed():
            app.logger.info('Clicking header menu button')
            self.click_header_dropdown()

    def log_out(self):
        app.logger.info('Logging out')
        if not self.is_present(BoaPages.HEADER_DROPDOWN):
            self.driver.get(f'{boa_utils.get_boa_base_url()}')
        self.open_menu()
        self.wait_for_element_and_click(BoaPages.LOG_OUT_LINK)

        # In case logout doesn't work the first time, try again
        time.sleep(2)
        if self.is_present(BoaPages.LOG_OUT_LINK):
            if not self.element(BoaPages.LOG_OUT_LINK).is_displayed():
                self.open_menu()
                self.wait_for_element_and_click(BoaPages.LOG_OUT_LINK)
            time.sleep(2)

        self.wait_for_boa_title('Welcome')

    def confirm_delete_or_discard(self):
        self.wait_for_element_and_click(self.CONFIRM_DELETE_OR_DISCARD)

    def cancel_delete_or_discard(self):
        self.wait_for_element_and_click(self.CANCEL_DELETE_OR_DISCARD)

    # BATCH NOTES

    BATCH_NOTE_BUTTON = By.ID, 'batch-note-button'
