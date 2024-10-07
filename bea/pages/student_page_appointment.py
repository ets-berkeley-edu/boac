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

from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.student_page_timeline import StudentPageTimeline
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class StudentPageAppointment(StudentPageTimeline, CreateNoteModal):

    APPTS_BUTTON = By.ID, 'timeline-tab-appointment'
    SHOW_HIDE_APPTS_BUTTON = By.ID, 'timeline-tab-appointment-previous-messages'
    TOGGLE_ALL_APPTS_BUTTON = By.ID, 'toggle-expand-all-appointments'
    APPTS_EXPANDED_MSG = By.XPATH, '//span[text()="Collapse all appointments"]'
    APPTS_COLLAPSED_MSG = By.XPATH, '//span[text()="Expand all appointments"]'
    APPT_MSG_ROW = By.XPATH, '//div[contains(@id,"timeline-tab-appointment-message")]'
    APPT_TOPIC = By.XPATH, '//li[contains(@id, "topic")]'

    def show_appts(self):
        app.logger.info('Checking appointments tab')
        self.wait_for_element_and_click(self.APPTS_BUTTON)
        if self.is_present(self.SHOW_HIDE_APPTS_BUTTON) and 'Show' in self.element(self.SHOW_HIDE_APPTS_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_APPTS_BUTTON)

    def expand_all_appts(self):
        app.logger.info('Expanding all appointments')
        self.wait_for_element_and_click(self.TOGGLE_ALL_APPTS_BUTTON)
        self.when_visible(self.APPTS_EXPANDED_MSG, 2)

    def collapse_all_appts(self):
        app.logger.info('Collapsing all appointments')
        self.wait_for_element_and_click(self.TOGGLE_ALL_APPTS_BUTTON)
        self.when_visible(self.APPTS_COLLAPSED_MSG, 2)

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
        els = self.elements((By.XPATH, '//tr[starts-with(@id, "permalink-appointment")]'))
        for el in els:
            parts = el.get_attribute('id').split('-')[2:]
            ids.append('-'.join(parts))
        return ids

    def collapsed_appt_ids(self):
        return self.visible_collapsed_item_ids('appointment')

    @staticmethod
    def appt_advisor_loc(appt):
        return By.ID, f'appointment-{appt.record_id}-advisor-name'

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
        return self.els_text_if_exist((By.XPATH, f'//span[contains(@id, "appointment-{appt.record_id}-topic")]'))

    def expanded_appt_attachments(self, appt):
        return [el.text.strip().lower() for el in self.item_attachment_els(appt)]
