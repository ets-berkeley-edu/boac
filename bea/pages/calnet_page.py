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
from bea.pages.homepage import Homepage
from bea.pages.page import Page
from bea.test_utils import utils
from flask import current_app as app
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CalNetPage(Page):

    USERNAME_INPUT = (By.ID, 'username')
    PASSWORD_INPUT = (By.ID, 'password')
    SUBMIT_BUTTON = (By.ID, 'submit')
    TRUST_BROWSER_BUTTON = (By.ID, 'trust-browser-button')
    BAD_CREDS = (By.XPATH, '//span[contains(text(), "Invalid credentials.")]')

    def log_in(self, username=None, password=None):
        Wait(self.driver, utils.get_medium_timeout()).until(ec.title_contains('Central Authentication Service'))
        if username and password:
            app.logger.info(f'{username} is logging in')
            self.wait_for_element_and_type(self.USERNAME_INPUT, username)
            self.wait_for_element_and_type(self.PASSWORD_INPUT, password)
            self.wait_for_element_and_click(self.SUBMIT_BUTTON)
        else:
            if self.headless:
                pytest.exit('Browser is running in headless mode, manual login is not supported')
            else:
                app.logger.info('Waiting for manual login')
                self.wait_for_element_and_type(self.USERNAME_INPUT, 'PLEASE LOG IN MANUALLY')
        tries = 0
        max_tries = utils.get_long_timeout()
        while tries <= max_tries:
            tries += 1
            try:
                assert self.is_present(self.TRUST_BROWSER_BUTTON) \
                       or self.is_present(self.BAD_CREDS) \
                       or self.is_present(BoaPages.HEADER_DROPDOWN) \
                       or self.is_present(Homepage.NOT_AUTH_MSG)
                break
            except AssertionError:
                if tries == max_tries:
                    raise
                else:
                    time.sleep(1)
        if self.is_present(self.TRUST_BROWSER_BUTTON):
            self.wait_for_element_and_click(self.TRUST_BROWSER_BUTTON)
        elif self.is_present(self.BAD_CREDS):
            pytest.exit('Invalid credentials')
