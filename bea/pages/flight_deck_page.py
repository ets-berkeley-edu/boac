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
from selenium.webdriver.common.by import By


class FlightDeckPage(BoaPages):
    MY_PROFILE_HEADING = By.XPATH, '//h1[text()="Profile"]'
    DEMO_MODE_TOGGLE = By.ID, 'toggle-demo-mode'

    def load_advisor_page(self):
        self.driver.get(f'{boa_utils.get_boa_base_url()}/profile')
        self.when_visible(self.MY_PROFILE_HEADING, utils.get_short_timeout())

    # SERVICE ALERTS

    EDIT_SERVICE_ALERT_HEADING = By.ID, 'edit-service-announcement'
    POST_SERVICE_ALERT_CHECKBOX = By.ID, 'checkbox-publish-service-announcement'
    UPDATE_SERVICE_ALERT_INPUT = By.XPATH, '(//div[@role="textbox"])[2]'
    UPDATE_SERVICE_ALERT_BUTTON = By.ID, 'button-update-service-announcement'

    def service_alert_checkbox_label(self):
        return self.element(self.POST_SERVICE_ALERT_CHECKBOX).get_attribute('aria-label')

    def dismiss_alert(self):
        app.logger.info('Dismissing service alert')
        self.wait_for_element_and_click(self.DISMISS_ALERT_BUTTON)
        self.when_not_present(self.SERVICE_ALERT_BANNER, 1)

    def update_service_alert(self, alert_string):
        app.logger.info(f'Entering service alert {alert_string}')
        self.wait_for_textbox_and_type(self.UPDATE_SERVICE_ALERT_INPUT, alert_string)
        self.wait_for_element_and_click(self.UPDATE_SERVICE_ALERT_BUTTON)

    def toggle_service_alert_checkbox(self, new_label):
        app.logger.info('Clicking the service alert checkbox')
        self.when_present(self.POST_SERVICE_ALERT_CHECKBOX, utils.get_short_timeout())
        time.sleep(utils.get_click_sleep())
        if new_label == 'Posted' and self.service_alert_checkbox_label() == 'Post' \
                or new_label == 'Post' and self.service_alert_checkbox_label() == 'Posted':
            self.click_element_js(self.POST_SERVICE_ALERT_CHECKBOX)
            if new_label == 'Posted':
                self.when_present(self.SERVICE_ALERT_BANNER, 2)
            else:
                self.when_not_present(self.SERVICE_ALERT_BANNER, 2)

    def post_service_alert(self):
        app.logger.info('Posting a service alert')
        self.toggle_service_alert_checkbox('Posted')

    def unpost_service_alert(self):
        app.logger.info('Un-posting a service alert')
        self.toggle_service_alert_checkbox('Post')

    # TOPICS

    TOPIC_SEARCH_INPUT = By.ID, 'filter-topics'
    TOPIC_SEARCH_CLEAR_BUTTON = By.XPATH, '//button[contains(., "Clear")]'
    TOPIC_CREATE_BUTTON = By.ID, 'new-note-button'
    TOPIC_NAME_INPUT = By.ID, 'topic-label'
    TOPIC_SAVE_BUTTON = By.ID, 'topic-save'
    TOPIC_CANCEL_BUTTON = By.ID, 'cancel'
    TOPIC_VALIDATION_MSG = By.ID, 'topic-label-error'
    TOPIC_LENGTH_MSG = By.ID, 'input-live-help'

    def label_validation_error(self):
        return self.element(self.TOPIC_VALIDATION_MSG).text

    def label_length_error(self):
        return self.element(self.TOPIC_LENGTH_MSG).text

    @staticmethod
    def topic_row_xpath(topic):
        return f'//h2[text()="Manage Topics"]/following-sibling::div//tbody//td[text()="{topic.name}"]/..'

    def topic_row(self, topic):
        return By.XPATH, self.topic_row_xpath(topic)

    def is_topic_deleted(self, topic):
        return self.element((By.XPATH, f'{self.topic_row_xpath(topic)}/td[2]')).text == 'Yes'

    def topic_in_notes_count(self, topic):
        return self.element((By.XPATH, f'{self.topic_row_xpath(topic)}/td[3]')).text

    def topic_deletion_toggle_button(self, topic):
        return By.XPATH, f'{self.topic_row_xpath(topic)}/td[4]/button'

    def click_create_topic(self):
        app.logger.info('Clicking the Create topic button')
        self.wait_for_page_and_click(self.TOPIC_CREATE_BUTTON)

    def click_save_topic(self):
        app.logger.info('Clicking the Save topic button')
        self.wait_for_element_and_click(self.TOPIC_SAVE_BUTTON)

    def click_cancel_topic(self):
        app.logger.info('Clicking the Cancel topic button')
        self.wait_for_element_and_click(self.TOPIC_CANCEL_BUTTON)
        self.when_not_present(self.TOPIC_NAME_INPUT, 1)

    def delete_or_undelete_topic(self, topic):
        app.logger.info(f'Clicking the delete button for topic {topic.name}')
        self.wait_for_element_and_click(self.topic_deletion_toggle_button(topic))
        self.confirm_delete_or_discard()

    def enter_topic_label(self, label):
        app.logger.info(f'Entering topic label {label}')
        self.wait_for_element_and_type(self.TOPIC_NAME_INPUT, label)

    def create_topic(self, topic):
        self.click_create_topic()
        self.enter_topic_label(topic.name)
        self.click_save_topic()
        self.set_new_topic_id(topic)

    @staticmethod
    def set_new_topic_id(topic):
        timeout = utils.get_short_timeout()
        tries = 0
        while tries <= timeout:
            tries += 1
            try:
                assert boa_utils.get_topic_id(topic)
                break
            except AssertionError:
                if tries == 0:
                    raise
                else:
                    time.sleep(1)

    def search_for_topic(self, topic):
        app.logger.info(f'Searching for topic {topic.name}')
        self.wait_for_element_and_type(self.TOPIC_SEARCH_INPUT, topic.name)
        time.sleep(utils.get_click_sleep())
