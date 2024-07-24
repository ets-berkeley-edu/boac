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
import json
import time

from bea.models.advisor_role import AdvisorRole
from bea.models.department import Department
from bea.models.department_membership import DepartmentMembership
from bea.pages.pagination import Pagination
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class PassengerManifestPage(Pagination):

    def hit_page_url(self):
        self.driver.get(f'{boa_utils.get_boa_base_url()}/admin/passengers')

    def load_page(self):
        self.hit_page_url()
        self.when_present(self.USER_SEARCH_INPUT, utils.get_medium_timeout())
        self.hide_boa_footer()

    # User export

    DOWNLOAD_USERS_BUTTON = By.ID, 'download-boa-users-csv'

    def download_boa_users(self):
        app.logger.info('Downloading BOA users CSV')
        utils.prepare_download_dir()
        self.wait_for_element_and_click(self.DOWNLOAD_USERS_BUTTON)
        return utils.wait_for_export_csv()

    # Filters

    FILTER_MODE_SELECT = By.ID, 'user-filter-options'
    USER_SEARCH_INPUT = By.ID, 'search-user-input'
    AUTOCOMPLETE_NAMES = By.XPATH, '//div[contains(@class, "v-autocomplete")]//div[@role="option"]'
    PERMISSIONS_SELECT = By.ID, 'user-permission-options'
    DEPT_SELECT = By.ID, 'department-select-list'
    STATUS_SELECT = By.ID, 'user-status-options'

    def set_first_auto_suggest(self, locator, name):
        self.wait_for_textbox_and_type(locator, name)
        time.sleep(utils.get_click_sleep())
        Wait(self.driver, utils.get_medium_timeout()).until(
            ec.presence_of_all_elements_located(self.AUTOCOMPLETE_NAMES),
        )
        time.sleep(2)
        self.elements(self.AUTOCOMPLETE_NAMES)[0].click()

    def search_for_advisor(self, advisor):
        app.logger.info(f'Searching for advisor UID {advisor.uid}')
        self.when_present(self.USER_SEARCH_INPUT, utils.get_medium_timeout())
        self.set_first_auto_suggest(self.USER_SEARCH_INPUT, advisor.uid)

    def select_filter_mode(self):
        self.wait_for_select_and_click_option(self.FILTER_MODE_SELECT, 'Filter')

    def select_all_depts(self):
        app.logger.info('Selecting All Departments')
        self.wait_for_select_and_click_option(self.DEPT_SELECT, 'All')

    def select_dept(self, dept):
        app.logger.info(f'Selecting department {dept.name}')
        self.wait_for_select_and_click_option(self.DEPT_SELECT, dept.name)

    def select_admin_mode(self):
        self.wait_for_select_and_click_option(self.FILTER_MODE_SELECT, 'BOA Admins')

    # Advisors table

    ADVISOR_ROW = By.XPATH, '//tr[contains(@id, "tr-user-")]'
    ADVISOR_UID = By.XPATH, '//td[contains(@id, "-column-uid")]'
    ADVISOR_NAME = By.XPATH, '//td[contains(@id, "-column-lastname")]/div/*'
    ADVISOR_DEPT = By.XPATH, '//td[contains(@id, "-column-departments")]'
    ADVISOR_EMAIL = By.XPATH, '//td[contains(@id, "-column-campusemail")]'

    def wait_for_advisor_list(self):
        try:
            time.sleep(1)
            Wait(self.driver, utils.get_medium_timeout()).until(ec.presence_of_all_elements_located(self.ADVISOR_ROW))
        except TimeoutException:
            app.logger.info('There are no advisors listed')

    def list_view_uids(self):
        self.wait_for_advisor_list()
        return list(map(lambda el: el.text, self.elements(self.ADVISOR_UID)))

    def visible_advisor_depts(self, user):
        loc = By.XPATH, f'//span[contains(@id, "dept-") and contains(@id, "-{user.uid}")]/span'
        return list(map(lambda el: el.text, self.elements(loc)))

    def expand_user_row(self, user):
        self.wait_for_element_and_click((By.XPATH, f'//td[@id="td-user-{user.uid}-column-data-table-expand"]/button'))

    def visible_user_details(self, user):
        loc = By.XPATH, f'//tr[@id="tr-user-{user.uid}"]/following-sibling::tr//pre'
        if self.is_present(loc) and self.element(loc).text:
            return json.loads(self.element(loc).text)
        else:
            return ''

    def visible_dept_role(self, user, dept):
        loc = By.XPATH, f'//td[id="td-user-{user.uid}-column-departments"]//span[contains(text(), "{dept.name}")]'
        if self.is_present(loc):
            return self.element(loc).text.split(' - ')[-1]
        else:
            return ''

    @staticmethod
    def become_user_loc(user):
        return By.ID, f'become-{user.uid}'

    def click_become_user_link(self, user):
        app.logger.info(f'Becoming user {user.uid}')
        self.wait_for_page_and_click(self.become_user_loc(user))

    # Add / edit user

    ADD_USER_BUTTON = By.ID, 'add-new-user-btn'
    ADD_USER_UID_INPUT = By.ID, 'uid-input'
    ADMIN_CBX = By.ID, 'is-admin'
    BLOCKED_CBX = By.ID, 'is-blocked'
    DELETED_CBX = By.ID, 'is-deleted'
    CANVAS_DATA_CBX = By.ID, 'can-access-canvas-data'
    NOTES_APPTS_CBX = By.ID, 'can-access-advising-data'
    DEGREE_PROGRESS_SELECT = By.ID, 'degree-progress-permission-select'
    REMOVE_DEPT_BUTTON = By.XPATH, '//button[contains(@id, "remove-department-")]'
    AUTOMATE_DEG_PROG_CBX = By.ID, 'automate-degree-progress-permission'
    SAVE_USER_BUTTON = By.ID, 'save-changes-to-user-profile'
    CANCEL_USER_BUTTON = By.ID, 'delete-cancel'

    @staticmethod
    def dupe_user_loc(user):
        return By.XPATH, f'//div[contains(text(), "User with UID {user.uid} is already in the BOA database.")]'

    @staticmethod
    def remove_dept_role_button_loc(dept):
        return By.ID, f'remove-department-{dept.code}'

    @staticmethod
    def dept_role_select_loc(dept):
        return By.ID, f'select-department-{dept.code}-role'

    @staticmethod
    def is_automated_dept_cbx_loc(dept):
        return By.XPATH, f'//input[@id="is-automate-membership-{dept.code}"]'

    @staticmethod
    def edit_user_button_loc(user):
        return By.ID, f'edit-{user.uid}'

    def click_add_user(self):
        app.logger.info('Clicking the add user button')
        self.wait_for_element_and_click(self.ADD_USER_BUTTON)

    def click_edit_user(self, user):
        app.logger.info(f'Clicking the edit button for UID {user.uid}')
        self.wait_for_element_and_click(self.edit_user_button_loc(user))

    def click_cancel_button(self):
        app.logger.info('Clicking the cancel button')
        self.wait_for_element_and_click(self.CANCEL_USER_BUTTON)

    def set_user_level_flags(self, user):
        app.logger.info(f'UID {user.uid} is-admin is {user.is_admin}')
        if user.is_admin and not self.element(self.ADMIN_CBX).is_selected():
            app.logger.info('Clicking is-admin checkbox')
            self.click_element_js(self.ADMIN_CBX)
            time.sleep(utils.get_click_sleep())
        if user.is_blocked and not self.element(self.BLOCKED_CBX).is_selected():
            app.logger.info('Clicking is-blocked checkbox')
            self.click_element_js(self.BLOCKED_CBX)
            time.sleep(utils.get_click_sleep())
        if (user.can_access_canvas_data and not self.element(self.CANVAS_DATA_CBX).is_selected()) or (
                self.element(self.CANVAS_DATA_CBX).is_selected() and not user.can_access_canvas_data):
            app.logger.info('Clicking can-access-canvas-data checkbox')
            self.click_element_js(self.CANVAS_DATA_CBX)
            time.sleep(utils.get_click_sleep())
        if (user.can_access_advising_data and not self.element(self.NOTES_APPTS_CBX).is_selected()) or (
                self.element(self.NOTES_APPTS_CBX).is_selected() and not user.can_access_advising_data):
            app.logger.info('Clicking can-access-advising-data checkbox')
            self.click_element_js(self.NOTES_APPTS_CBX)
            time.sleep(utils.get_click_sleep())
        if user.depts and Department.COE in user.depts:
            self.select_deg_prog_option(user)

    def select_deg_prog_option(self, user):
        option = user.degree_progress_perm.desc if user.degree_progress_perm else 'Select...'
        self.wait_for_select_and_click_option(self.DEGREE_PROGRESS_SELECT, option)

    def click_automate_deg_prog(self):
        self.when_present(self.AUTOMATE_DEG_PROG_CBX, utils.get_short_timeout())
        self.click_element_js(self.AUTOMATE_DEG_PROG_CBX)

    def add_user_dept_roles(self, user):
        for membership in user.dept_memberships:
            app.logger.info(f'Adding UID {user.uid} department role {vars(membership)}')
            self.wait_for_select_and_click_option(self.DEPT_SELECT, membership.dept.code)
            if membership.advisor_role == AdvisorRole.ADVISOR:
                self.wait_for_select_and_click_option(self.dept_role_select_loc(membership.dept), 'Advisor')
            elif membership.advisor_role == AdvisorRole.DIRECTOR:
                self.wait_for_select_and_click_option(self.dept_role_select_loc(membership.dept), 'Director')
            if (membership.is_automated and not self.element(self.is_automated_dept_cbx_loc(membership.dept)).is_selected()) or (
                    self.element(self.is_automated_dept_cbx_loc(membership.dept)).is_selected() and not membership.is_automated):
                self.click_element_js(self.is_automated_dept_cbx_loc(membership.dept))
                time.sleep(utils.get_click_sleep())

    def save_user(self):
        self.wait_for_element_and_click(self.SAVE_USER_BUTTON)
        self.when_not_present(self.SAVE_USER_BUTTON, utils.get_short_timeout())

    def enter_new_user_data(self, user):
        self.wait_for_textbox_and_type(self.ADD_USER_UID_INPUT, user.uid)
        self.set_user_level_flags(user)
        self.add_user_dept_roles(user)
        self.wait_for_element_and_click(self.SAVE_USER_BUTTON)

    def add_user(self, user):
        app.logger.info(f'Adding UID {user.uid}')
        self.click_add_user()
        self.enter_new_user_data(user)
        self.when_not_present(self.SAVE_USER_BUTTON, utils.get_short_timeout())

    def edit_user(self, user):
        app.logger.info(f'Editing UID {user.uid} with attributes {vars(user)}')
        self.click_edit_user(user)
        self.when_present(self.ADMIN_CBX, utils.get_short_timeout())
        self.set_user_level_flags(user)
        if (user.active and not self.element(self.DELETED_CBX).is_selected()) or (
                self.element(self.DELETED_CBX).is_selected() and not user.active):
            app.logger.info('Clicking is-deleted checkbox')
            self.click_element_js(self.DELETED_CBX)
            time.sleep(utils.get_click_sleep())
        for el in self.elements(self.REMOVE_DEPT_BUTTON):
            el.click()
            time.sleep(2)
        self.add_user_dept_roles(user)
        if user.degree_progress_perm:
            self.select_deg_prog_option(user)
        self.save_user()

    def search_for_and_edit_user(self, user):
        self.search_for_advisor(user)
        self.when_present(self.edit_user_button_loc(user), utils.get_short_timeout())
        self.edit_user(user)

    def set_deg_prog_perm(self, user, dept, perm):
        if not user.degree_progress_perm == perm:
            self.search_for_advisor(user)
            user.dept_memberships = [DepartmentMembership(advisor_role=AdvisorRole.ADVISOR, dept=dept, is_automated=True)]
            user.degree_progress_perm = perm
            self.edit_user(user)
