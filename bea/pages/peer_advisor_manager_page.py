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


class PeerAdvisorManagerPage(BoaPages):

    def hit_peer_advisor_manager_page_url(self, peer_dept_id):
        app.logger.info('Hitting peer advisor manager page URL')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/peer/management/{peer_dept_id}')

    def load_peer_advisor_manager_page(self, peer_dept_id):
        self.hit_peer_advisor_manager_page_url(peer_dept_id)
        self.when_present(self.ACCT_MGMT_TAB, utils.get_short_timeout())

    # ACCT MGMT

    ACCT_MGMT_TAB = By.ID, 'peer-advising-management-count-accounts'

    def click_acct_mgmt_tab(self):
        app.logger.info('Clicking Acct Mgmt')
        self.wait_for_element_and_click(self.ACCT_MGMT_TAB)

    # Create peer

    ADD_STUDENT_INPUT = By.ID, 'add-student-input'
    ADD_STUDENT_BTN = By.ID, 'add-student-add-button'

    def search_student_by_uid(self, student):
        # Hit escape to dismiss any existing option lists
        self.hit_escape()
        self.wait_for_textbox_and_type(self.ADD_STUDENT_INPUT, student.uid)

    def search_student_by_name(self, student):
        # Hit escape to dismiss any existing option lists
        self.hit_escape()
        self.wait_for_textbox_and_type(self.ADD_STUDENT_INPUT, student.full_name)

    @staticmethod
    def peer_auto_suggest_option(student):
        return By.XPATH, f'//div[@role="option"]//div[contains(., "{student.uid}")]'

    def add_peer(self, student):
        app.logger.info(f'Looking up UID {student.uid}')
        self.search_student_by_uid(student)
        self.wait_for_element_and_click(self.peer_auto_suggest_option(student))
        self.when_present(self.peer_advisor_row(student), utils.get_short_timeout())

    # Peer table

    SHOW_INACTIVE_TOGGLE = By.ID, 'toggle-inactive-students-button'

    def show_deleted_peers(self):
        self.when_present(self.SHOW_INACTIVE_TOGGLE, utils.get_short_timeout())
        if self.element(self.SHOW_INACTIVE_TOGGLE).is_selected():
            app.logger.info('Deleted peers should already be visible')
        else:
            self.wait_for_element_and_click(self.SHOW_INACTIVE_TOGGLE)

    def hide_deleted_peers(self):
        self.when_present(self.SHOW_INACTIVE_TOGGLE, utils.get_short_timeout())
        if self.element(self.SHOW_INACTIVE_TOGGLE).is_selected():
            self.wait_for_element_and_click(self.SHOW_INACTIVE_TOGGLE)
        else:
            app.logger.info('Deleted peers should already be hidden')

    def visible_peer_advisor_uids(self):
        self.when_present(self.ADD_STUDENT_INPUT, utils.get_short_timeout())
        time.sleep(utils.get_click_sleep())
        els = self.elements((By.XPATH, '//tr[starts-with(@id, "tr-member-")]'))
        return [el.get_dom_attribute('id').split('-')[-1] for el in els]

    @staticmethod
    def peer_advisor_row_xpath(user):
        return f'//tr[@id="tr-member-{user.uid}"]'

    def peer_advisor_row(self, user):
        return By.XPATH, self.peer_advisor_row_xpath(user)

    def peer_advisor_name(self, user):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_advisor_row_xpath(user)}/td[1]'))

    def peer_advisor_note_count(self, user):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_advisor_row_xpath(user)}/td[2]'))

    def peer_advisor_date(self, user):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_advisor_row_xpath(user)}/td[3]'))

    @staticmethod
    def peer_advisor_remove_btn(user):
        return By.ID, f'delete-peer-advisor-{user.uid}'

    @staticmethod
    def peer_advisor_restore_btn(user):
        return By.ID, f'restore-peer-advisor-{user.uid}'

    def delete_peer(self, user):
        app.logger.info(f'Deleting peer UID {user.uid}')
        self.wait_for_element_and_click(self.peer_advisor_remove_btn(user))

    def restore_peer(self, user):
        app.logger.info(f'Restoring peer UID {user.uid}')
        self.wait_for_element_and_click(self.peer_advisor_restore_btn(user))
        self.when_present(self.peer_advisor_remove_btn(user))

    @staticmethod
    def sortable_header(header_text):
        return By.XPATH, f'//th[contains(., "{header_text}")]'

    def sort_by_name(self):
        app.logger.info('Clicking sort-by-name')
        self.wait_for_element_and_click(self.sortable_header('Peer Advisor'))

    def sort_by_notes_count(self):
        app.logger.info('Clicking sort-by-note-count')
        self.wait_for_element_and_click(self.sortable_header('Notes Created'))

    def sort_by_date(self):
        app.logger.info('Clicking sort-by-date_added')
        self.wait_for_element_and_click(self.sortable_header('Date Added'))

    # NOTE TEMPLATES

    NOTE_TEMPLATES_TAB = By.ID, 'peer-advising-management-count-templatess'

    def click_note_templates_tab(self):
        app.logger.info('Clicking Note Templates')
        self.wait_for_element_and_click(self.NOTE_TEMPLATES_TAB)

    # Template table

    def visible_peer_template_ids(self):
        self.when_present(self.CREATE_PEER_TEMPLATE_BTN, utils.get_short_timeout())
        time.sleep(utils.get_click_sleep())
        els = self.elements((By.XPATH, '//tbody/tr/td[3]/button[1]'))
        return [el.get_dom_attribute('id').split('-')[-1] for el in els]

    @staticmethod
    def peer_template_row_xpath(template):
        return f'//tr[contains(., "{template.name}")]'

    def peer_template_row(self, template):
        return By.XPATH, self.peer_template_row_xpath(template)

    def peer_template_name(self, template):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_template_row_xpath(template)}/td[1]'))

    def peer_template_date(self, template):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_template_row_xpath(template)}/td[2]'))

    def peer_template_edit_btn(self, template):
        return By.XPATH, f'{self.peer_template_row_xpath(template)}//button[1]'

    def peer_template_copy_btn(self, template):
        return By.XPATH, f'{self.peer_template_row_xpath(template)}//button[2]'

    def peer_template_delete_btn(self, template):
        return By.XPATH, f'{self.peer_template_row_xpath(template)}//button[3]'

    CREATE_PEER_TEMPLATE_BTN = By.ID, 'create-new-peer-advising-note-template'
    PEER_TEMPLATE_NAME_INPUT = By.ID, 'peer-advising-note-template-name-text'
    PEER_TEMPLATE_CANCEL_BTN = By.ID, 'cancel-peer-advising-note-template'
    PEER_TEMPLATE_SAVE_BTN = By.ID, 'save-new-peer-advising-note-template'

    def enter_peer_template_name(self, name):
        app.logger.info(f'Entering peer advising template name {name}')
        self.wait_for_textbox_and_type(self.PEER_TEMPLATE_NAME_INPUT, name)

    def add_peer_template_topics(self, template):
        for topic in template.topics:
            app.logger.info(f'Adding topic {topic.name}')
            self.wait_for_select_and_click_option(self.ADD_TOPIC_SELECT, topic.name)
            self.when_present(self.topic_pill(topic), utils.get_short_timeout())

    def enter_peer_template_data(self, template):
        self.enter_peer_template_name(template)
        self.enter_note_body(template)
        self.add_peer_template_topics(template)

    def click_save_peer_template(self):
        app.logger.info('Saving peer advisor template')
        self.wait_for_element_and_click(self.PEER_TEMPLATE_SAVE_BTN)

    def click_cancel_peer_template(self):
        app.logger.info('Canceling peer advisor template')
        self.wait_for_element_and_click(self.PEER_TEMPLATE_CANCEL_BTN)
        self.when_not_present(self.PEER_TEMPLATE_NAME_INPUT, 2)

    def is_save_peer_template_enabled(self):
        return self.element(self.PEER_TEMPLATE_SAVE_BTN).is_enabled()

    # Create

    def click_create_peer_template(self):
        app.logger.info('Clicking create-peer-template button')
        self.wait_for_element_and_click(self.CREATE_PEER_TEMPLATE_BTN)

    def create_peer_template(self, template):
        self.click_create_peer_template()
        self.enter_peer_template_data(template)
        self.click_save_peer_template()
        self.set_new_template_id(template)
        self.when_present(self.peer_template_row(template), 2)

    # Edit

    def click_edit_peer_template(self, template):
        app.logger.info(f'Editing template {template.record_id}')
        self.wait_for_element_and_click(self.peer_template_edit_btn(template))

    def edit_peer_template(self, template):
        self.click_edit_peer_template(template)
        self.enter_peer_template_data(template)
        self.click_save_peer_template()
        self.when_present(self.peer_template_row(template), 2)

    # Copy

    def click_copy_peer_template(self, template):
        app.logger.info(f'Copying template {template.record_id}')
        self.wait_for_element_and_click(self.peer_template_copy_btn(template))

    # TODO - copy_peer_template

    # Delete

    def click_delete_peer_template(self, template):
        app.logger.info(f'Clicking delete for template {template.record_id}')
        self.wait_for_element_and_click(self.peer_template_delete_btn(template))

    def delete_peer_template(self, template):
        app.logger.info(f'Deleting template {template.record_id}')
        self.click_delete_peer_template(template)
        self.confirm_delete_or_discard()
        self.when_not_present(self.peer_template_row(template))

    # REPORTING & STATISTICS

    REPORTING_TAB = By.ID, 'peer-advising-management-tab-reportings'

    def click_reporting_tab(self):
        app.logger.info('Clicking Reporting & Statistics')
        self.wait_for_element_and_click(self.REPORTING_TAB)

    # TODO
