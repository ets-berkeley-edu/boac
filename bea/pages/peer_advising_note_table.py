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

from bea.pages.student_page_advising_note import StudentPageAdvisingNote
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class PeerAdvisingNoteTable(StudentPageAdvisingNote):

    PEER_NOTE_TABLE = By.ID, 'notes-for-peer-advisor-view'
    PEER_NOTE_NO_RESULTS = By.ID, 'peer-advisor-no-notes'

    def visible_peer_note_ids(self):
        els = self.elements((By.XPATH, '//button[contains(@id, "open-peer-advising-")]'))
        ids = [el.get_dom_attribute('id').split('-')[-1] for el in els]
        return ids

    @staticmethod
    def peer_note_row_xpath(note):
        return f'//button[@id="open-peer-advising-{note.record_id}"]/ancestor::tr'

    def peer_note_row(self, note):
        return By.XPATH, self.peer_note_row_xpath(note)

    def wait_for_peer_note(self, note):
        self.when_visible(self.peer_note_row(note), utils.get_short_timeout())

    def peer_note_student(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_note_row_xpath(note)}/td[1]'))

    def peer_note_body(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_note_row_xpath(note)}/td[2]'), 'Has attachment(s)')

    def peer_note_topics(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_note_row_xpath(note)}/td[3]'))

    def peer_note_date(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_note_row_xpath(note)}/td[4]'))

    @staticmethod
    def peer_manager_note_student_link(note):
        return By.ID, f'link-to-student-{note.student.sid}'

    def click_peer_manager_note_student_link(self, note):
        app.logger.info(f'Clicking link to UID {note.student.uid} on note {note.record_id}')
        self.wait_for_element_and_click(self.peer_manager_note_student_link(note))

    def peer_manager_note_date(self, note):
        return self.el_text_if_exists((By.XPATH, f'{self.peer_note_row_xpath(note)}/td[3]'))

    @staticmethod
    def peer_note_date_format(note):
        return note.updated_date.strftime('%b %-d, %Y')

    def expand_peer_note(self, note):
        app.logger.info(f'Expanding note {note.record_id}')
        self.wait_for_element_and_click((By.ID, f'open-peer-advising-{note.record_id}'))
        self.when_visible((By.ID, f'note-{note.record_id}-body'), 2)
        time.sleep(utils.get_click_sleep())

    def close_peer_note(self, note):
        app.logger.info(f'Closing note {note.record_id}')
        self.wait_for_element_and_click((By.ID, f'show-note-{note.record_id}-details'))
        self.when_not_present((By.ID, f'note-{note.record_id}-body'), 2)
