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

from datetime import datetime
import time

from bea.pages.boa_pages import BoaPages
from bea.test_utils import boa_degree_progress_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class DegreeTemplateMgmtPage(BoaPages):

    CREATE_DEGREE_CHECK_LINK = By.ID, 'degree-check-create-btn'
    BATCH_DEGREE_CHECK_LINK = By.ID, 'degree-check-batch-btn'
    CREATE_DEGREE_SAVE_BUTTON = By.ID, 'start-degree-btn'
    CREATE_DEGREE_NAME_INPUT = By.ID, 'create-degree-input'
    DUPE_NAME_MSG = By.XPATH, '//span[contains(., "already exists. Please choose a different name.")]'

    def click_create_degree(self):
        app.logger.info('Clicking the add-degree button')
        self.wait_for_page_and_click(self.CREATE_DEGREE_CHECK_LINK)

    def is_degree_save_enabled(self):
        self.when_present(self.CREATE_DEGREE_SAVE_BUTTON, utils.get_short_timeout())
        return self.element(self.CREATE_DEGREE_SAVE_BUTTON).is_enabled()

    def enter_degree_name(self, name):
        app.logger.info(f'Entering degree check template name {name}')
        self.wait_for_textbox_and_type(self.CREATE_DEGREE_NAME_INPUT, name)

    def degree_name_input_value(self):
        return self.el_value(self.CREATE_DEGREE_NAME_INPUT)

    def click_save_new_degree(self):
        app.logger.info('Clicking new degree check template save button')
        self.wait_for_element_and_click(self.CREATE_DEGREE_SAVE_BUTTON)

    def create_new_degree(self, template):
        self.click_create_degree()
        self.enter_degree_name(template.name)
        self.click_save_new_degree()
        self.when_present((By.XPATH, f'//h1[text()="{template.name}"]'), utils.get_short_timeout())
        boa_degree_progress_utils.set_new_template_id(template)

    def click_batch_degree_checks(self):
        app.logger.info('Clicking the link to create batch degree checks')
        self.wait_for_element_and_click(self.BATCH_DEGREE_CHECK_LINK)

    # LIST

    TEMPLATE_LINK = By.XPATH, '//a[contains(@id, "degree-check-") and not(contains(@id, "print"))]'
    TEMPLATE_CREATE_DATE = By.XPATH, '//td[contains(@id, "-createdAt")]/div'

    def visible_template_names(self):
        return self.els_text_if_exist(self.TEMPLATE_LINK)

    def visible_template_create_dates(self):
        return self.els_text_if_exist(self.TEMPLATE_CREATE_DATE)

    @staticmethod
    def degree_check_row_xpath(degree_check):
        return f'//tr[contains(., "{degree_check.name}")]'

    def degree_check_link(self, degree_check):
        return By.XPATH, f'{self.degree_check_row_xpath(degree_check)}//a'

    def wait_for_degree_link(self, degree_check):
        self.when_present(self.degree_check_link(degree_check), utils.get_short_timeout())

    def degree_check_create_date(self, degree_check):
        loc = By.XPATH, f'{self.degree_check_row_xpath(degree_check)}/td[contains(@id, "-createdAt")]/div'
        text = self.el_text_if_exists(loc)
        if text:
            return datetime.strptime(text, '%b %d, %Y').date()
        else:
            return None

    def click_degree_link(self, degree_check):
        app.logger.info(f'Clicking the link for {degree_check.name}')
        self.wait_for_element_and_click(self.degree_check_link(degree_check))

    # RENAME

    RENAME_DEGREE_INPUT = By.ID, 'rename-template-input'
    RENAME_DEGREE_SAVE_BUTTON = By.ID, 'confirm-rename-btn'
    RENAME_DEGREE_CANCEL_BUTTON = By.ID, 'rename-cancel-btn'

    def degree_check_rename_button(self, degree_check):
        return By.XPATH, f'{self.degree_check_row_xpath(degree_check)}//button[contains(@id, "-rename-btn")]'

    def click_rename_button(self, degree_check):
        app.logger.info(f'Clicking the rename button for template {degree_check.name}')
        self.wait_for_element_and_click(self.degree_check_rename_button(degree_check))

    def enter_new_name(self, name):
        app.logger.info(f'Entering new degree name {name}')
        self.wait_for_textbox_and_type(self.RENAME_DEGREE_INPUT, name)

    def new_name_input_value(self):
        return self.el_value(self.RENAME_DEGREE_INPUT)

    def click_save_new_name(self):
        app.logger.info('Clicking rename save button')
        self.wait_for_element_and_click(self.RENAME_DEGREE_SAVE_BUTTON)

    def click_cancel_new_name(self):
        app.logger.info('Clicking rename cancel button')
        self.wait_for_element_and_click(self.RENAME_DEGREE_CANCEL_BUTTON)

    # COPY

    COPY_DEGREE_NAME_INPUT = By.ID, 'degree-name-input'
    COPY_DEGREE_SAVE_BUTTON = By.ID, 'clone-confirm'
    COPY_DEGREE_CANCEL_BUTTON = By.ID, 'clone-cancel'

    def degree_check_copy_button(self, degree_check):
        return By.XPATH, f'{self.degree_check_row_xpath(degree_check)}//button[contains(@id, "-copy-btn")]'

    def click_copy_button(self, degree_check):
        app.logger.info(f'Clicking the copy button for template {degree_check.name}')
        self.wait_for_element_and_click(self.degree_check_copy_button(degree_check))

    def enter_copy_name(self, name):
        app.logger.info(f'Entering copied degree name {name}')
        self.wait_for_textbox_and_type(self.COPY_DEGREE_NAME_INPUT, name)

    def copy_name_input_value(self):
        return self.el_value(self.COPY_DEGREE_NAME_INPUT)

    def click_save_copy(self):
        app.logger.info('Clicking copy save button')
        self.wait_for_element_and_click(self.COPY_DEGREE_SAVE_BUTTON)

    def click_cancel_copy(self):
        app.logger.info('Clicking copy cancel button')
        self.wait_for_element_and_click(self.COPY_DEGREE_CANCEL_BUTTON)

    # DELETE

    def degree_check_delete_button(self, degree_check):
        return By.XPATH, f'{self.degree_check_row_xpath(degree_check)}//button[contains(@id, "-delete-btn")]'

    def click_delete_degree(self, degree_check):
        app.logger.info(f'Clicking the delete button for template {degree_check.name}')
        self.wait_for_element_and_click(self.degree_check_delete_button(degree_check))

    def click_confirm_delete(self):
        app.logger.info('Clicking the delete confirm button')
        self.wait_for_element_and_click(self.CONFIRM_DELETE_OR_DISCARD)
        time.sleep(1)

    def click_cancel_delete(self):
        app.logger.info('Clicking delete cancel button')
        self.wait_for_element_and_click(self.CANCEL_DELETE_OR_DISCARD)

    # PRINT

    def degree_check_print_button(self, degree_check):
        return By.XPATH, f'{self.degree_check_row_xpath(degree_check)}//a[contains(@id, "print-link")]'

    # BATCH SUCCESS

    BATCH_SUCCESS_MSG = By.ID, 'alert-batch-created'
