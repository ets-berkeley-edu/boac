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
import datetime
import re
import time

from bea.models.department import Department
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.student_page_timeline import StudentPageTimeline
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class StudentPageAdvisingNote(StudentPageTimeline, CreateNoteModal):

    # E-FORMS

    E_FORMS_BUTTON = (By.ID, 'timeline-tab-eForm')
    SHOW_HIDE_E_FORMS_BUTTON = (By.ID, 'toggle-expand-all-eForms')
    E_FORMS_DOWNLOAD_LINK = (By.ID, 'download-notes-link')

    def show_e_forms(self):
        app.logger.info('Checking eForms tab')
        self.wait_for_element_and_click(self.E_FORMS_BUTTON)
        if self.is_present(self.SHOW_HIDE_E_FORMS_BUTTON) and 'Show?' in self.element(
                self.SHOW_HIDE_E_FORMS_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_E_FORMS_BUTTON)

    # EXISTING NOTES

    NOTES_BUTTON = (By.ID, 'timeline-tab-note')
    FILTER_NOTES_BUTTON = (By.ID, 'toggle-my-notes-button')
    SHOW_HIDE_NOTES_BUTTON = (By.ID, 'timeline-tab-note-previous-messages')
    TOGGLE_ALL_NOTES_BUTTON = (By.ID, 'toggle-expand-all-notes')
    NOTES_EXPANDED_MSG = (By.XPATH, '//span[text()="Collapse all notes"]')
    NOTES_COLLAPSED_MSG = (By.XPATH, '//span[text()="Expand all notes"]')
    NOTES_DOWNLOAD_LINK = (By.ID, 'download-notes-link')
    NOTE_MSG_ROW = (By.XPATH, '//div[contains(@id,"timeline-tab-note-message")]')
    DRAFT_NOTE_FLAG = (By.XPATH, '//span[text()="Draft"]')

    def show_notes(self):
        app.logger.info('Checking notes tab')
        self.wait_for_element_and_click(self.NOTES_BUTTON)
        if self.is_present(self.SHOW_HIDE_NOTES_BUTTON) and 'Show' in self.element(self.SHOW_HIDE_NOTES_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_NOTES_BUTTON)

    def toggle_my_notes(self):
        self.wait_for_element_and_click(self.FILTER_NOTES_BUTTON)

    def expand_all_notes(self):
        app.logger.info('Expanding all notes')
        self.wait_for_element_and_click(self.TOGGLE_ALL_NOTES_BUTTON)
        self.when_visible(self.NOTES_EXPANDED_MSG, 2)

    def collapse_all_notes(self):
        app.logger.info('Collapsing all notes')
        self.wait_for_element_and_click(self.TOGGLE_ALL_NOTES_BUTTON)
        self.when_visible(self.NOTES_COLLAPSED_MSG, 2)

    TIMELINE_NOTES_QUERY_INPUT = (By.ID, 'timeline-notes-query-input')
    TIMELINE_NOTES_SPINNER = (By.ID, 'timeline-notes-spinner')

    def search_within_timeline_notes(self, query):
        app.logger.debug(f"Searching for '{query}'")
        self.wait_for_element_and_type(self.TIMELINE_NOTES_QUERY_INPUT, query)
        self.hit_enter()
        time.sleep(1)
        self.when_not_present(self.TIMELINE_NOTES_SPINNER, utils.get_short_timeout())

    def clear_timeline_notes_search(self):
        self.search_within_timeline_notes('')

    @staticmethod
    def expected_note_id_sort_order(notes):
        notes.sort(key=lambda n: ((n.set_date or n.created_date), n.record_id))
        notes.reverse()
        return list(map(lambda n: n.record_id, notes))

    # Collapsed note

    @staticmethod
    def note_loc(note_subject):
        return By.XPATH, f'//span[text()="{note_subject}"]/..'

    def visible_collapsed_note_ids(self):
        return self.visible_collapsed_item_ids('note')

    def visible_collapsed_note_data(self, note):
        subj_loc = By.ID, f'note-{note.record_id}-subject'
        subj = self.element(subj_loc).get_attribute('innerText') if self.is_present(subj_loc) else None
        category_loc = By.ID, f'note-{note.record_id}-category-closed'
        category = self.element(category_loc).text if self.is_present(category_loc) else None
        date_loc = By.ID, f'collapsed-note-{note.record_id}-created-at'
        date = self.element(date_loc).text.replace('Last updated on', '').strip() if self.is_present(date_loc) else None
        is_draft = self.is_present((By.ID, f'note-{note.record_id}-is-draft'))
        return {
            'subject': subj,
            'category': category,
            'created_date': date,
            'is_draft': is_draft,
        }

    # Expanded note

    def expand_note_by_subject(self, note_subject):
        self.wait_for_element_and_click(self.note_loc(note_subject))

    def visible_expanded_note_data(self, note):
        time.sleep(2)

        # The body text area contains formatting elements even without text, so account for that when getting the element's text
        body_loc = By.ID, f'note-{note.record_id}-message-open'
        if self.is_present(body_loc):
            text = self.element(body_loc).text
            body_text = '' if re.sub('/\W/', '', text).replace('&nbsp;', '') == '' else text.replace('\n', '').strip()
        else:
            body_text = ''

        advisor_loc = By.ID, f'note-{note.record_id}-author-name'
        advisor = self.element(advisor_loc).text if self.is_present(advisor_loc) else None

        advisor_dept_els = self.elements((By.XPATH, f"//span[contains(@id, 'note-{note.record_id}-author-dept-')]"))
        advisor_depts = list(map(lambda el: el.text, advisor_dept_els))
        advisor_depts.sort()

        advisor_role_loc = By.ID, f'note-{note.record_id}-author-role'
        advisor_role = self.element(advisor_role_loc) if self.is_present(advisor_role_loc) else None

        contact_type_loc = By.ID, f'note-{note.record_id}-contact-type'
        contact_type = self.element(contact_type_loc).text if self.is_present(contact_type_loc) else None

        created_loc = By.ID, f'expanded-note-{note.record_id}-created-at'
        if self.is_present(created_loc):
            text = self.element(created_loc).text.replace('Created on', '')
            created_date = re.sub('/\s+/', ' ', text).strip()
        else:
            created_date = None

        note_src_loc = By.XPATH, f"//tr[@id='permalink-note-{note.record_id}']//span[contains(text(), 'note imported from')]"
        note_src = self.element(note_src_loc).text if self.is_present(note_src_loc) else None

        permalink_loc = By.ID, f'advising-note-permalink-{note.record_id}'
        permalink_url = self.element(permalink_loc).get_attribute('href') if self.is_present(permalink_loc) else None

        set_date_loc = By.ID, f'expanded-note-{note.record_id}-set-date'
        if self.is_present(set_date_loc):
            text = self.element(set_date_loc).text
            set_date = re.sub('/\s+/', ' ', text).strip()
        else:
            set_date = None

        topic_els = self.elements((By.XPATH, f"//*[contains(@id, 'note-{note.record_id}-topic-')]"))
        topics = list(map(lambda el: el.text, topic_els))
        topics.sort()

        topic_remove_btn_els = self.elements((By.XPATH, f"//*[contains(@id, 'remove-note-{note.record_id}-topic-')]"))

        updated_loc = By.ID, f'expanded-note-{note.record_id}-updated-at'
        if self.is_present(updated_loc):
            text = self.element(updated_loc).text.replace('Last updated on', '')
            updated_date = re.sub('/\s+/', ' ', text).strip()
        else:
            updated_date = None

        return {
            'advisor': advisor,
            'advisor_role': advisor_role,
            'advisor_depts': advisor_depts,
            # TODO - attachments
            'attachments': [],
            'body': body_text,
            'contact_type': contact_type,
            'created_date': created_date or updated_date,
            'note_src': note_src,
            'permalink_url': permalink_url,
            'remove_topic_btns': topic_remove_btn_els,
            'set_date': set_date,
            'topics': topics,
            'updated_date': updated_date,
        }

    @staticmethod
    def e_form_data_loc(e_form, label):
        return By.XPATH, f"//tr[@id='permalink-eForm-{e_form.id}']//dt[text()='{label}']/following-sibling::dd"

    def visible_expanded_e_form_data(self, e_form):
        time.sleep(1)
        created_loc = By.ID, f'expanded-eForm-{e_form.id}-created-at'
        if self.is_present(created_loc):
            text = self.element(created_loc).text.replace('Created on', '')
            created_date = re.sub(r'/\s+ /', ' ', text).strip()
        else:
            created_date = None

        updated_loc = By.ID, f'expanded-eForm-{e_form.id}-updated-at'
        if self.is_present(updated_loc):
            text = self.element(updated_loc).text.replace('Last updated on', '')
            updated_date = re.sub(r'/\s+ /', ' ', text).strip()
        else:
            updated_date = None

        action_loc = By.XPATH, self.e_form_data_loc(e_form, 'Action')
        action = self.element(action_loc).text if self.is_present(action_loc) else None
        course_loc = By.XPATH, self.e_form_data_loc(e_form, 'Course')
        course = self.element(course_loc).text if self.is_present(course_loc) else None
        date_final_loc = By.XPATH, self.e_form_data_loc(e_form, 'Final Date & Time Stamp')
        date_final = self.element(date_final_loc).text if self.is_present(date_final_loc) else None
        date_init_loc = By.XPATH, self.e_form_data_loc(e_form, 'Date Initiated')
        date_init = self.element(date_init_loc).text if self.is_present(date_init_loc) else None
        form_id_loc = By.XPATH, self.e_form_data_loc(e_form, 'Form ID')
        form_id = self.element(form_id_loc).text if self.is_present(form_id_loc) else None
        status_loc = By.XPATH, self.e_form_data_loc(e_form, 'Form Status')
        status = self.element(status_loc).text if self.is_present(status_loc) else None
        term_loc = By.XPATH, self.e_form_data_loc(e_form, 'Term')
        term = self.element(term_loc).text if self.is_present(term_loc) else None
        return {
            'action': action,
            'course': course,
            'created_date': created_date,
            'date_final': date_final,
            'date_init': date_init,
            'form_id': form_id,
            'status': status,
            'term': term,
            'updated_date': updated_date,
        }

    def verify_note(self, note, viewer):
        app.logger.info(f'Verifying visible data for note ID {note.record_id}')

        # Verify data visible when note is collapsed
        self.when_visible(self.collapsed_item_loc(note), utils.get_medium_timeout())
        time.sleep(1)
        self.collapse_item(note)
        visible_data = self.visible_collapsed_note_data(note)
        date = note.set_date or note.updated_date
        expected_short_updated_date = self.expected_item_short_date_format(date)
        assert visible_data['subject'] == note.subject
        utils.assert_equivalence(visible_data['created_date'], expected_short_updated_date)

        # Verify data visible when note is expanded
        self.expand_item(note)
        visible_data.update(self.visible_expanded_note_data(note))
        app.logger.info(f"Expecting advisor '{visible_data['advisor']}' not to be empty")
        assert visible_data['advisor']
        if not note.source == TimelineRecordSource.EOP:
            app.logger.info(f"Expecting advisor role '{visible_data['advisor_role']}' not to be empty")
            app.logger.info(f"Expecting advisor depts '{visible_data['advisor_depts']}' not to be empty")
            assert visible_data['advisor_role']
            assert visible_data['advisor_depts']

        # Topics
        topics = []
        for topic in note.topics:
            name = topic.name.upper() if topic.__class__.__name__ == 'Topic' else topic.upper()
            topics.append(name)
        topics.sort()
        assert visible_data['topics'] == topics
        assert len(visible_data['remove_topic_btns']) == 0

        # Contact Type
        if note.contact_type:
            utils.assert_equivalence(visible_data['contact_type'], note.contact_type)
        else:
            app.logger.info(f"Expecting contact type '{visible_data['contact_type']}' to be empty")
            assert not visible_data['contact_type']

        # TODO - verify created_date, udpated_date

        expected_set_date = self.expected_item_short_date_format(note.set_date) if note.set_date else None
        utils.assert_equivalence(visible_data['set_date'], expected_set_date)

        # Body and attachments - private versus non-private
        if not note.body or (note.is_private and not viewer.is_admin and Department.ZCEEE not in viewer.depts):
            app.logger.info('Expecting body to be empty')
            assert not visible_data['body']
            assert not visible_data['attachments']
        else:
            app.logger.info('Expecting body not to be empty')
            assert visible_data['body']
            non_deleted_attachments = list(filter(lambda a: not a.deleted_at, note.attachments))
            file_names = list(map(lambda a: a.file_name, non_deleted_attachments))
            file_names.sort()
            visible_data['attachments'].sort()
            assert visible_data['attachments'] == file_names

    # EDIT / DELETE

    DRAFT_NOTE_WARNING = By.XPATH, '//div[text()=" You are editing a draft note. "]'

    @staticmethod
    def edit_note_button_loc(note):
        return By.ID, f'edit-note-{note.record_id}-button'

    @staticmethod
    def delete_note_button_loc(note):
        return By.ID, f'delete-note-button-{note.record_id}'

    def click_edit_note_button(self, note):
        app.logger.debug('Clicking the Edit Note button')
        self.wait_for_element_and_click(self.edit_note_button_loc(note))

    def save_note_edit(self, note):
        self.click_save_note_edit()
        self.when_not_present(self.EDIT_NOTE_SAVE_BUTTON, utils.get_short_timeout())
        self.when_visible(self.collapsed_item_loc(note), utils.get_short_timeout())
        note.updated_date = datetime.datetime.now()

    def edit_note_subject_and_save(self, note):
        app.logger.info(f'Changing note ID {note.record_id} subject to {note.subject}')
        self.expand_item(note)
        self.click_edit_note_button(note)
        self.enter_edit_note_subject(note)
        self.save_note_edit(note)

    def delete_note(self, note):
        app.logger.info(f'Deleting note {note.record_id}')
        self.expand_item(note)
        self.wait_for_element_and_click(self.delete_note_button_loc(note))
        self.confirm_delete_or_discard()
        note.deleted_date = datetime.datetime.now()

    # Save

    EDIT_NOTE_SAVE_BUTTON = By.XPATH, '//button[@id="save-note-button"]'

    def click_save_note_edit(self):
        app.logger.debug('Clicking the edit note Save button')
        self.wait_for_element_and_click(self.EDIT_NOTE_SAVE_BUTTON)

    # Cancel

    EDIT_NOTE_CANCEL_BUTTON = By.ID, 'cancel-edit-note-button'

    def click_cancel_note_edit(self):
        app.logger.debug('Clicking the edit note Cancel button')
        self.wait_for_element_and_click(self.EDIT_NOTE_CANCEL_BUTTON)

    # CREATE NOTE, STUDENT PROFILE

    NEW_NOTE_BUTTON = By.ID, 'new-note-button'

    def click_create_new_note(self):
        app.logger.debug('Clicking the New Note button')
        self.wait_for_element_and_click(self.NEW_NOTE_BUTTON)

    def create_note(self, note, topics, attachments):
        self.click_create_new_note()
        self.enter_new_note_subject(note)
        self.enter_note_body(note)
        if attachments:
            self.add_attachments_to_new_note(note, attachments)
        self.add_topics(note, topics)
        self.set_note_privacy(note)
        self.select_contact_type(note)
        self.enter_set_date(note)
        self.click_save_new_note()
        self.set_new_note_id(note)
