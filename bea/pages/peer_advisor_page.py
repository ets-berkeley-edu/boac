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

from bea.pages.peer_advising_note_table import PeerAdvisingNoteTable
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class PeerAdvisorPage(PeerAdvisingNoteTable):

    PEER_PAGE_HEADING = By.XPATH, '//h1[text()="Peer Advising Notes"]'

    def hit_peer_page_url(self):
        app.logger.info('Hitting peer advisor page')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/peer_advisor/home')

    def load_peer_page_admin_view(self, peer):
        app.logger.info(f'Loading peer advisor page for UID {peer.uid}')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/peer_advisor/{peer.uid}/home')
        self.when_visible(self.PEER_PAGE_HEADING, utils.get_short_timeout())

    # Note modal

    PEER_NEW_NOTE_BTN = By.ID, 'peer-advisor-create-note-button'

    def click_new_peer_note_button(self):
        app.logger.info('Clicking the New Note button')
        self.wait_for_element_and_click(self.PEER_NEW_NOTE_BTN)
        self.when_present(self.PEER_NOTE_STUDENT_INPUT, 2)

    # Adding student

    PEER_NOTE_STUDENT_INPUT = By.ID, 'find-student-autocomplete'
    REMOVE_ADDED_STUDENT_BTN = By.ID, 'clear-student-selection'

    @staticmethod
    def student_auto_suggest_option(student):
        return By.XPATH, f'//div[@role="option"]//div[contains(., "{student.sid}")]'

    @staticmethod
    def selected_student(student):
        return By.XPATH, f'//h4[contains(text(), "{student.sid}")]'

    def search_peer_note_student(self, student, search_term):
        self.hit_escape()
        # The lookup is flaky so give it a few tries
        tries = 3
        while tries > 0:
            try:
                tries -= 1
                self.wait_for_textbox_and_type_chars(self.PEER_NOTE_STUDENT_INPUT, search_term)
                self.when_present(self.student_auto_suggest_option(student), 3)
                break
            except TimeoutError:
                if tries == 0:
                    raise

    def search_peer_note_student_by_sid(self, student):
        self.search_peer_note_student(student, student.sid)

    def search_peer_note_student_by_name(self, student):
        self.search_peer_note_student(student, student.full_name)

    def search_peer_note_student_by_email(self, student):
        self.search_peer_note_student(student, student.email)

    def add_student_to_peer_note(self, student):
        app.logger.info(f'Looking up UID {student.uid}')
        self.search_peer_note_student_by_sid(student)
        self.wait_for_element_and_click(self.student_auto_suggest_option(student))
        self.when_present(self.selected_student(student), 3)

    def remove_student_from_peer_note(self, student):
        app.logger.info(f'Removing SID {student.sid} from peer note')
        self.wait_for_element_and_click(self.REMOVE_ADDED_STUDENT_BTN)
        self.when_not_present(self.selected_student(student), 3)

    # Student enrollments

    PEER_NOTE_SCHEDULE_TOGGLE = By.ID, 'show-hide-student-enrollments'
    PEER_NOTE_SCHEDULE_DIV = By.ID, 'student-enrollments'

    def expand_student_schedule(self):
        if self.is_present(self.PEER_NOTE_SCHEDULE_DIV):
            app.logger.info('Student schedule is already expanded')
        else:
            self.wait_for_element_and_click(self.PEER_NOTE_SCHEDULE_TOGGLE)
            self.when_present(self.PEER_NOTE_SCHEDULE_DIV, 2)

    def collapse_student_schedule(self):
        if self.is_present(self.PEER_NOTE_SCHEDULE_DIV):
            self.wait_for_element_and_click(self.PEER_NOTE_SCHEDULE_TOGGLE)
            self.when_not_present(self.PEER_NOTE_SCHEDULE_DIV, 2)
        else:
            app.logger.info('Student schedule is already collapsed')

    @staticmethod
    def term_table_xpath(term_name):
        return f'//th[text()="{term_name}"]/ancestor::table'

    def course_code(self, term_name, course_idx):
        return self.el_text_if_exists((By.XPATH, f'{self.term_table_xpath(term_name)}//tr[{course_idx + 1}]/td[1]'),
                                      'Waitlisted')

    def course_units(self, term_name, course_idx):
        return self.el_text_if_exists((By.XPATH, f'{self.term_table_xpath(term_name)}//tr[{course_idx + 1}]/td[2]'))

    # Create and verify note

    def save_and_wait_for_peer_note(self, note):
        self.click_save_new_note()
        self.set_new_note_id(note, note.student)
        self.wait_for_peer_note(note)

    def create_peer_note(self, note, attachments=None):
        self.add_student_to_peer_note(note.student)
        self.enter_note_body(note)
        self.add_topics(note)
        self.select_contact_type(note)
        if attachments:
            self.add_attachments_to_new_note(note, attachments)
        self.save_and_wait_for_peer_note(note)

    def verify_peer_note(self, note):
        self.wait_for_peer_note(note)
        utils.assert_equivalence(self.peer_note_student(note), note.student.full_name)
        utils.assert_equivalence(self.peer_note_body(note), note.body.strip())
        if note.topics:
            for topic in note.topics:
                utils.assert_actual_includes_expected(self.peer_note_topics(note), topic.name)
        else:
            utils.assert_equivalence(self.peer_note_topics(note), '—')
        utils.assert_equivalence(self.peer_note_date(note), note.date.strftime('%b %-d, %Y'))

        self.expand_peer_note(note)
        utils.assert_equivalence(self.expanded_note_advisor(note), note.advisor.full_name)
        if note.topics:
            for topic in note.topics:
                utils.assert_actual_includes_expected(self.expanded_note_topics(note), topic.name)
        if note.contact_type:
            utils.assert_equivalence(self.expanded_note_contact_type(note), note.contact_type)
        # TODO verify attachment pills
