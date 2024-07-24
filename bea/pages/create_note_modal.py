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

from datetime import datetime
import time

from bea.models.department import Department
from bea.pages.boa_pages import BoaPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CreateNoteModal(BoaPages):

    # DRAFT NOTE

    SAVE_AS_DRAFT_BUTTON = By.ID, 'save-as-draft-button'
    UPDATE_DRAFT_BUTTON = By.XPATH, '//button[text()=" Update Draft "]'
    EDIT_DRAFT_HEADING = By.XPATH, '//h3[text()=" Edit Draft Note "]'

    def click_save_as_draft(self):
        app.logger.info('Clicking the save-as-draft button')
        self.wait_for_element_and_click(self.SAVE_AS_DRAFT_BUTTON)
        self.when_not_present(self.SAVE_AS_DRAFT_BUTTON, utils.get_medium_timeout())

    def click_update_note_draft(self):
        app.logger.info('Clicking the update draft button')
        self.wait_for_element_and_click(self.UPDATE_DRAFT_BUTTON)

    # CREATE NOTE, SHARED ELEMENTS

    # Subject

    NEW_NOTE_SUBJECT_INPUT = By.ID, 'create-note-subject'

    def enter_new_note_subject(self, note):
        app.logger.info(f'Entering new note subject {note.subject}')
        self.wait_for_textbox_and_type(self.NEW_NOTE_SUBJECT_INPUT, note.subject)

    EDIT_NOTE_SUBJECT_INPUT = By.ID, 'edit-note-subject'
    SUBJ_REQUIRED_MSG = By.XPATH, '//span[text()="Subject is required"]'

    def enter_edit_note_subject(self, note):
        app.logger.info(f'Entering edited note subject {note.subject}')
        self.wait_for_textbox_and_type(self.EDIT_NOTE_SUBJECT_INPUT, note.subject)

    # Body

    NOTE_BODY_TEXT_AREA = By.XPATH, '(//div[@role="textbox"])[2]'

    def wait_for_note_body_editor(self):
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_element_located(self.NOTE_BODY_TEXT_AREA))

    def enter_note_body(self, note):
        app.logger.info(f'Entering note body {note.body}')
        self.wait_for_note_body_editor()
        self.wait_for_textbox_and_type(self.NOTE_BODY_TEXT_AREA, note.body)

    # Topics

    TOPIC_INPUT = By.ID, 'add-note-topic'
    ADD_TOPIC_SELECT = By.ID, 'add-topic-select-list'
    TOPIC_OPTION = By.XPATH, '//select[@id="add-topic-select-list"]/option'
    TOPIC_REMOVE_BUTTON = By.XPATH, '//li[contains(@id, "remove-note-")]'

    def topic_options(self):
        self.wait_for_element_and_click(self.ADD_TOPIC_SELECT)
        Wait(self.driver, 1).until(ec.presence_of_all_elements_located(self.TOPIC_OPTION))
        time.sleep(utils.get_click_sleep())
        return [el.get_attribute('value') for el in self.elements(self.TOPIC_OPTION) if el.get_attribute('value')]

    @staticmethod
    def new_note_unsaved_topic_pill(topic):
        return By.XPATH, f'//li[contains(@id, \"-topic\")][contains(., \"{topic.name}\")]'

    @staticmethod
    def topic_pill(note, topic):
        return By.XPATH, f'//li[contains(@id, \"note-{note.record_id}-topic\")][contains(., \"{topic.name}\")]'

    @staticmethod
    def new_note_unsaved_topic_remove_btn(topic):
        return By.XPATH, f'//li[contains(@id, \"-topic\")][contains(., \"{topic.name}\")]//button'

    @staticmethod
    def topic_remove_button(note, topic):
        return By.XPATH, f'//li[contains(@id, \"note-{note.record_id}-topic\")][contains(., \"{topic.name}\")]//button'

    def add_topics(self, note, topics):
        for topic in topics:
            app.logger.info(f'Adding topic {topic.name}')
            self.wait_for_select_and_click_option(self.ADD_TOPIC_SELECT, topic.name)
            if note.record_id:
                Wait(self.driver, utils.get_short_timeout()).until(
                    ec.visibility_of_element_located(self.topic_pill(note, topic)),
                )
            else:
                Wait(self.driver, utils.get_short_timeout()).until(
                    ec.visibility_of_element_located(self.new_note_unsaved_topic_pill(topic)),
                )
        note.topics += topics

    def remove_topics(self, note, topics):
        current_topics = list(map(lambda t: t.name, note.topics))
        for topic in topics:
            app.logger.info(f'Removing topic {topic.name}')
            if note.record_id:
                self.wait_for_element_and_click(self.topic_remove_button(note, topic))
                self.when_not_visible(self.topic_pill(note, topic), utils.get_short_timeout())
            else:
                self.wait_for_element_and_click(self.new_note_unsaved_topic_remove_btn(topic))
                self.when_not_visible(self.new_note_unsaved_topic_pill(topic), utils.get_short_timeout())
            if topic.name in current_topics:
                matching_topic = next(filter(lambda t: t.name == topic.name, note.topics))
                note.topics.remove(matching_topic)

    # Attachments

    NEW_NOTE_ATTACH_INPUT = By.XPATH, '//div[@id="new-note-modal-container"]//input[@type="file"]'
    NOTE_ATTACHMENT_SIZE_MSG = By.XPATH, '//div[contains(text(),"Attachments are limited to 20 MB in size.")]'
    NOTE_DUPE_ATTACHMENT_MSG = By.XPATH, '//div[contains(text(),"Another attachment has the name")]'

    @staticmethod
    def new_note_attachment_delete_button(attachment):
        return By.XPATH, f'//button[@aria-label="Remove attachment {attachment.file_name}"]'

    def enter_new_note_attachments(self, file_string):
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_element_located(self.NEW_NOTE_ATTACH_INPUT))
        self.element(self.NEW_NOTE_ATTACH_INPUT).send_keys(file_string)

    def add_attachments_to_new_note(self, note, attachments):
        files = list(map(lambda a: f'{utils.attachments_dir()}/{a.file_name}', attachments))
        files = '\n'.join(files)
        app.logger.info(f'Adding attachments to an unsaved note: {files}')
        self.enter_new_note_attachments(files)
        self.when_visible(self.new_note_attachment_delete_button(attachments[-1]), utils.get_medium_timeout())
        time.sleep(utils.get_click_sleep())
        note.attachments += attachments

    def remove_attachments_from_new_note(self, note, attachments):
        for a in attachments:
            app.logger.info(f'Removing attachment {a.file_name} from an unsaved note')
            self.wait_for_element_and_click(self.new_note_attachment_delete_button(a))
            self.when_not_visible(self.new_note_attachment_delete_button(a), utils.get_short_timeout())
            note.attachments.remove(a)
            note.updated_date = datetime.now()

    SORRY_NO_ATTACHMENT_MSG = By.XPATH, '//body[text()="Sorry, attachment not available."]'

    @staticmethod
    def existing_note_attachment_input(note):
        return By.XPATH, f'//div[@id="note-{note.record_id}-attachment-dropzone"]/input'

    @staticmethod
    def existing_note_attachment_delete_button(note, attachment):
        return By.XPATH, f'//div[@id=\"note-{note.record_id}-outer\"]//li[contains(., \"{attachment.file_name}\")]//button'

    def add_attachments_to_existing_note(self, note, attachments):
        for a in attachments:
            app.logger.info(f'Adding attachment {a.file_name} to note ID {note.record_id}')
            Wait(self.driver, utils.get_short_timeout()).until(
                ec.presence_of_element_located(self.existing_note_attachment_input(note)),
            )
            self.element(self.existing_note_attachment_input(note)).send_keys(
                f'{utils.attachments_dir()}/{a.file_name}')
            self.when_visible(self.existing_note_attachment_delete_button(note, a), utils.get_medium_timeout())
            time.sleep(utils.get_click_sleep())
            note.updated_date = datetime.now()
            note.attachments.append(a)

    def remove_attachments_from_existing_note(self, note, attachments):
        for a in attachments:
            app.logger.info(f'Removing attachment {a.file_name} from note ID {note.record_id}')
            self.wait_for_element_and_click(self.existing_note_attachment_delete_button(note, a))
            self.confirm_delete_or_discard()
            self.when_not_visible(self.existing_note_attachment_delete_button(note, a), utils.get_short_timeout())
            note.attachments.remove(a)
            a.deleted_at = datetime.now()
            note.updated_date = datetime.now()

    # CE3 restricted

    UNIVERSAL_RADIO = By.XPATH, '//input[@id="note-is-not-private-radio-button"]/ancestor::div[contains(@class, "custom-radio")]'
    PRIVATE_RADIO = By.XPATH, '//input[@id="note-is-private-radio-button"]/ancestor::div[contains(@class, "custom-radio")]'

    def set_note_privacy(self, note):
        if note.advisor.depts and Department.ZCEEE.value['name'] in note.advisor.depts:
            if note.is_private:
                app.logger.info('Setting note to private')
                self.wait_for_element_and_click(self.PRIVATE_RADIO)
            else:
                app.logger.info('Setting note to non-private')
                self.wait_for_element_and_click(self.UNIVERSAL_RADIO)
        else:
            app.logger.info(f'Advisor not with CE3, so privacy defaults to {note.is_private}')

    # Contact type

    @staticmethod
    def contact_type(note):
        if note.contact_type:
            return By.XPATH, f'//input[@type="radio"][@value="{note.contact_type}"]'
        else:
            return By.XPATH, '//input[@id="contact-option-none-radio-button"]'

    def select_contact_type(self, note):
        app.logger.info(f'Selecting contact type {note.contact_type}')
        self.wait_for_page_and_click_js(self.contact_type(note))

    # Set date

    SET_DATE_INPUT = By.ID, 'manually-set-date-input'

    def enter_set_date(self, note):
        app.logger.info(f'Entering note set date {note.set_date}')
        date = note.set_date and note.set_date.strftime('%m/%d/%Y') or ''
        self.wait_for_textbox_and_type(self.SET_DATE_INPUT, date)
        time.sleep(5)

    # Save

    NEW_NOTE_SAVE_BUTTON = By.ID, 'create-note-button'

    def click_save_new_note(self):
        app.logger.info('Clicking the new note Save button')
        self.wait_for_element_and_click(self.NEW_NOTE_SAVE_BUTTON)

    def set_new_note_id(self, note):
        start_time = datetime.now()
        tries = 0
        max_tries = 15
        while tries <= max_tries:
            tries += 1
            try:
                results = boa_utils.get_note_ids_by_subject(note.subject)
                assert len(results) > 0
                note.record_id = f'{results[0]}'
                break
            except AssertionError:
                if tries == max_tries:
                    raise
                else:
                    time.sleep(1)
        app.logger.info(f'Note ID is {note.record_id}')
        end_time = datetime.now()
        app.logger.info(f'Note was created in {(end_time - start_time).seconds} seconds')
        self.when_not_present(self.NEW_NOTE_SUBJECT_INPUT, utils.get_short_timeout())
        note.created_date = datetime.now()
        note.updated_date = datetime.now()
        return note.record_id

    # Cancel

    NEW_NOTE_CANCEL_BUTTON = By.ID, 'create-note-cancel'

    def click_cancel_new_note(self):
        self.wait_for_element_and_click(self.NEW_NOTE_CANCEL_BUTTON)
