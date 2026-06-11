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
import csv
import datetime
import itertools
import re
import time
import zipfile
from io import TextIOWrapper

from flask import current_app as app
from selenium.webdriver.common.by import By

from bea.models.advisor_role import PeerAdvisingRole
from bea.models.department import Department
from bea.models.notes_and_appts.timeline_e_form import TimelineEForm
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.student_page_timeline import StudentPageTimeline
from bea.test_utils import boa_utils, utils


class StudentPageAdvisingNote(StudentPageTimeline, CreateNoteModal):
    # EXISTING NOTES

    NOTES_BUTTON = (By.ID, 'timeline-tab-note')
    FILTER_NOTES_BUTTON = (By.ID, 'show-items-created-by-me')
    SHOW_HIDE_NOTES_BUTTON = (By.ID, 'timeline-tab-note-previous-messages')
    TOGGLE_ALL_NOTES_BUTTON = (By.ID, 'toggle-expand-all-notes')
    NOTES_DOWNLOAD_LINK = (By.ID, 'download-notes-link')
    NOTE_MSG_ROW = (By.XPATH, '//div[contains(@id,"timeline-tab-note-message")]')
    DRAFT_NOTE_FLAG = (By.XPATH, '//span[text()="Draft"]')

    def show_notes(self):
        app.logger.info('Checking notes tab')
        self.when_present(self.TIMELINE_TABLE, utils.get_short_timeout())
        if self.is_present(self.NOTES_BUTTON):
            self.wait_for_element_and_click(self.NOTES_BUTTON)
        if self.is_present(self.SHOW_HIDE_NOTES_BUTTON) and 'Show' in self.element(self.SHOW_HIDE_NOTES_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_NOTES_BUTTON)

    def toggle_my_notes(self):
        self.wait_for_element_and_click(self.FILTER_NOTES_BUTTON)
        time.sleep(1)

    def hit_note_permalink(self, note, url):
        app.logger.info(f'Hitting permalink for note {note.record_id} at {url}')
        self.driver.get(url)
        self.wait_for_spinner()
        self.when_present((By.ID, f'note-{note.record_id}-is-open'), utils.get_short_timeout())

    TIMELINE_NOTES_QUERY_INPUT = (By.ID, 'timeline-notes-query-input')
    TIMELINE_NOTES_SPINNER = (By.ID, 'timeline-notes-spinner')

    def search_within_timeline_notes(self, query):
        app.logger.info(f"Searching for '{query}'")
        self.scroll_to_top()
        self.wait_for_textbox_and_send_keys(self.TIMELINE_NOTES_QUERY_INPUT, query)
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

    @staticmethod
    def is_updated_date_expected(note):
        created = note.created_date.strftime('%Y %m %d %H %M %S')
        updated = note.updated_date.strftime('%Y %m %d %H %M %S')
        if created != updated and note.advisor.uid != 'UCBCONVERSION':
            return True
        else:
            return False

    def visible_collapsed_note_data(self, note):
        return {
            'subject': self.collapsed_note_subject(note),
            'category': self.collapsed_note_category(note),
            'created_date': self.collapsed_note_date(note),
            'is_draft': self.collapsed_note_is_draft(note),
        }

    def collapsed_note_subject(self, note):
        return self.el_text_if_exists((By.ID, f'note-{note.record_id}-subject'))

    def collapsed_note_date(self, note):
        date_loc = By.ID, f'collapsed-note-{note.record_id}-created-at'
        return self.el_text_if_exists(date_loc, 'Last updated on')

    def collapsed_note_category(self, note):
        category_loc = By.ID, f'note-{note.record_id}-category-closed'
        return self.element(category_loc).text if self.is_present(category_loc) else None

    def collapsed_note_is_draft(self, note):
        return self.is_present((By.ID, f'note-{note.record_id}-is-draft'))

    # Expanded note

    def expanded_note_body(self, note):
        # Body may contain formatting elements even without text
        body_loc = (By.ID, f'note-{note.record_id}-subject') if note.is_peer_advising else (By.ID, f'note-{note.record_id}-message-open')
        if self.is_present(body_loc):
            text = self.element(body_loc).text
            return '' if re.sub(r'/\W/', '', text).replace('&nbsp;', '') == '' else text.replace('\n', '').strip()
        else:
            return None

    @staticmethod
    def expanded_note_advisor_loc(note):
        return By.ID, f'note-{note.record_id}-author-name'

    def expanded_note_advisor(self, note):
        return self.el_text_if_exists(self.expanded_note_advisor_loc(note))

    def expanded_note_advisor_depts(self, note):
        advisor_dept_loc = By.XPATH, f"//span[contains(@id, 'note-{note.record_id}-author-dept-')]"
        depts = self.els_text_if_exist(advisor_dept_loc)
        depts.sort()
        return depts

    def expanded_note_peer_dept(self, note):
        return self.el_text_if_exists((By.ID, f'note-{note.record_id}-peer-advising-department'))

    def expanded_note_peer_dept_parent(self, note):
        return self.el_text_if_exists((By.ID, f'note-{note.record_id}-university-department-of-peer-advisor'))

    def expanded_note_advisor_role(self, note):
        advisor_role_loc = By.ID, f'note-{note.record_id}-author-role'
        return self.el_text_if_exists(advisor_role_loc)

    def expanded_note_contact_type(self, note):
        contact_type_loc = By.ID, f'note-{note.record_id}-contact-type'
        return self.el_text_if_exists(contact_type_loc)

    def expanded_note_created_date(self, note):
        created_loc = By.ID, f'expanded-note-{note.record_id}-created-at'
        if self.is_present(created_loc):
            text = self.element(created_loc).text.replace('Created on', '').replace('\n@\n', '\n')
            return re.sub(r'/\s+/', ' ', text).strip()
        else:
            return None

    def expanded_note_source(self, note):
        note_src_loc = By.XPATH, f"//article[@id='timeline-note-{note.record_id}']//span[contains(text(), 'note imported from')]"
        return self.el_text_if_exists(note_src_loc)

    def expanded_note_permalink_url(self, note):
        permalink_loc = By.ID, f'advising-note-permalink-{note.record_id}'
        if self.is_present(permalink_loc):
            return f"{boa_utils.get_boa_base_url()}{self.element(permalink_loc).get_dom_attribute('href')}"
        else:
            return None

    def expanded_note_set_date(self, note):
        set_date_loc = By.ID, f'expanded-note-{note.record_id}-set-date'
        if self.is_present(set_date_loc):
            text = self.element(set_date_loc).text
            return re.sub(r'/\s+/', ' ', text).strip()
        else:
            return None

    def expanded_note_topics(self, note):
        topic_loc = By.XPATH, f"//*[contains(@id, 'note-{note.record_id}-topic-')]"
        topics = self.els_text_if_exist(topic_loc)
        topics.sort()
        return topics

    def expanded_note_topic_remove_btn_els(self, note):
        return self.elements((By.XPATH, f"//*[contains(@id, 'remove-note-{note.record_id}-topic-')]"))

    def expanded_note_updated_date(self, note):
        updated_loc = By.ID, f'expanded-note-{note.record_id}-updated-at'
        if self.is_present(updated_loc):
            text = self.element(updated_loc).text.replace('Last updated on', '').replace('\n@\n', '\n')
            return re.sub(r'/\s+/', ' ', text).strip()
        else:
            return None

    def expanded_note_attachments(self, note):
        els = self.item_attachment_els(note)
        attachment_names = [el.get_attribute('innerText').strip().lower() for el in els]
        attachment_names.sort()
        return attachment_names

    def verify_note(self, note, viewer):
        app.logger.info(f'Verifying visible data for note ID {note.record_id}')
        self.show_notes()

        # Collapsed

        self.when_visible(self.collapsed_item_loc(note), utils.get_medium_timeout())
        time.sleep(1)
        self.collapse_item(note)
        date = note.set_date or note.updated_date
        expected_short_updated_date = self.expected_item_short_date_format(date)
        if note.subject:
            utils.assert_equivalence(self.collapsed_note_subject(note), note.subject)
        utils.assert_equivalence(self.collapsed_note_date(note), expected_short_updated_date)

        # Expanded

        self.expand_item(note)
        utils.assert_existence(self.expanded_note_advisor(note))

        if note.advisor.dept_memberships:
            advisor_peer_roles = [mem.peer_advising_role for mem in note.advisor.dept_memberships if mem.peer_advising_role]
            if PeerAdvisingRole.PEER_ADVISOR in advisor_peer_roles:
                utils.assert_existence(self.expanded_note_advisor_role(note))
                utils.assert_existence(self.expanded_note_peer_dept(note))
                utils.assert_existence(self.expanded_note_peer_dept_parent(note))
        elif note.source != TimelineRecordSource.EOP:
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

        expected_set_date = self.expected_item_short_date_format(note.set_date) if note.set_date else None
        if (note.set_date and expected_set_date):
          utils.assert_equivalence(self.expanded_note_set_date(note), expected_set_date)

        attachments = [a.file_name for a in note.attachments if not a.deleted_at]
        attachments.sort()
        should_see_attachments = (not note.is_private) or (viewer.is_admin or Department.ZCEEE in viewer.depts)
        if attachments and should_see_attachments:
            self.wait_for_attachments()
        visible_attachments = self.expanded_note_attachments(note)
        visible_attachments.sort()

        visible_body = self.expanded_note_body(note)
        if should_see_attachments:
            utils.assert_equivalence(visible_body, note.body)
            utils.assert_equivalence(visible_attachments, attachments)
        else:
            utils.assert_non_existence(visible_body)
            utils.assert_non_existence(visible_attachments)

    # COMMENTS

    COMMENT_SAVE_ERROR = By.ID, 'edit-comment-input-error'

    @staticmethod
    def add_comment_button_loc(note):
        return By.ID, f'note-{note.record_id}-add-comment-btn'

    @staticmethod
    def new_comment_text_area_loc(note):
        return By.XPATH, f'//div[@id="note-{note.record_id}-comment-new-text"]//div[@role="textbox"]'

    @staticmethod
    def new_comment_save_loc(note):
        return By.ID, f'note-{note.record_id}-comment-new-save-btn'

    @staticmethod
    def new_comment_cancel_loc(note):
        return By.ID, f'note-{note.record_id}-comment-new-cancel-btn'

    @staticmethod
    def comment_body_loc(note, comment):
        return By.ID, f'note-{note.record_id}-comment-{comment.comment_id}-text'

    @staticmethod
    def comment_edit_button_loc(note, comment):
        return By.ID, f'note-{note.record_id}-comment-{comment.comment_id}-edit-btn'

    @staticmethod
    def comment_delete_button_loc(note, comment):
        return By.ID, f'note-{note.record_id}-comment-{comment.comment_id}-delete-btn'

    @staticmethod
    def edit_comment_text_area_loc(note, comment):
        return By.XPATH, f'//div[@id="note-{note.record_id}-comment-{comment.comment_id}-text"]//div[@role="textbox"]'

    @staticmethod
    def edit_comment_save_loc(note, comment):
        return By.ID, f'note-{note.record_id}-comment-{comment.comment_id}-save-btn'

    @staticmethod
    def edit_comment_cancel_loc(note, comment):
        return By.ID, f'note-{note.record_id}-comment-{comment.comment_id}-cancel-btn'

    def click_add_comment_button(self, note):
        app.logger.debug(f'Clicking Add Comment button for note {note.record_id}')
        self.wait_for_element_and_click(self.add_comment_button_loc(note))

    def save_new_comment(self, note):
        app.logger.debug('Saving new comment')
        self.wait_for_element_and_click(self.new_comment_save_loc(note))
        self.when_not_present(self.new_comment_save_loc(note), utils.get_short_timeout())

    def cancel_new_comment(self, note):
        app.logger.debug('Canceling new comment')
        self.wait_for_element_and_click(self.new_comment_cancel_loc(note))
        self.when_not_present(self.new_comment_cancel_loc(note), utils.get_short_timeout())

    def add_comment(self, note, comment):
        app.logger.info(f'Adding comment to note {note.record_id}')
        self.click_add_comment_button(note)
        self.wait_for_textbox_and_send_keys(self.new_comment_text_area_loc(note), comment.body)
        self.save_new_comment(note)

    def click_edit_comment_button(self, note, comment):
        app.logger.debug(f'Clicking edit button for comment {comment.comment_id}')
        self.wait_for_element_and_click(self.comment_edit_button_loc(note, comment))

    def save_edit_comment(self, note, comment):
        app.logger.debug('Saving comment edit')
        self.wait_for_element_and_click(self.edit_comment_save_loc(note, comment))
        self.when_not_present(self.edit_comment_save_loc(note, comment), utils.get_short_timeout())

    def delete_comment(self, note, comment):
        app.logger.info(f'Deleting comment {comment.comment_id} from note {note.record_id}')
        self.wait_for_element_and_click(self.comment_delete_button_loc(note, comment))
        self.confirm_delete_or_discard()
        self.when_not_present(self.comment_body_loc(note, comment), utils.get_short_timeout())

    def comment_body_text(self, note, comment):
        loc = self.comment_body_loc(note, comment)
        return self.element(loc).text if self.is_present(loc) else None

    # Comment attachments

    @staticmethod
    def new_comment_attachment_input_loc(note):
        return By.ID, f'note-{note.record_id}-comment-new-choose-file-for-note-attachment'

    @staticmethod
    def new_comment_attachment_error_loc(note):
        return By.ID, f'note-{note.record_id}-comment-new-attachment-error'

    @staticmethod
    def new_comment_attachment_delete_btn_loc(note, attachment):
        return By.XPATH, f'//ul[@id="note-{note.record_id}-comment-new-attachments-list"]//li[contains(., "{attachment.file_name}")]//button'

    @staticmethod
    def edit_comment_attachment_input_loc(note, comment):
        return By.ID, f'note-{note.record_id}-comment-{comment.comment_id}-choose-file-for-note-attachment'

    @staticmethod
    def edit_comment_attachment_error_loc(note, comment):
        return By.ID, f'note-{note.record_id}-comment-{comment.comment_id}-attachment-error'

    @staticmethod
    def edit_comment_attachment_delete_btn_loc(note, comment, attachment):
        list_id = f'note-{note.record_id}-comment-{comment.comment_id}-attachments-list'
        return By.XPATH, f'//ul[@id="{list_id}"]//li[contains(., "{attachment.file_name}")]//button'

    @staticmethod
    def comment_attachment_remove_btn_loc(note, comment, index):
        return By.ID, f'remove-note-{note.record_id}-comment-{comment.comment_id}-attachment-{index}-btn'

    def add_attachments_to_new_comment(self, note, comment, attachments):
        for a in attachments:
            app.logger.info(f'Adding attachment {a.file_name} to new comment on note {note.record_id}')
            path = f'{utils.attachments_dir()}/{a.file_name}'
            self.when_present(self.new_comment_attachment_input_loc(note), utils.get_short_timeout())
            self.element(self.new_comment_attachment_input_loc(note)).send_keys(path)
            self.when_present(self.new_comment_attachment_delete_btn_loc(note, a), utils.get_medium_timeout())
            comment.attachments.append(a)

    def remove_attachments_from_new_comment(self, note, comment, attachments):
        for a in attachments:
            app.logger.info(f'Removing attachment {a.file_name} from new comment on note {note.record_id}')
            self.wait_for_element_and_click(self.new_comment_attachment_delete_btn_loc(note, a))
            self.when_not_present(self.new_comment_attachment_delete_btn_loc(note, a), utils.get_short_timeout())
            comment.attachments.remove(a)

    def add_attachments_to_existing_comment(self, note, comment, attachments):
        for a in attachments:
            app.logger.info(f'Adding attachment {a.file_name} to comment {comment.comment_id} on note {note.record_id}')
            path = f'{utils.attachments_dir()}/{a.file_name}'
            self.when_present(self.edit_comment_attachment_input_loc(note, comment), utils.get_short_timeout())
            self.element(self.edit_comment_attachment_input_loc(note, comment)).send_keys(path)
            self.when_present(self.edit_comment_attachment_delete_btn_loc(note, comment, a), utils.get_medium_timeout())
            comment.attachments.append(a)

    def remove_attachments_from_existing_comment(self, note, comment, attachments):
        for a in attachments:
            app.logger.info(f'Removing attachment {a.file_name} from comment {comment.comment_id} on note {note.record_id}')
            self.wait_for_element_and_click(self.edit_comment_attachment_delete_btn_loc(note, comment, a))
            self.when_not_present(self.edit_comment_attachment_delete_btn_loc(note, comment, a), utils.get_short_timeout())
            comment.attachments.remove(a)

    def visible_comment_attachments(self, note, comment):
        loc = By.XPATH, (
            f'//ul[@id="note-{note.record_id}-comment-{comment.comment_id}-attachments-list"]'
            f'//span[contains(@class, "truncate-with-ellipsis")]'
        )
        return [el.text.strip().lower() for el in self.elements(loc)]

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
        self.wait_for_element_and_click(self.delete_note_button_loc(note))
        self.confirm_delete_or_discard()
        note.deleted_date = datetime.datetime.now()

    # Save

    EDIT_NOTE_SAVE_BUTTON = By.ID, 'save-note-button'

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

    def create_note(self, note, topics, attachments, student=None):
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
        self.set_new_note_id(note, student)

    # Notes

    def notes_export_zip_file_name(self, student):
        return self.export_zip_file_name(student, 'notes')

    def notes_export_csv_file_name(self, student):
        return self.export_csv_file_name(student, 'notes')

    def download_notes(self, student):
        app.logger.info(f'Downloading notes for UID {student.uid}')
        utils.prepare_download_dir()
        self.wait_for_element_and_click(self.NOTES_DOWNLOAD_LINK)
        return utils.wait_for_export_zip()

    def note_export_file_names(self, student):
        names = self.downloaded_zip_file_name_list(self.notes_export_zip_file_name(student))
        return list(map(lambda n: n.lower(), names))

    def expected_note_export_file_names(self, student, notes, downloader):
        names = [self.notes_export_csv_file_name(student)]

        attachments = []
        for note in notes:
            if not isinstance(note, TimelineEForm) and not (
                    note.is_private and not downloader.is_admin and Department.ZCEEE not in downloader.depts):
                attachments.extend([attach for attach in note.attachments if not attach.deleted_at])

        # Account for duplicate attachment file names
        for key, result in itertools.groupby(attachments, key=lambda att: att.file_name):
            parts = key.rpartition('.')
            grouped = list(result)
            for dupe_attach in grouped:
                idx = grouped.index(dupe_attach)
                names.append(f"{parts[0]}{'' if idx == 0 else idx}.{parts[-1]}")
        return names

    def verify_note_in_export_csv(self, student, note, downloader):
        file_path = f'{utils.default_download_dir()}/{self.notes_export_zip_file_name(student)}'
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            with zip_file.open(self.notes_export_csv_file_name(student)) as csv_file:
                csv_reader = csv.DictReader(TextIOWrapper(csv_file))
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
                        if (
                                note.is_private and not downloader.is_admin and Department.ZCEEE not in downloader.depts) or not note.body:
                            assert not row['body']

                        exp_tops = [topic.name.lower() if topic.__class__.__name__ == 'Topic' else topic for topic in
                                    note.topics]
                        exp_tops.sort()
                        act_tops = [topic.strip().lower() for topic in row['topics'].split(';')] if row['topics'] else []
                        act_tops.sort()
                        assert act_tops == exp_tops

                        if (
                                note.is_private and not downloader.is_admin and Department.ZCEEE not in downloader.depts) or not note.attachments:
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
