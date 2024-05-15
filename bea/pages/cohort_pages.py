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
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CohortPages(BoaPages):

    RESULTS = By.XPATH, '//h1'
    EXPORT_LIST_BUTTON = By.ID, 'export-student-list-button'
    FERPA_WARNING_LINK = By.XPATH, '//a[contains(text(), "Office of the Registrar\'s FERPA guide")]'
    EXPORT_LIST_CXL_BUTTON = By.ID, 'export-list-cancel'
    HISTORY_BUTTON = By.ID, 'show-cohort-history-button'
    BACK_TO_COHORT_BUTTON = By.XPATH, '//button[contains(text(), "Back to Cohort")]'

    @staticmethod
    def cohort_heading_loc(cohort):
        return By.XPATH, f'//h1[contains(text(),"{cohort.name}")]'

    def results_count(self):
        time.sleep(2)
        Wait(self.driver, utils.get_short_timeout())
        return int(self.element(self.RESULTS).text.split(' ')[0])

    def click_export_list(self):
        self.wait_for_element(self.EXPORT_LIST_BUTTON, utils.get_medium_timeout())
        Wait(self.driver, 3).until(ec.element_to_be_clickable(self.element(self.EXPORT_LIST_BUTTON)))
        self.wait_for_element_and_click(self.EXPORT_LIST_BUTTON)

    def click_cancel_export_list(self):
        self.wait_for_element_and_click(self.EXPORT_LIST_CXL_BUTTON)

    # SAVE/CREATE

    SAVE_COHORT_BUTTON_ONE = By.ID, 'save-button'
    COHORT_NAME_INPUT = By.ID, 'create-input'
    SAVE_COHORT_BUTTON_TWO = By.ID, 'create-confirm'
    CANCEL_COHORT_BUTTON = By.ID, 'create-cancel'
    APPLY_BUTTON = By.ID, 'unsaved-filter-apply'

    def click_save_cohort_button_one(self):
        time.sleep(2)
        self.wait_for_element_and_click(self.SAVE_COHORT_BUTTON_ONE)

    def apply_and_save_cohort(self):
        self.wait_for_element_and_click(self.APPLY_BUTTON)
        self.wait_for_element_and_click(self.SAVE_COHORT_BUTTON_ONE)

    def name_cohort(self, cohort):
        self.wait_for_element_and_type(self.COHORT_NAME_INPUT, cohort.name)
        self.wait_for_element_and_click(self.SAVE_COHORT_BUTTON_TWO)

    def save_and_name_cohort(self, cohort):
        self.click_save_cohort_button_one()
        self.name_cohort(cohort)

    def wait_for_filtered_cohort(self, cohort):
        self.wait_for_element(self.cohort_heading_loc(cohort), utils.get_medium_timeout())
        boa_utils.set_filtered_cohort_id(cohort)

    def cancel_cohort(self):
        try:
            self.wait_for_element_and_click(self.CANCEL_COHORT_BUTTON)
            self.when_not_present(self.MODAL, utils.get_short_timeout())
        except NoSuchElementException:
            app.logger.info('No cancel button to click')

    def create_new_cohort(self, cohort):
        app.logger.info(f'Creating a new cohort named {cohort.name}')
        self.save_and_name_cohort(cohort)
        self.wait_for_filtered_cohort(cohort)

    # RENAME

    RENAME_COHORT_BUTTON = By.ID, 'rename-button'
    RENAME_COHORT_CONFIRM_BUTTON = By.ID, 'rename-confirm'
    RENAME_COHORT_CANCEL_BUTTON = By.ID, 'rename-cancel'
    RENAME_COHORT_INPUT = By.ID, 'rename-cohort-input'

    def rename_cohort(self, cohort, new_name):
        app.logger.info(f'Changing the name of cohort ID {cohort.cohort_id} to {new_name}')
        self.load_cohort(cohort)
        self.wait_for_page_and_click(self.RENAME_COHORT_BUTTON)
        self.wait_for_element_and_type(self.RENAME_COHORT_INPUT, new_name)
        self.wait_for_element_and_click(self.RENAME_COHORT_CONFIRM_BUTTON)
        cohort.name = new_name
        self.wait_for_element(self.cohort_heading_loc(cohort), utils.get_short_timeout())

    # DELETE

    DELETE_COHORT_BUTTON = By.ID, 'delete-button'
    CONFIRM_DELETE_BUTTON = By.ID, 'delete-confirm'
    CANCEL_DELETE_BUTTON = By.ID, 'delete-cancel'

    def delete_cohort(self, cohort):
        app.logger.info(f'Deleting a cohort named {cohort.name}')
        self.wait_for_page_and_click(self.DELETE_COHORT_BUTTON)
        self.wait_for_element_and_click(self.CONFIRM_DELETE_BUTTON)
        Wait(self.driver, utils.get_short_timeout()).until(ec.url_contains(f'{boa_utils.get_boa_base_url()}/home'))
        time.sleep(utils.get_click_sleep())

    def cancel_cohort_deletion(self, cohort):
        app.logger.info(f'Canceling the deletion of cohort {cohort.name}')
        self.wait_for_page_and_click(self.DELETE_COHORT_BUTTON)
        self.wait_for_element_and_click(self.CANCEL_DELETE_BUTTON)
        self.when_not_present(self.CONFIRM_DELETE_BUTTON, utils.get_short_timeout())
        Wait(self.driver, 1).until(ec.url_contains(f'{cohort.cohort_id}'))

    # SORTING

    COHORT_SORT_BUTTON = By.ID, 'students-sort-by__BV_toggle_'

    @staticmethod
    def sort_option_loc(option):
        return By.XPATH, f'//button[@id="sort-by-option-{option}"]'

    def sort_by(self, option):
        app.logger.info(f'Sorting by {option}')
        self.wait_for_element_and_click(self.COHORT_SORT_BUTTON)
        self.wait_for_element_and_click(self.sort_option_loc(option))
        self.wait_for_spinner()

    def sort_by_first_name(self):
        self.sort_by('first_name')

    def sort_by_last_name(self):
        self.sort_by('last_name')
