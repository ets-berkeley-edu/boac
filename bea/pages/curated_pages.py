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

from bea.pages.cohort_pages import CohortPages
from bea.pages.curated_modal import CuratedModal
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CuratedPages(CohortPages, CuratedModal):

    RENAME_GROUP_BUTTON = By.ID, 'rename-curated-group-button'
    RENAME_GROUP_CONFIRM_BUTTON = By.ID, 'rename-curated-group-confirm'
    RENAME_GROUP_CANCEL_BUTTON = By.ID, 'rename-curated-group-cancel'
    RENAME_GROUP_INPUT = By.ID, 'rename-curated-group-input'

    def load_page(self, group):
        self.driver.get(f'{boa_utils.get_boa_base_url()}/curated/{group.cohort_id}')
        self.wait_for_spinner()
        self.hide_boa_footer()

    def hit_non_auth_group(self, group):
        self.driver.get(f'{boa_utils.get_boa_base_url()}/curated/{group.cohort_id}')
        self.wait_for_404()

    def rename_group(self, group, new_name):
        app.logger.info(f'Changing the name of group ID {group.cohort_id} to {new_name}')
        self.load_page(group)
        self.wait_for_page_and_click(self.RENAME_GROUP_BUTTON)
        self.wait_for_element_and_type(self.RENAME_GROUP_INPUT, new_name)
        self.wait_for_element_and_click(self.RENAME_GROUP_CONFIRM_BUTTON)
        group.name = new_name
        self.when_present(self.cohort_heading_loc(group), utils.get_short_timeout())

    # DELETE

    DELETE_GROUP_BUTTON = By.ID, 'delete-curated-group-button'
    CONFIRM_DELETE_GROUP_BUTTON = By.ID, 'are-you-sure-confirm'
    CANCEL_DELETE_GROUP_BUTTON = By.ID, 'are-you-sure-cancel'

    def delete_group(self, group):
        app.logger.info(f'Deleting a group named {group.name}')
        self.wait_for_page_and_click(self.DELETE_GROUP_BUTTON)
        self.wait_for_element_and_click(self.CONFIRM_DELETE_GROUP_BUTTON)
        Wait(self.driver, utils.get_short_timeout()).until(ec.url_contains(f'{boa_utils.get_boa_base_url()}/home'))
        time.sleep(utils.get_click_sleep())

    def load_and_delete_group(self, group):
        self.load_page(group)
        self.delete_group(group)

    def cancel_group_deletion(self, group):
        app.logger.info(f'Canceling the deletion of cohort {group.name}')
        self.wait_for_page_and_click(self.DELETE_GROUP_BUTTON)
        self.wait_for_element_and_click(self.CANCEL_DELETE_GROUP_BUTTON)
        self.when_not_present(self.CONFIRM_DELETE_GROUP_BUTTON, utils.get_short_timeout())
        Wait(self.driver, 1).until(ec.url_contains(f'{group.cohort_id}'))

    # ADD STUDENTS / ADMITS

    ADD_STUDENTS_BUTTON = By.ID, 'bulk-add-sids-button'
    CREATE_GROUP_TEXTAREA_SIDS = By.ID, 'curated-group-bulk-add-sids'
    ADD_SIDS_TO_GROUP_BUTTON = By.ID, 'btn-curated-group-bulk-add-sids'
    SIDS_BAD_FORMAT_ERROR_MSG = By.XPATH, '//div[contains(text(), "SIDs must be separated by commas, line breaks, or tabs.")]'
    SIDS_NOT_FOUND_ERROR_MSG = By.XPATH, '//div[contains(text(), "not found")]'
    REMOVE_INVALID_SIDS_BUTTON = By.ID, 'remove-invalid-sids-btn'

    def click_add_sids_button(self):
        self.wait_for_element_and_click(self.ADD_STUDENTS_BUTTON)

    def click_add_sids_to_group_button(self):
        self.wait_for_page_and_click(self.ADD_SIDS_TO_GROUP_BUTTON)

    def click_remove_invalid_sids(self):
        app.logger.info('Clicking button to remove invalid SIDs')
        self.when_present(self.REMOVE_INVALID_SIDS_BUTTON, utils.get_medium_timeout())
        self.click_element_js(self.REMOVE_INVALID_SIDS_BUTTON)
        self.when_not_present(self.REMOVE_INVALID_SIDS_BUTTON, utils.get_short_timeout())

    def create_group_with_bulk_sids(self, group, members):
        self.enter_comma_sep_sids(self.CREATE_GROUP_TEXTAREA_SIDS, members)
        self.click_add_sids_to_group_button()
        self.name_and_save_group(group)
        boa_utils.append_new_members_to_group(group, members)
        self.wait_for_sidebar_group(group)

    def enter_text_in_sids_input(self, sids_string):
        self.click_add_sids_button()
        self.enter_sid_list(self.CREATE_GROUP_TEXTAREA_SIDS, sids_string)

    def add_comma_sep_sids_to_existing_grp(self, group, members):
        self.click_add_sids_button()
        self.enter_comma_sep_sids(self.CREATE_GROUP_TEXTAREA_SIDS, members)
        self.click_add_sids_to_group_button()
        boa_utils.append_new_members_to_group(group, members)

    def add_line_sep_sids_to_existing_grp(self, group, members):
        self.click_add_sids_button()
        self.enter_line_sep_sids(self.CREATE_GROUP_TEXTAREA_SIDS, members)
        self.click_add_sids_to_group_button()
        boa_utils.append_new_members_to_group(group, members)

    def add_space_sep_sids_to_existing_grp(self, group, members):
        self.click_add_sids_button()
        self.enter_space_sep_sids(self.CREATE_GROUP_TEXTAREA_SIDS, members)
        self.click_add_sids_to_group_button()
        boa_utils.append_new_members_to_group(group, members)
