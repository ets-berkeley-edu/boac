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
import time

from bea.pages.user_list_pages import UserListPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class Homepage(UserListPages):

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

    # FILTERED COHORTS AND CURATED GROUPS

    NO_FILTERED_COHORTS_MSG = By.ID, 'no-cohorts-header'
    FILTERED_COHORT = By.XPATH, '//button[contains(@id,"sortable-cohort")]//h3'
    CURATED_GROUP = By.XPATH, '//div[contains(@id,"sortable-curated")]//h3'

    @staticmethod
    def user_rows(xpath):
        return By.XPATH, f'{xpath}//tbody/tr[@class="v-data-table__tr"]'

    def filtered_cohorts(self):
        Wait(self.driver, utils.get_medium_timeout()).until(ec.presence_of_all_elements_located(self.FILTERED_COHORT))
        els = self.elements(self.FILTERED_COHORT)
        return list(map(lambda el: el.text.replace('Show details for cohort', '').split(':')[0].strip(), els))

    def curated_groups(self):
        Wait(self.driver, utils.get_medium_timeout()).until(ec.presence_of_all_elements_located(self.CURATED_GROUP))
        els = self.elements(self.CURATED_GROUP)
        return list(map(lambda el: el.text.replace('Show details for curated group', '').split(':')[0].strip(), els))

    @staticmethod
    def view_all_members_link_loc(cohort):
        if cohort.__class__.__name__ == 'FilteredCohort':
            return By.ID, f'sortable-cohort-{cohort.cohort_id}-view-all'
        else:
            return By.ID, f'sortable-curated-{cohort.cohort_id}-view-all'

    def expand_member_rows(self, cohort):
        time.sleep(2)
        if not (self.is_present(self.view_all_members_link_loc(cohort)) and self.element(
                self.view_all_members_link_loc(cohort)).is_displayed()):
            if cohort.__class__.__name__ == 'FilteredCohort':
                self.wait_for_element_and_click((By.ID, f'sortable-cohort-{cohort.cohort_id}-expand-btn'))
            else:
                self.wait_for_element_and_click((By.ID, f'sortable-curated-{cohort.cohort_id}-expand-btn'))

    def member_rows(self, cohort):
        if cohort.__class__.__name__ == 'FilteredCohort':
            return self.user_rows(self.filtered_cohort_xpath(cohort))
        else:
            return self.user_rows(self.curated_group_xpath(cohort))

    def member_count(self, cohort):
        if cohort.__class__.__name__ == 'FilteredCohort':
            loc = By.ID, f'sortable-cohort-{cohort.cohort_id}-total-student-count'
        else:
            loc = By.ID, f'sortable-curated-{cohort.cohort_id}-total-student-count'
        return int(self.element(loc).text) if self.is_present(loc) else None

    def verify_member_alerts(self, cohort, advisor, cohort_members_with_alerts=None):
        if cohort.members:
            member_alerts = boa_utils.get_un_dismissed_users_alerts(cohort.members, advisor)
        else:
            member_alerts = []
        alert_members = cohort_members_with_alerts or boa_utils.get_members_with_alerts(cohort, member_alerts)
        alert_members.sort(key=lambda m: (m.last_name, m.first_name, m.sid), reverse=False)
        alert_members.sort(key=lambda m: m.alert_count, reverse=True)
        alert_members = alert_members[0:50]

        # Verify the total cohort/group alert-bearing member count
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located(self.view_all_members_link_loc(cohort)),
        )
        rows = self.elements(self.member_rows(cohort))
        utils.assert_equivalence(len(rows), len(alert_members))

        # Verify the alert count per expected member
        for member in alert_members:
            app.logger.info(f'Checking cohort row for SID {member.sid}')
            utils.assert_equivalence(self.user_row_data(member.sid, cohort)['alert_count'], str(member.alert_count))

    def click_filtered_cohort(self, cohort):
        app.logger.info(f'Clicking link to my cohort {cohort.name}')
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.FILTERED_COHORT))
        self.wait_for_element_and_click(self.view_all_members_link_loc(cohort))
