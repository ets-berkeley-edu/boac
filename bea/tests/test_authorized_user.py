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

from bea.models.user import User
from bea.pages.homepage import Homepage
from bea.test_utils import boa_utils
from bea.test_utils import utils
import pytest
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


@pytest.mark.usefixtures('page_objects')
class TestAuthorizedUser:

    auth_user = User({
        'uid': utils.get_admin_uid(),
        'username': utils.get_admin_username(),
    })

    def test_record_each_login(self):
        initial_logins = boa_utils.get_user_login_count(self.auth_user)
        self.homepage.log_in(self.auth_user.username, utils.get_admin_password(), self.calnet_page)
        updated_logins = boa_utils.get_user_login_count(self.auth_user)
        assert initial_logins == updated_logins + 1

    def test_deleted_user_login_not_ok(self):
        self.homepage.log_out()
        boa_utils.soft_delete_user(self.auth_user)
        self.homepage.load_page()
        self.homepage.click_sign_in_button()
        self.calnet_page.log_in(self.auth_user.username, utils.get_admin_password())
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located(Homepage.NOT_AUTH_MSG),
        )

    def test_restored_user_login_ok(self):
        boa_utils.restore_user(self.auth_user)
        self.homepage.click_sign_in_button()
        self.homepage.wait_for_boa_title('Home')

    def test_not_auth_user_login_not_ok(self):
        self.homepage.log_out()
        boa_utils.hard_delete_user(self.auth_user)
        self.homepage.load_page()
        self.homepage.click_sign_in_button()
        self.calnet_page.log_in(self.auth_user.username, utils.get_admin_password())
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located(Homepage.NOT_AUTH_MSG),
        )

    def test_auth_user_login_ok(self):
        boa_utils.create_admin_user(self.auth_user)
        self.homepage.click_sign_in_button()
        self.homepage.wait_for_boa_title('Home')

    def test_expired_cookies_force_login(self):
        self.driver.delete_all_cookies()
        self.search_form.enter_simple_search('foo')
        self.search_form.hit_enter()
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located(Homepage.SIGN_IN_BUTTON),
        )
