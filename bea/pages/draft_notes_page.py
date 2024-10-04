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

from bea.models.notes_and_appts.note import Note
from bea.pages.boa_pages import BoaPages
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class DraftNotesPage(BoaPages):

    DRAFTS_HEADING = By.XPATH, '//h1[contains(text(), "Draft Notes")]'
    NO_DRAFTS_MSG = By.ID, ''
    DRAFT_NOTE_ROW = By.XPATH, '//tbody/tr'

    def visible_draft_ids(self):
        self.when_present(self.DRAFTS_HEADING, utils.get_short_timeout())
        time.sleep(2)
        return [el.get_attribute('id').split('-')[-1] for el in self.elements(self.DRAFT_NOTE_ROW)]

    @staticmethod
    def draft_row_xpath(note):
        return f'//tr[@id="draft-note-{note.record_id}"]'

    def draft_row_loc(self, note):
        return By.XPATH, self.draft_row_xpath(note)

    def wait_for_draft_row(self, note):
        self.when_present(self.draft_row_loc(note), utils.get_short_timeout())

    def visible_draft_student(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.draft_row_xpath(note)}/td[1]'))

    def visible_draft_sid(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.draft_row_xpath(note)}/td[2]'))

    def visible_draft_subject(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.draft_row_xpath(note)}/td[3]'))

    def visible_draft_author(self, note, viewer):
        if viewer.is_admin:
            return self.el_text_if_exists((By.XPATH, f'{self.draft_row_xpath(note)}/td[4]'))
        else:
            return None

    def visible_draft_date(self, note, viewer):
        node = 5 if viewer.is_admin else 4
        return self.el_text_if_exists((By.XPATH, f'{self.draft_row_xpath(note)}/td[{node}]'))

    def draft_student_link_loc(self, note):
        return By.XPATH, f'{self.draft_row_xpath(note)}//a'

    def click_draft_student_link(self, note):
        app.logger.info(f'Clicking the student link for draft note {note.record_id}')
        self.wait_for_element_and_click(self.draft_student_link_loc(note))

    def draft_subject_button_loc(self, note):
        return By.XPATH, f'{self.draft_row_xpath(note)}/td[3]//button'

    def click_draft_subject(self, note):
        app.logger.info(f'Opening note edit modal for draft note {note.record_id}')
        self.wait_for_element_and_click(self.draft_subject_button_loc(note))

    def draft_delete_button_loc(self, note):
        return By.XPATH, f'{self.draft_row_xpath(note)}/td[last()]'

    def click_delete_draft(self, note):
        app.logger.info(f'Clicking delete button for draft note {note.record_id}')
        self.wait_for_element_and_click(self.draft_delete_button_loc(note))

    def delete_all_drafts(self):
        drafts = [Note({'record_id': record_id}) for record_id in self.visible_draft_ids()]
        for draft in drafts:
            self.click_delete_draft(draft)
            self.confirm_delete_or_discard()
            self.when_not_present(self.draft_row_loc(draft), utils.get_short_timeout())
