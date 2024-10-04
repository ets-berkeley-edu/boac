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
import csv
import datetime
import itertools
import re
import time
from zipfile import ZipFile

from bea.models.department import Department
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.student_page_timeline import StudentPageTimeline
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class StudentPageAdvisingNote(StudentPageTimeline, CreateNoteModal):

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
        return {
            'subject': self.collapsed_note_subject(note),
            'category': self.collapsed_note_category(note),
            'created_date': self.collapsed_note_date(note),
            'is_draft': self.collapsed_note_is_draft(note),
        }

    def collapsed_note_subject(self, note):
        subj_loc = By.ID, f'note-{note.record_id}-subject'
        return self.element(subj_loc).get_attribute('innerText') if self.is_present(subj_loc) else None

    def collapsed_note_category(self, note):
        category_loc = By.ID, f'note-{note.record_id}-category-closed'
        return self.element(category_loc).text if self.is_present(category_loc) else None

    def collapsed_note_date(self, note):
        date_loc = By.ID, f'collapsed-note-{note.record_id}-created-at'
        return self.element(date_loc).text.replace('Last updated on', '').strip() if self.is_present(date_loc) else None

    def collapsed_note_is_draft(self, note):
        return self.is_present((By.ID, f'note-{note.record_id}-is-draft'))

    # Expanded note

    def expand_note_by_subject(self, note_subject):
        self.wait_for_element_and_click(self.note_loc(note_subject))

    def expanded_note_body(self, note):
        # Body may contain formatting elements even without text
        body_loc = By.ID, f'note-{note.record_id}-message-open'
        if self.is_present(body_loc):
            text = self.element(body_loc).text
            return '' if re.sub('/\W/', '', text).replace('&nbsp;', '') == '' else text.replace('\n', '').strip()
        else:
            return ''

    def expanded_note_advisor(self, note):
        advisor_loc = By.ID, f'note-{note.record_id}-author-name'
        return self.element(advisor_loc).text if self.is_present(advisor_loc) else None

    def expanded_note_advisor_depts(self, note):
        advisor_dept_els = self.elements((By.XPATH, f"//span[contains(@id, 'note-{note.record_id}-author-dept-')]"))
        advisor_depts = list(map(lambda el: el.text, advisor_dept_els))
        advisor_depts.sort()
        return advisor_depts

    def expanded_note_advisor_role(self, note):
        advisor_role_loc = By.ID, f'note-{note.record_id}-author-role'
        return self.element(advisor_role_loc) if self.is_present(advisor_role_loc) else None

    def expanded_note_contact_type(self, note):
        contact_type_loc = By.ID, f'note-{note.record_id}-contact-type'
        return self.element(contact_type_loc).text if self.is_present(contact_type_loc) else None

    def expanded_note_created_date(self, note):
        created_loc = By.ID, f'expanded-note-{note.record_id}-created-at'
        if self.is_present(created_loc):
            text = self.element(created_loc).text.replace('Created on', '')
            return re.sub('/\s+/', ' ', text).strip()
        else:
            return None

    def expanded_note_source(self, note):
        note_src_loc = By.XPATH, f"//tr[@id='permalink-note-{note.record_id}']//span[contains(text(), 'note imported from')]"
        return self.element(note_src_loc).text if self.is_present(note_src_loc) else None

    def expanded_note_permalink_url(self, note):
        permalink_loc = By.ID, f'advising-note-permalink-{note.record_id}'
        return self.element(permalink_loc).get_attribute('href') if self.is_present(permalink_loc) else None

    def expanded_note_set_date(self, note):
        set_date_loc = By.ID, f'expanded-note-{note.record_id}-set-date'
        if self.is_present(set_date_loc):
            text = self.element(set_date_loc).text
            return re.sub('/\s+/', ' ', text).strip()
        else:
            return None

    def expanded_note_topics(self, note):
        topic_els = self.elements((By.XPATH, f"//*[contains(@id, 'note-{note.record_id}-topic-')]"))
        topics = list(map(lambda el: el.text, topic_els))
        topics.sort()
        return topics

    def expanded_note_topic_remove_btn_els(self, note):
        return self.elements((By.XPATH, f"//*[contains(@id, 'remove-note-{note.record_id}-topic-')]"))

    def expanded_note_updated_date(self, note):
        updated_loc = By.ID, f'expanded-note-{note.record_id}-updated-at'
        if self.is_present(updated_loc):
            text = self.element(updated_loc).text.replace('Last updated on', '')
            return re.sub('/\s+/', ' ', text).strip()
        else:
            return None

    def expanded_note_attachments(self, note):
        attachment_names = [el.text.strip().lower() for el in self.item_attachment_els(note)]
        attachment_names.sort()
        return attachment_names

    def verify_note(self, note, viewer):
        app.logger.info(f'Verifying visible data for note ID {note.record_id}')

        # Collapsed

        self.when_visible(self.collapsed_item_loc(note), utils.get_medium_timeout())
        time.sleep(1)
        self.collapse_item(note)
        date = note.set_date or note.updated_date
        expected_short_updated_date = self.expected_item_short_date_format(date)
        utils.assert_equivalence(self.collapsed_note_subject(note), note.subject)
        utils.assert_equivalence(self.collapsed_note_date(note), expected_short_updated_date)

        # Expanded

        self.expand_item(note)
        utils.assert_existence(self.expanded_note_advisor(note))
        if not note.source == TimelineRecordSource.EOP:
            utils.assert_existence(self.expanded_note_advisor_role(note))
            utils.assert_existence(self.expanded_note_advisor_depts(note))

        topics = []
        for topic in note.topics:
            name = topic.name.upper() if topic.__class__.__name__ == 'Topic' else topic.upper()
            topics.append(name)
        topics.sort()
        utils.assert_equivalence(self.expanded_note_topics(note), topics)
        utils.assert_equivalence(len(self.expanded_note_topic_remove_btn_els(note)), 0)

        utils.assert_equivalence(self.expanded_note_contact_type(note), note.contact_type)

        # TODO - verify created_date, updated_date

        expected_set_date = self.expected_item_short_date_format(note.set_date) if note.set_date else None
        utils.assert_equivalence(self.expanded_note_set_date(note), expected_set_date)

        attachments = [a.file_name for a in note.attachments if not a.deleted_at]
        attachments.sort()
        visible_attachments = self.expanded_note_attachments(note)
        visible_attachments.sort()

        visible_body = self.expanded_note_body(note)
        if note.is_private:
            if viewer.is_admin or Department.ZCEEE in viewer.depts:
                utils.assert_equivalence(visible_body, note.body)
                utils.assert_equivalence(visible_attachments, attachments)
            else:
                utils.assert_non_existence(visible_body)
                utils.assert_non_existence(visible_attachments)
        else:
            utils.assert_equivalence(visible_body, note.body)
            utils.assert_equivalence(visible_attachments, attachments)

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

    @staticmethod
    def e_form_data_loc(e_form, label):
        return By.XPATH, f"//tr[@id='permalink-eForm-{e_form.id}']//dt[text()='{label}']/following-sibling::dd"

    def expanded_e_form_created_date(self, e_form):
        created_loc = By.ID, f'expanded-eForm-{e_form.id}-created-at'
        if self.is_present(created_loc):
            text = self.element(created_loc).text.replace('Created on', '')
            return re.sub(r'/\s+ /', ' ', text).strip()
        else:
            return None

    def expanded_e_form_updated_date(self, e_form):
        updated_loc = By.ID, f'expanded-eForm-{e_form.id}-updated-at'
        if self.is_present(updated_loc):
            text = self.element(updated_loc).text.replace('Last updated on', '')
            return re.sub(r'/\s+ /', ' ', text).strip()
        else:
            return None

    def expanded_e_form_action(self, e_form):
        return self.el_text_if_exists(By.XPATH, self.e_form_data_loc(e_form, 'Action'))

    def expanded_e_form_course(self, e_form):
        return self.el_text_if_exists(By.XPATH, self.e_form_data_loc(e_form, 'Course'))

    def expanded_e_form_date_final(self, e_form):
        return self.el_text_if_exists(By.XPATH, self.e_form_data_loc(e_form, 'Final Date & Time Stamp'))

    def expanded_e_form_date_init(self, e_form):
        return self.el_text_if_exists(By.XPATH, self.e_form_data_loc(e_form, 'Date Initiated'))

    def expanded_e_form_id(self, e_form):
        return self.el_text_if_exists(By.XPATH, self.e_form_data_loc(e_form, 'Form ID'))

    def expanded_e_form_status(self, e_form):
        return self.el_text_if_exists(By.XPATH, self.e_form_data_loc(e_form, 'Form Status'))

    def expanded_e_form_term(self, e_form):
        return self.el_text_if_exists(By.XPATH, self.e_form_data_loc(e_form, 'Term'))

    def visible_expanded_note_data(self, note):
        time.sleep(2)
        return {
            'advisor': self.expanded_note_advisor(note),
            'advisor_role': self.expanded_note_advisor_role(note),
            'advisor_depts': self.expanded_note_advisor_depts(note),
            'attachments': self.expanded_note_attachments(note),
            'body': self.expanded_note_body(note),
            'contact_type': self.expanded_note_contact_type(note),
            'created_date': self.expanded_note_created_date(note) or self.expanded_note_updated_date(note),
            'note_src': self.expanded_note_source(note),
            'permalink_url': self.expanded_note_permalink_url(note),
            'remove_topic_btns': self.expanded_note_topic_remove_btn_els(note),
            'set_date': self.expanded_note_set_date(note),
            'topics': self.expanded_note_topics(note),
            'updated_date': self.expanded_note_updated_date(note),
        }

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

    # NOTE / E-FORM DOWNLOADS

    @staticmethod
    def export_zip_file_name(student, record_type_str):
        timestamp = datetime.datetime.now().strftime('%Y%m%d')
        return f'advising_{record_type_str}_{student.first_name.lower()}_{student.last_name.lower()}_{timestamp}.zip'

    def export_csv_file_name(self, student, record_type_str):
        return self.export_zip_file_name(student, record_type_str).replace('zip', 'csv')

    @staticmethod
    def downloaded_zip_file_name_list(zip_name):
        zip_path = f'{utils.default_download_dir()}/{zip_name}'
        with ZipFile(zip_path, 'r') as zip_file:
            return zip_file.namelist()

    # Notes

    def notes_export_zip_file_name(self, student):
        return self.export_zip_file_name(student, 'notes')

    def notes_export_csv_file_name(self, student):
        return self.export_csv_file_name(student, 'notes')

    def download_notes(self, student):
        app.logger.info(f'Downloading notes for UID {student.uid}')
        utils.prepare_download_dir()
        self.wait_for_element_and_click(self.NOTES_DOWNLOAD_LINK)
        return utils.wait_for_export_csv()

    def note_export_file_names(self, student):
        return self.downloaded_zip_file_name_list(self.notes_export_zip_file_name(student))

    def expected_note_export_file_names(self, student, notes, downloader):
        names = [self.notes_export_csv_file_name(student)]

        attachments = []
        for note in notes:
            if not (note.__class__.__name__ == 'TimelineEForm') or (
                    note.is_private and not downloader.is_admin and Department.ZCEEE not in downloader.depts):
                attachments.extend([attach for attach in note.attachments if not attach.deleted_at])

        # Account for duplicate attachment file names
        for key, result in itertools.groupby(attachments, key=lambda att: att.file_name):
            parts = result[0].file_name.rpartition('.')
            for dupe_attach in result:
                idx = result.index(dupe_attach)
                names.append(f"{parts[0]}{'' if idx == 0 else idx}.{parts[-1]}")
        return names

    def parse_note_export_csv_to_table(self, student):
        with ZipFile(self.notes_export_zip_file_name(student)) as zip_file:
            with zip_file.read(self.notes_export_csv_file_name(student)) as csv_file:
                return csv.DictReader(open(csv_file))

    @staticmethod
    def verify_note_in_export_csv(student, note, csv_reader, downloader):
        rows = list(csv_reader)
        for row in rows:
            try:
                assert row['date_created'] == note.created_date.strftime('%Y-%m-%d')
                assert row['student_sid'] == int(student.sid)
                assert row['student_name'] == student.full_name
                if note.advisor and note.advisor.uid != 'UCBCONVERSION':
                    assert row['author_uid'] == int(note.advisor.uid)
                if note.subject:
                    assert row['subject'] == note.subject
                if (note.is_private and not downloader.is_admin and Department.ZCEEE not in downloader.depts) or not note.body:
                    assert not row['body']

                exp_tops = [topic.name.lower() if topic.__class__.__name__ == 'Topic' else topic for topic in note.topics]
                exp_tops.sort()
                act_tops = [topic.strip().lower() for topic in row['topics'].split(';')] if row['topics'] else []
                act_tops.sort()
                assert act_tops == exp_tops

                if (note.is_private and not downloader.is_admin and Department.ZCEEE not in downloader.depts) or not note.attachments:
                    exp_att = []
                else:
                    exp_att = [a.file_name for a in note.attachments]
                    exp_att.sort()
                act_att = [att.strip() for att in row['attachments'].split(';')] if row['attachments'] else []
                act_att.sort()
                assert exp_att == act_att

                return True

            except AssertionError:
                if row == rows[-1]:
                    return False

    # E-Forms

    def e_forms_export_zip_file_name(self, student):
        return self.export_zip_file_name(student, 'eForms')

    def e_forms_export_csv_file_name(self, student):
        return self.export_csv_file_name(student, 'eForms')

    def download_e_forms(self, student):
        app.logger.info(f'Downloading eForms for UID {student.uid}')
        self.download_file(self.E_FORMS_DOWNLOAD_LINK, self.e_forms_export_zip_file_name(student))

    def e_form_export_file_names(self, student):
        return self.downloaded_zip_file_name_list(self.e_forms_export_zip_file_name(student))

    def expected_e_form_export_file_names(self, student):
        return [self.e_forms_export_csv_file_name(student)]

    def parse_e_forms_export_csv_to_table(self, student):
        with ZipFile(self.e_forms_export_zip_file_name(student)) as zip_file:
            with zip_file.read(self.e_forms_export_csv_file_name(student)) as csv_file:
                return csv.DictReader(open(csv_file))

    @staticmethod
    def verify_e_form_in_export_csv(student, e_form, csv_reader):
        rows = list(csv_reader)
        for row in rows:
            try:
                assert row['created_date'] == e_form.created_date.strftime('%Y-%m-%d')
                assert row['student_sid'] == int(student.sid)
                assert row['student_name'] == student.full_name
                assert row['eform_id'] == e_form.form_id
                if e_form.action:
                    assert row['late_change_request_action'] == e_form.action
                if e_form.grading_basis:
                    assert row['grading_basis'] == e_form.grading_basis
                if e_form.requested_grading_basis:
                    assert row['requested_grading_basis'] == e_form.requested_grading_basis
                if e_form.units_taken:
                    assert row['units_taken'] == e_form.units_taken
                if e_form.requested_units_taken:
                    assert row['requested_units_taken'] == e_form.requested_units_taken
                if e_form.status:
                    assert row['late_change_request_status'] == e_form.status
                if e_form.term:
                    assert row['late_change_request_term'] == e_form.term
                assert row['late_change_request_course'] == e_form.course
                return True
            except AssertionError:
                if row == rows[-1]:
                    return False
