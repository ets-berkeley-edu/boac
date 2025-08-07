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

from flask import current_app as app
from selenium.webdriver.common.by import By

from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.student_page_timeline import StudentPageTimeline


class StudentPageEForm(StudentPageTimeline, CreateNoteModal):

    # E-FORMS

    E_FORMS_BUTTON = (By.ID, 'timeline-tab-eForm')
    SHOW_HIDE_E_FORMS_BUTTON = (By.ID, 'toggle-expand-all-eForms')
    E_FORM_MSG_ROW = By.XPATH, '//tr[contains(@id, "permalink-eForm-")]'

    def show_e_forms(self):
        app.logger.info('Checking eForms tab')
        self.wait_for_element_and_click(self.E_FORMS_BUTTON)
        if self.is_present(self.SHOW_HIDE_E_FORMS_BUTTON) and 'Show?' in self.element(
                self.SHOW_HIDE_E_FORMS_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_E_FORMS_BUTTON)

    @staticmethod
    def e_form_data_loc(e_form, label):
        return By.XPATH, f"//tr[@id='permalink-eForm-{e_form.record_id}']//dt[text()='{label}']/following-sibling::dd"

    def collapsed_e_form_date(self, e_form):
        date_loc = By.ID, f'collapsed-eForm-{e_form.record_id}-created-at'
        return self.el_text_if_exists(date_loc, 'Last updated on')

    def expanded_e_form_created_date(self, e_form):
        created_loc = By.ID, f'expanded-eForm-{e_form.record_id}-created-at'
        if self.is_present(created_loc):
            text = self.element(created_loc).text.replace('Created on', '')
            return re.sub(r'/\s+ /', ' ', text).strip()
        else:
            return None

    def expanded_e_form_updated_date(self, e_form):
        updated_loc = By.ID, f'expanded-eForm-{e_form.record_id}-updated-at'
        if self.is_present(updated_loc):
            text = self.element(updated_loc).text.replace('Last updated on', '')
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
