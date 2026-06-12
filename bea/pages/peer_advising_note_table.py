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
import datetime
import time

from flask import current_app as app
from selenium.webdriver.common.by import By

from bea.pages.student_page_advising_note import StudentPageAdvisingNote
from bea.test_utils import utils


class PeerAdvisingNoteTable(StudentPageAdvisingNote):

    PEER_NOTE_TABLE = By.ID, 'notes-for-peer-advisor-view'
    SHOW_MORE_NOTES_BTN = By.ID, 'fetch-more-notes'

    def visible_peer_note_ids(self):
        els = self.elements((By.XPATH, '//button[contains(@id, "open-peer-advising-")]'))
        return [el.get_dom_attribute('id').split('-')[-1] for el in els]

    def show_more_peer_notes(self):
        self.wait_for_element_and_click(self.SHOW_MORE_NOTES_BTN)
        time.sleep(5)

    @staticmethod
    def peer_note_row_xpath(note):
        return f'//article[@id="peer-advisor-note-{note.record_id}"]'

    def peer_note_student_xpath(self, note):
        return f'//div[@id="peer-advisor-note-{note.record_id}-student"]'

    def peer_note_body_xpath(self, note):
        return f'//div[@id="peer-advisor-note-{note.record_id}-details"]'

    def peer_note_row(self, note):
        return By.XPATH, self.peer_note_row_xpath(note)

    def wait_for_peer_note(self, note):
        self.when_present(self.peer_note_row(note), utils.get_medium_timeout())

    def peer_note_student(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_note_row_xpath(note)}{self.peer_note_student_xpath(note)}'))

    def peer_note_body(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_note_row_xpath(note)}{self.peer_note_body_xpath(note)}'), 'Has attachment(s)')

    def peer_note_date(self, note):
        return self.el_text_if_exists(
            (By.XPATH, f'{self.peer_note_row_xpath(note)}//div[contains(@id, "updated-at")]'),
            text_to_remove='Last updated on')

    @staticmethod
    def peer_manager_note_student_link(note):
        return By.ID, f'note-{note.record_id}-link-to-student'

    def click_peer_manager_note_student_link(self, note):
        app.logger.info(f'Clicking link to UID {note.student.uid} on note {note.record_id}')
        self.wait_for_element_and_click(self.peer_manager_note_student_link(note))

    def peer_manager_note_date(self, note):
        return self.el_text_if_exists(
            (By.XPATH, f'{self.peer_note_row_xpath(note)}//div[contains(@id, "updated-at")]'),
            text_to_remove='Last updated on')

    @staticmethod
    def peer_note_date_format(note):
        if datetime.datetime.now().strftime('%Y') == note.updated_date.strftime('%Y'):
            return note.updated_date.strftime('%b %-d')
        else:
            return note.updated_date.strftime('%b %-d, %Y')

    def expand_peer_note(self, note):
        app.logger.info(f'Expanding note {note.record_id}')
        self.wait_for_element_and_click((By.ID, f'open-peer-advising-{note.record_id}'))
        self.when_visible((By.ID, f'note-{note.record_id}-body'), 2)
        time.sleep(utils.get_click_sleep())

    # EDIT / DELETE

    PEER_NOTE_EDIT_SAVE_BTN = By.ID, 'save-note-button'

    @staticmethod
    def peer_note_edit_button(note):
        return By.ID, f'edit-note-{note.record_id}-button'

    @staticmethod
    def peer_note_delete_button(note):
        return By.ID, f'delete-note-button-{note.record_id}'

    def is_peer_note_edit_save_btn_enabled(self):
        return self.element(self.PEER_NOTE_EDIT_SAVE_BTN).is_enabled()

    def click_peer_note_edit_button(self, note):
        self.wait_for_element_and_click(self.peer_note_edit_button(note))

    def save_peer_note_edit(self, note):
        app.logger.info(f'Saving edit for peer note {note.record_id}')
        self.wait_for_element_and_click(self.PEER_NOTE_EDIT_SAVE_BTN)
        self.when_not_present(self.PEER_NOTE_EDIT_SAVE_BTN, utils.get_short_timeout())

    def delete_peer_note(self, note):
        app.logger.info(f'Deleting peer note {note.record_id}')
        self.wait_for_element_and_click(self.peer_note_delete_button(note))
        self.confirm_delete_or_discard()
        note.deleted_date = datetime.datetime.now()
