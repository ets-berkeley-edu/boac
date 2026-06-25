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

import pytz
from flask import current_app as app
from selenium.webdriver.common.by import By

from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.student_page_timeline import StudentPageTimeline
from bea.test_utils import utils


class StudentPageAppointment(StudentPageTimeline, CreateNoteModal):

    APPTS_BUTTON = By.ID, 'timeline-tab-appointment'
    SHOW_HIDE_APPTS_BUTTON = By.ID, 'timeline-tab-appointment-previous-messages'
    TOGGLE_ALL_APPTS_BUTTON = By.ID, 'toggle-expand-all-appointments'
    APPT_MSG_ROW = By.XPATH, '//div[contains(@id,"timeline-tab-appointment-message")]'
    APPT_TOPIC = By.XPATH, '//li[contains(@id, "topic")]'

    def show_appts(self):
        app.logger.info('Checking appointments tab')
        self.wait_for_element_and_click(self.APPTS_BUTTON)
        if self.is_present(self.SHOW_HIDE_APPTS_BUTTON) and 'Show' in self.element(self.SHOW_HIDE_APPTS_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_APPTS_BUTTON)

    def appt_els(self):
        return self.elements(self.APPT_MSG_ROW)

    TIMELINE_APPTS_QUERY_INPUT = (By.ID, 'timeline-appointments-query-input')
    TIMELINE_APPTS_SPINNER = (By.ID, 'timeline-appointments-spinner')

    def search_within_timeline_appts(self, query):
        app.logger.info(f"Searching for '{query}'")
        self.wait_for_textbox_and_type_chars(self.TIMELINE_APPTS_QUERY_INPUT, query)
        time.sleep(1)
        self.when_not_present(self.TIMELINE_APPTS_SPINNER, utils.get_short_timeout())

    def clear_timeline_appt_search(self):
        self.search_within_timeline_appts('')

    def visible_appt_ids(self):
        ids = []
        els = self.elements((By.XPATH, '//article[starts-with(@id, "timeline-appointment")]'))
        for el in els:
            parts = el.get_dom_attribute('id').split('-')[2:]
            ids.append('-'.join(parts))
        return ids

    @staticmethod
    def appt_advisor_loc(appt):
        return By.ID, f'note-{appt.record_id}-author-name'

    def collapsed_appt_detail(self, appt):
        return self.el_text_if_exists((By.ID, f'appointment-{appt.record_id}-details-closed'))

    def collapsed_appt_status(self, appt):
        return self.el_text_if_exists((By.XPATH, f'//div[starts-with(@id, "collapsed-appointment-{appt.record_id}-status-")]'))

    def collapsed_appt_date(self, appt):
        return self.el_text_if_exists((By.ID, f'collapsed-appointment-{appt.record_id}-created-at'), 'Last updated on')

    def expanded_appt_details(self, appt):
        return self.el_text_if_exists((By.ID, f'appointment-{appt.record_id}-details'))

    def expanded_appt_date(self, appt):
        return self.el_text_if_exists((By.ID, f'expanded-appointment-{appt.record_id}-created-at'), 'Appointment date')

    def expanded_appt_time_range(self, appt):
        return self.el_text_if_exists((By.ID, f'expanded-appointment-{appt.record_id}-appt-time-range'))

    @staticmethod
    def expected_appt_time_range(appt):
        tz = pytz.timezone(app.config['TIMEZONE'])
        start = appt.start_time.astimezone(tz).strftime('%-I:%M%p')
        end = appt.end_time.astimezone(tz).strftime('%-I:%M%p')
        return f'{start} - {end}'

    def expanded_appt_check_in_time(self, appt):
        return self.el_text_if_exists((By.ID, f'appointment-{appt.record_id}-checked-in-at'))

    def expanded_appt_cancel_reason(self, appt):
        return self.el_text_if_exists((By.ID, f'appointment-{appt.record_id}-cancel-reason'))

    def expanded_appt_cancel_addl_info(self, appt):
        return self.el_text_if_exists((By.ID, f'appointment-{appt.record_id}-cancel-explained'))

    def expanded_appt_advisor_name(self, appt):
        return self.el_text_if_exists(self.appt_advisor_loc(appt))

    def expanded_appt_advisor_role(self, appt):
        return self.el_text_if_exists((By.ID, f'appointment-{appt.record_id}--advisor-role'))

    def expanded_appt_advisor_depts(self, appt):
        return self.els_text_if_exist((By.XPATH, f'//span[contains(@id, "appointment-{appt.record_id}-advisor-dept-")]'))

    def expanded_appt_type(self, appt):
        return self.el_text_if_exists((By.ID, f'appointment-{appt.record_id}-type'))

    def expanded_appt_topics(self, appt):
        return self.els_text_if_exist((By.XPATH, f'//div[contains(@id, "appointment-{appt.record_id}-topic-")]'))

    def expanded_appt_attachments(self, appt):
        return [self.attachment_name_from_link(el).lower() for el in self.item_attachment_els(appt)]

    # COMMENTS

    @staticmethod
    def appt_add_comment_button_loc(appt):
        return By.ID, f'appointment-{appt.record_id}-add-comment-btn'

    @staticmethod
    def appt_new_comment_text_area_loc(appt):
        return By.XPATH, f'//div[@id="appointment-{appt.record_id}-comment-new-text"]//div[@role="textbox"]'

    @staticmethod
    def appt_new_comment_save_loc(appt):
        return By.ID, f'appointment-{appt.record_id}-comment-new-save-btn'

    @staticmethod
    def appt_new_comment_cancel_loc(appt):
        return By.ID, f'appointment-{appt.record_id}-comment-new-cancel-btn'

    @staticmethod
    def appt_comment_body_loc(appt, comment):
        return By.ID, f'appointment-{appt.record_id}-comment-{comment.comment_id}-text'

    @staticmethod
    def appt_comment_edit_button_loc(appt, comment):
        return By.ID, f'appointment-{appt.record_id}-comment-{comment.comment_id}-edit-btn'

    @staticmethod
    def appt_comment_delete_button_loc(appt, comment):
        return By.ID, f'appointment-{appt.record_id}-comment-{comment.comment_id}-delete-btn'

    @staticmethod
    def appt_edit_comment_text_area_loc(appt, comment):
        return By.XPATH, f'//div[@id="appointment-{appt.record_id}-comment-{comment.comment_id}-text"]//div[@role="textbox"]'

    @staticmethod
    def appt_edit_comment_save_loc(appt, comment):
        return By.ID, f'appointment-{appt.record_id}-comment-{comment.comment_id}-save-btn'

    def click_add_appt_comment_button(self, appt):
        app.logger.debug(f'Clicking Add Comment button for appointment {appt.record_id}')
        self.wait_for_element_and_click(self.appt_add_comment_button_loc(appt))

    def save_new_appt_comment(self, appt):
        app.logger.debug('Saving new appointment comment')
        self.wait_for_element_and_click(self.appt_new_comment_save_loc(appt))
        self.when_not_present(self.appt_new_comment_save_loc(appt), utils.get_short_timeout())

    def cancel_new_appt_comment(self, appt):
        app.logger.debug('Canceling new appointment comment')
        self.wait_for_element_and_click(self.appt_new_comment_cancel_loc(appt))
        self.when_not_present(self.appt_new_comment_cancel_loc(appt), utils.get_short_timeout())

    def add_appt_comment(self, appt, comment):
        app.logger.info(f'Adding comment to appointment {appt.record_id}')
        self.click_add_appt_comment_button(appt)
        self.wait_for_textbox_and_send_keys(self.appt_new_comment_text_area_loc(appt), comment.body)
        self.save_new_appt_comment(appt)

    def click_edit_appt_comment_button(self, appt, comment):
        app.logger.debug(f'Clicking edit button for appointment comment {comment.comment_id}')
        self.wait_for_element_and_click(self.appt_comment_edit_button_loc(appt, comment))

    def save_edit_appt_comment(self, appt, comment):
        app.logger.debug('Saving appointment comment edit')
        self.wait_for_element_and_click(self.appt_edit_comment_save_loc(appt, comment))
        self.when_not_present(self.appt_edit_comment_save_loc(appt, comment), utils.get_short_timeout())

    def delete_appt_comment(self, appt, comment):
        app.logger.info(f'Deleting comment {comment.comment_id} from appointment {appt.record_id}')
        self.wait_for_element_and_click(self.appt_comment_delete_button_loc(appt, comment))
        self.confirm_delete_or_discard()
        self.when_not_present(self.appt_comment_body_loc(appt, comment), utils.get_short_timeout())

    def appt_comment_body_text(self, appt, comment):
        loc = self.appt_comment_body_loc(appt, comment)
        return self.element(loc).text if self.is_present(loc) else None
