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
import re
import time

from flask import current_app as app
from selenium.webdriver.common.by import By

from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.student_page_timeline import StudentPageTimeline
from bea.test_utils import utils


class StudentPageEForm(StudentPageTimeline, CreateNoteModal):

    # E-FORMS

    E_FORMS_BUTTON = (By.ID, 'timeline-tab-eForm')
    SHOW_HIDE_E_FORMS_BUTTON = (By.ID, 'timeline-tab-eForm-previous-messages')
    E_FORM_MSG_ROW = By.XPATH, '//article[contains(@id, "timeline-eForm-")]'
    TIMELINE_E_FORMS_QUERY_INPUT = (By.ID, 'timeline-eForms-query-input')

    def show_e_forms(self):
        app.logger.info('Checking eForms tab')
        self.wait_for_element_and_click(self.E_FORMS_BUTTON)
        if self.is_present(self.SHOW_HIDE_E_FORMS_BUTTON) and 'Show' in self.element(
                self.SHOW_HIDE_E_FORMS_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_E_FORMS_BUTTON)

    def search_within_timeline_e_forms(self, query):
        app.logger.info(f"Searching for '{query}'")
        self.scroll_to_top()
        self.wait_for_textbox_and_send_keys(self.TIMELINE_E_FORMS_QUERY_INPUT, query)
        time.sleep(1)

    def visible_e_form_ids(self):
        return self.visible_collapsed_item_ids('eForm')

    @staticmethod
    def e_form_data_loc(e_form, label):
        return By.XPATH, f"//article[@id='timeline-eForm-{e_form.record_id}']//dt[text()='{label}']/following-sibling::dd"

    def collapsed_e_form_date(self, e_form):
        date_loc = By.ID, f'collapsed-eForm-{e_form.record_id}-created-at'
        return self.el_text_if_exists(date_loc, 'Last updated on')

    def expanded_e_form_created_date(self, e_form):
        created_loc = By.ID, f'expanded-eForm-{e_form.record_id}-created-at'
        if self.is_present(created_loc):
            text = self.element(created_loc).text.replace('Created on', '').replace('\n@\n', '\n')
            return re.sub(r'/\s+ /', ' ', text).strip()
        else:
            return None

    def expanded_e_form_updated_date(self, e_form):
        updated_loc = By.ID, f'expanded-eForm-{e_form.record_id}-updated-at'
        if self.is_present(updated_loc):
            text = self.element(updated_loc).text.replace('Last updated on', '').replace('\n@\n', '\n')
            return re.sub(r'/\s+ /', ' ', text).strip()
        else:
            return None

    def expanded_e_form_action(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Action'))

    def expanded_e_form_course(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Course'))

    def expanded_e_form_date_final(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Final Date & Time Stamp'))

    def expanded_e_form_date_init(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Date Initiated'))

    def expanded_e_form_id(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Form ID'))

    def expanded_e_form_status(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Form Status '))

    def expanded_e_form_term(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Term'))

    # COMMENTS

    @staticmethod
    def e_form_add_comment_button_loc(e_form):
        return By.ID, f'eForm-{e_form.record_id}-add-comment-btn'

    @staticmethod
    def e_form_new_comment_text_area_loc(e_form):
        return By.XPATH, f'//div[@id="eForm-{e_form.record_id}-comment-new-text"]//div[@role="textbox"]'

    @staticmethod
    def e_form_new_comment_save_loc(e_form):
        return By.ID, f'eForm-{e_form.record_id}-comment-new-save-btn'

    @staticmethod
    def e_form_new_comment_cancel_loc(e_form):
        return By.ID, f'eForm-{e_form.record_id}-comment-new-cancel-btn'

    @staticmethod
    def e_form_comment_body_loc(e_form, comment):
        return By.ID, f'eForm-{e_form.record_id}-comment-{comment.comment_id}-text'

    @staticmethod
    def e_form_comment_edit_button_loc(e_form, comment):
        return By.ID, f'eForm-{e_form.record_id}-comment-{comment.comment_id}-edit-btn'

    @staticmethod
    def e_form_comment_delete_button_loc(e_form, comment):
        return By.ID, f'eForm-{e_form.record_id}-comment-{comment.comment_id}-delete-btn'

    @staticmethod
    def e_form_edit_comment_text_area_loc(e_form, comment):
        return By.XPATH, f'//div[@id="eForm-{e_form.record_id}-comment-{comment.comment_id}-text"]//div[@role="textbox"]'

    @staticmethod
    def e_form_edit_comment_save_loc(e_form, comment):
        return By.ID, f'eForm-{e_form.record_id}-comment-{comment.comment_id}-save-btn'

    def click_add_e_form_comment_button(self, e_form):
        app.logger.debug(f'Clicking Add Comment button for eForm {e_form.record_id}')
        self.wait_for_element_and_click(self.e_form_add_comment_button_loc(e_form))

    def save_new_e_form_comment(self, e_form):
        app.logger.debug('Saving new eForm comment')
        self.wait_for_element_and_click(self.e_form_new_comment_save_loc(e_form))
        self.when_not_present(self.e_form_new_comment_save_loc(e_form), utils.get_short_timeout())

    def cancel_new_e_form_comment(self, e_form):
        app.logger.debug('Canceling new eForm comment')
        self.wait_for_element_and_click(self.e_form_new_comment_cancel_loc(e_form))
        self.when_not_present(self.e_form_new_comment_cancel_loc(e_form), utils.get_short_timeout())

    def add_e_form_comment(self, e_form, comment):
        app.logger.info(f'Adding comment to eForm {e_form.record_id}')
        self.click_add_e_form_comment_button(e_form)
        self.wait_for_textbox_and_send_keys(self.e_form_new_comment_text_area_loc(e_form), comment.body)
        self.save_new_e_form_comment(e_form)

    def click_edit_e_form_comment_button(self, e_form, comment):
        app.logger.debug(f'Clicking edit button for eForm comment {comment.comment_id}')
        self.wait_for_element_and_click(self.e_form_comment_edit_button_loc(e_form, comment))

    def save_edit_e_form_comment(self, e_form, comment):
        app.logger.debug('Saving eForm comment edit')
        self.wait_for_element_and_click(self.e_form_edit_comment_save_loc(e_form, comment))
        self.when_not_present(self.e_form_edit_comment_save_loc(e_form, comment), utils.get_short_timeout())

    def delete_e_form_comment(self, e_form, comment):
        app.logger.info(f'Deleting comment {comment.comment_id} from eForm {e_form.record_id}')
        self.wait_for_element_and_click(self.e_form_comment_delete_button_loc(e_form, comment))
        self.confirm_delete_or_discard()
        self.when_not_present(self.e_form_comment_body_loc(e_form, comment), utils.get_short_timeout())

    def e_form_comment_body_text(self, e_form, comment):
        loc = self.e_form_comment_body_loc(e_form, comment)
        return self.element(loc).text if self.is_present(loc) else None
