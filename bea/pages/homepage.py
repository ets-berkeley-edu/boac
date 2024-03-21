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

from datetime import datetime

from bea.pages.boa_pages import BoaPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class Homepage(BoaPages):

    SIGN_IN_BUTTON = (By.ID, 'sign-in')
    DEV_AUTH_UID_INPUT = (By.ID, 'dev-auth-uid')
    DEV_AUTH_PASSWORD_INPUT = (By.ID, 'dev-auth-password')
    DEV_AUTH_SUBMIT_BUTTON = (By.ID, 'dev-auth-submit')
    COPYRIGHT = (By.CLASS_NAME, 'copyright')
    NOT_AUTH_MSG = (By.XPATH, '//div[contains(., "Sorry, you are not registered to use BOA.")]')
    DELETED_MSG = (By.XPATH, '//div[contains(., "Sorry, user is not authorized to use BOA.")]')

    def load_page(self):
        self.driver.get(boa_utils.get_boa_base_url())
        self.wait_for_spinner()

    def click_sign_in_button(self):
        self.wait_for_page_and_click(Homepage.SIGN_IN_BUTTON)

    def log_in(self, username, password, cal_net):
        self.load_page()
        self.wait_for_boa_title('Welcome')
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.text_to_be_present_in_element(Homepage.COPYRIGHT, datetime.today().strftime('%Y')),
        )
        self.click_sign_in_button()
        cal_net.log_in(username, password)
        self.wait_for_boa_title('Home')

    def enter_dev_auth_creds(self, user=None):
        uid = user.uid if user else utils.get_admin_uid()
        app.logger.info(f'Logging in UID {uid} using developer auth')
        self.load_page()
        self.wait_for_element_and_type(Homepage.DEV_AUTH_UID_INPUT, uid)
        self.wait_for_element_and_type(Homepage.DEV_AUTH_PASSWORD_INPUT, app.config['DEVELOPER_AUTH_PASSWORD'])
        self.wait_for_element_and_click(Homepage.DEV_AUTH_SUBMIT_BUTTON)

    def dev_auth(self, user=None):
        self.enter_dev_auth_creds(user)
        self.wait_for_boa_title('Home')
