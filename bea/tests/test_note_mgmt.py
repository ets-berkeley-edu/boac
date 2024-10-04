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
import os
import random

from bea.config.bea_test_config import BEATestConfig
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.topic import Topic
from bea.models.notes_and_appts.topic import Topics
from bea.test_utils import boa_utils
from bea.test_utils import nessie_timeline_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


@pytest.mark.usefixtures('page_objects')
class TestNoteMgmt:

    test = BEATestConfig()
    test.note_mgmt()

    auth_users = boa_utils.get_authorized_users()
    director = boa_utils.get_director(auth_users)
    other_advisor = boa_utils.get_advising_data_advisor(test.dept, test.advisor)
    random.shuffle(test.students)
    test_student = test.students[0]

    app.logger.info(f'Advisor UID {test.advisor.uid}, director UID {director.uid}, other advisor UID {other_advisor.uid}')

    note_1 = Note({'advisor': test.advisor})
    note_2 = Note({'advisor': test.advisor})
    note_3 = Note({'advisor': test.advisor})
    note_4 = Note({'advisor': test.advisor})
    note_5 = Note({'advisor': test.advisor})
    note_6 = Note({'advisor': test.advisor})
    note_7 = Note({'advisor': test.advisor})
    note_8 = Note({'advisor': test.advisor})
    notes = [note_1, note_2, note_3, note_4, note_5, note_6, note_7, note_8]

    # Get the largest attachments for testing max attachments uploads
    test.attachments.sort(key=lambda a: a.file_size, reverse=True)
    too_big_attachments = list(filter(lambda a: a.file_size > 20000000, test.attachments))
    valid_attachments = list(filter(lambda a: a.file_size < 20000000, test.attachments))
    deleted_attachments = []

    def test_create_note_subject_required(self):
        self.homepage.dev_auth(self.test.advisor)
        self.student_page.load_page(self.test_student)
        self.note_1.subject = ''
        self.student_page.click_create_new_note()
        self.student_page.enter_new_note_subject(self.note_1)
        assert not self.student_page.element(self.student_page.NEW_NOTE_SAVE_BUTTON).is_enabled()

    def test_create_note_but_cancel(self):
        self.student_page.click_cancel_new_note()
        self.student_page.confirm_delete_or_discard()
        self.student_page.click_create_new_note()
        self.student_page.wait_for_note_body_editor()
        self.student_page.wait_for_textbox_and_type(self.student_page.NOTE_BODY_TEXT_AREA, 'An edit to forget')
        self.student_page.click_cancel_new_note()
        self.student_page.confirm_delete_or_discard()

    def test_create_note_with_subject_only(self):
        self.note_1.subject = f'Note 1 subject {utils.get_test_identifier()}'
        self.student_page.create_note(self.note_1, [], [])
        self.student_page.verify_note(self.note_1, self.test.advisor)

    def test_create_note_with_subject_and_body(self):
        self.note_2.subject = f'Note 2 subject {utils.get_test_identifier()}'
        self.note_2.body = f'Note 2 body {self.test.test_id}'
        self.student_page.create_note(self.note_2, [], [])
        self.student_page.verify_note(self.note_2, self.test.advisor)

    def test_create_note_with_contact_type_and_set_date(self):
        self.note_3.subject = f'Σημείωση θέμα 3 {utils.get_test_identifier()}'
        self.note_3.body = 'ノート本体4' * 100
        self.note_3.type = 'In-person same day'
        self.note_3.set_date = datetime.datetime.now() - datetime.timedelta(days=1)
        self.student_page.create_note(self.note_3, [], [])
        self.student_page.verify_note(self.note_3, self.test.advisor)

    def test_create_note_add_remove_attachments(self):
        self.note_4.subject = f'Note 4 subject {utils.get_test_identifier()}'
        self.student_page.click_create_new_note()
        self.student_page.enter_new_note_subject(self.note_4)
        self.student_page.add_attachments_to_new_note(self.note_4, self.valid_attachments[0:1])
        self.student_page.remove_attachments_from_new_note(self.note_4, self.valid_attachments[0:1])
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(self.note_4)
        self.student_page.verify_note(self.note_4, self.test.advisor)

    def test_create_note_with_attachments(self):
        self.note_5.subject = f'Note 5 subject {utils.get_test_identifier()}'
        self.student_page.create_note(self.note_5, [], self.valid_attachments[0:1])
        self.student_page.verify_note(self.note_5, self.test.advisor)

    def test_create_note_max_attachments(self):
        self.note_6.subject = f'Note 6 subject {utils.get_test_identifier()}'
        self.student_page.click_create_new_note()
        self.student_page.enter_new_note_subject(self.note_6)
        self.student_page.add_attachments_to_new_note(self.note_6, self.valid_attachments)
        self.student_page.when_not_visible(self.student_page.NEW_NOTE_ATTACH_INPUT, 1)
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(self.note_6)
        self.student_page.verify_note(self.note_6, self.test.advisor)

    def test_create_note_attachment_too_big(self):
        file_path = f'{utils.attachments_dir()}/{self.too_big_attachments[0].file_name}'
        self.student_page.click_create_new_note()
        self.student_page.enter_new_note_attachments(file_path)
        self.student_page.when_present(self.student_page.NOTE_ATTACHMENT_SIZE_MSG, utils.get_short_timeout())

    def test_create_note_add_remove_topics(self):
        topic_1 = Topic(Topics.COURSE_ADD.value)
        topic_2 = Topic(Topics.COURSE_DROP.value)
        self.note_7.subject = f'Note 7 subject {utils.get_test_identifier()}'
        self.student_page.click_cancel_new_note()
        self.student_page.confirm_delete_or_discard()
        self.student_page.load_page(self.test_student)
        self.student_page.click_create_new_note()
        self.student_page.enter_new_note_subject(self.note_7)
        self.student_page.add_topics(self.note_7, [topic_1, topic_2])
        self.student_page.remove_topics(self.note_7, [topic_1, topic_2])
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(self.note_7)
        self.student_page.verify_note(self.note_7, self.test.advisor)

    def test_create_note_with_topics(self):
        topic_1 = Topic(Topics.EAP.value)
        topic_2 = Topic(Topics.SAT_ACAD_PROGRESS_APPEAL.value)
        topic_3 = Topic(Topics.PASS_NO_PASS.value)
        topic_4 = Topic(Topics.PROBATION.value)
        self.note_8.subject = f'Note 8 subject {utils.get_test_identifier()}'
        self.student_page.load_page(self.test_student)
        self.student_page.create_note(self.note_8, [topic_1, topic_2, topic_3, topic_4], [])
        self.student_page.verify_note(self.note_8, self.test.advisor)

    def test_create_note_reindex(self):
        self.student_page.load_page(self.test_student)
        self.student_page.log_out()
        self.homepage.dev_auth()
        self.api_admin_page.reindex_notes()
        self.homepage.load_page()
        self.homepage.log_out()

    def test_search_my_new_note_by_subject(self):
        self.homepage.dev_auth(self.test.advisor)
        self.student_page.reopen_and_reset_adv_search()
        self.student_page.exclude_students()
        self.student_page.exclude_classes()
        self.student_page.select_notes_posted_by_you()
        self.student_page.enter_adv_search_and_hit_enter(self.note_1.subject)
        self.search_results_page.wait_for_note_search_result_rows()
        assert self.search_results_page.is_note_in_search_result(self.note_1)

    def test_search_my_new_note_by_body(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_2.body)
        self.search_results_page.wait_for_note_search_result_rows()
        assert self.search_results_page.is_note_in_search_result(self.note_2)

    def test_search_my_new_note_special_characters(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_3.subject)
        self.search_results_page.wait_for_note_search_result_rows()
        assert self.search_results_page.is_note_in_search_result(self.note_3)

    def test_search_anyone_new_note_by_subject(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.exclude_students()
        self.search_results_page.exclude_classes()
        self.search_results_page.select_notes_posted_by_anyone()
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_1.subject)
        self.search_results_page.wait_for_note_search_result_rows()
        assert self.search_results_page.is_note_in_search_result(self.note_1)

    def test_search_anyone_new_note_by_body(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_2.body)
        self.search_results_page.wait_for_note_search_result_rows()
        assert self.search_results_page.is_note_in_search_result(self.note_2)

    def test_search_anyone_new_note_special_characters(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_3.subject)
        self.search_results_page.wait_for_note_search_result_rows()
        assert self.search_results_page.is_note_in_search_result(self.note_3)

    def test_view_new_note_download_attachments(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_5)
        for attach in self.note_5.attachments:
            self.student_page.download_attachment(self.note_5, attach)

    def test_view_new_note_hit_permalink(self):
        permalink = self.student_page.expanded_note_permalink_url(self.note_5)
        self.driver.get(permalink)
        self.student_page.when_present(self.student_page.expanded_item_loc(self.note_5), utils.get_short_timeout())

    def test_view_new_notes_in_right_order(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        new_note_ids = list(map(lambda n: n.record_id, self.notes))
        visible_new_note_ids = self.student_page.visible_collapsed_note_ids()
        visible_new_note_ids = [record_id for record_id in visible_new_note_ids if record_id in new_note_ids]
        utils.assert_equivalence(visible_new_note_ids, self.student_page.expected_note_id_sort_order(self.notes))

    def test_view_new_notes_no_download_link(self):
        assert not self.student_page.is_present(self.student_page.NOTES_DOWNLOAD_LINK)

    def test_new_note_downloads_forbidden(self):
        utils.prepare_download_dir()
        self.api_notes_page.load_download_page(self.test_student)
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located(self.api_notes_page.NOT_FOUND_MSG),
        )
        assert utils.is_download_dir_empty()

    def test_view_all_student_notes(self):
        asc_notes = nessie_timeline_utils.get_asc_notes(self.test_student)
        boa_notes = boa_utils.get_student_notes(self.test_student)
        expected_boa_notes = [n for n in boa_notes if
                              not ((n.is_draft and n.advisor.uid != self.test.advisor.uid) or n.deleted_date)]
        data_sci_notes = nessie_timeline_utils.get_data_sci_notes(self.test_student)
        e_and_i_notes = nessie_timeline_utils.get_e_and_i_notes(self.test_student)
        eop_notes = nessie_timeline_utils.get_eop_notes(self.test_student)
        history_notes = nessie_timeline_utils.get_history_notes(self.test_student)
        sis_notes = nessie_timeline_utils.get_sis_notes(self.test_student)
        all_student_notes = asc_notes + expected_boa_notes + data_sci_notes + e_and_i_notes + eop_notes + history_notes + sis_notes

        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        expected = list(map(lambda n: n.record_id, all_student_notes))
        expected.sort()
        visible = self.student_page.visible_collapsed_note_ids()
        visible.sort()
        utils.assert_equivalence(visible, expected)
        self.student_page.toggle_my_notes()

        advisor_note_ids = [n.record_id for n in all_student_notes if n.advisor and n.advisor.uid == self.test.advisor.uid]
        advisor_note_ids.sort()
        visible_note_ids = self.student_page.visible_collapsed_note_ids()
        visible_note_ids.sort()
        utils.assert_equivalence(visible_note_ids, advisor_note_ids)

    def test_edit_note_and_cancel(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        original_subject = self.note_1.subject
        self.note_1.subject = 'An edit to forget'
        self.student_page.expand_item(self.note_1)
        self.student_page.click_edit_note_button(self.note_1)
        self.student_page.enter_edit_note_subject(self.note_1)
        self.student_page.click_cancel_note_edit()
        self.student_page.confirm_delete_or_discard()
        Wait(self.driver, 1).until(ec.none_of(ec.presence_of_all_elements_located(self.student_page.NOTE_BODY_TEXT_AREA)))
        self.note_1.subject = original_subject
        self.student_page.click_close_msg(self.note_1)
        self.student_page.verify_note(self.note_1, self.test.advisor)

    def test_edit_note_subject(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.note_1.subject = f'{self.note_1.subject} - EDITED'
        self.student_page.edit_note_subject_and_save(self.note_1)
        self.student_page.click_close_msg(self.note_1)
        self.student_page.verify_note(self.note_1, self.test.advisor)

    def test_edit_note_add_attachments(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_4)
        self.student_page.add_attachments_to_existing_note(self.note_4, self.valid_attachments[5:6])
        self.student_page.click_close_msg(self.note_4)
        self.student_page.verify_note(self.note_4, self.test.advisor)

    def test_edit_note_contact_type(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.note_4.type = 'Phone'
        self.student_page.expand_item(self.note_4)
        self.student_page.click_edit_note_button(self.note_4)
        self.student_page.select_contact_type(self.note_4)
        self.student_page.save_note_edit(self.note_4)
        self.student_page.click_close_msg(self.note_4)
        self.student_page.verify_note(self.note_4, self.test.advisor)

    def test_edit_note_remove_contact_type(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.note_4.type = None
        self.student_page.expand_item(self.note_4)
        self.student_page.click_edit_note_button(self.note_4)
        self.student_page.select_contact_type(self.note_4)
        self.student_page.save_note_edit(self.note_4)
        self.student_page.click_close_msg(self.note_4)
        self.student_page.verify_note(self.note_4, self.test.advisor)

    def test_edit_note_set_date(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.note_4.set_date = datetime.datetime.today() - datetime.timedelta(days=1)
        self.student_page.expand_item(self.note_4)
        self.student_page.click_edit_note_button(self.note_4)
        self.student_page.enter_set_date(self.note_4)
        self.student_page.save_note_edit(self.note_4)
        self.student_page.click_close_msg(self.note_4)
        self.student_page.verify_note(self.note_4, self.test.advisor)

    def test_edited_set_date_sort_order(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        test_note_ids = list(map(lambda n: n.record_id, self.notes))
        visible_note_ids = self.student_page.visible_collapsed_note_ids()
        visible_test_note_ids = [record_id for record_id in visible_note_ids if record_id in test_note_ids]
        utils.assert_equivalence(visible_test_note_ids, self.student_page.expected_note_id_sort_order(self.notes))

    def test_edit_note_remove_set_date(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.note_4.set_date = None
        self.student_page.expand_item(self.note_4)
        self.student_page.click_edit_note_button(self.note_4)
        self.student_page.enter_set_date(self.note_4)
        self.student_page.save_note_edit(self.note_4)
        self.student_page.click_close_msg(self.note_4)
        self.student_page.verify_note(self.note_4, self.test.advisor)

    def test_edit_note_max_attachments(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_6)
        assert not self.student_page.is_present(self.student_page.existing_note_attachment_input(self.note_6))

    def test_edit_note_remove_attachment(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_5)
        attach_to_delete = self.note_5.attachments[0]
        boa_utils.get_attachment_id_by_file_name(self.note_5, attach_to_delete)
        self.deleted_attachments.append(attach_to_delete)
        self.student_page.remove_attachments_from_existing_note(self.note_5, [self.note_5.attachments[0]])
        self.student_page.click_close_msg(self.note_5)
        self.student_page.verify_note(self.note_5, self.test.advisor)

    def test_edit_note_add_topics(self):
        topic_1 = Topic(Topics.LATE_ENROLLMENT.value)
        topic_2 = Topic(Topics.RETROACTIVE_ADD.value)
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_7)
        self.student_page.click_edit_note_button(self.note_7)
        self.student_page.add_topics(self.note_7, [topic_1, topic_2])
        self.student_page.click_save_note_edit()
        self.student_page.when_not_present(self.student_page.EDIT_NOTE_SAVE_BUTTON, utils.get_short_timeout())
        self.note_7.updated_date = datetime.datetime.now()
        self.student_page.click_close_msg(self.note_7)
        self.student_page.verify_note(self.note_7, self.test.advisor)

    def test_edit_note_remove_topics(self):
        topic_1 = Topic(Topics.EAP.value)
        topic_2 = Topic(Topics.PASS_NO_PASS.value)
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_8)
        self.student_page.click_edit_note_button(self.note_8)
        self.student_page.remove_topics(self.note_8, [topic_1, topic_2])
        self.student_page.click_save_note_edit()
        self.student_page.when_not_present(self.student_page.EDIT_NOTE_SAVE_BUTTON, utils.get_short_timeout())
        self.note_8.updated_date = datetime.datetime.now()
        self.student_page.click_close_msg(self.note_8)
        self.student_page.verify_note(self.note_8, self.test.advisor)

    def test_edit_one_note_at_a_time(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_1)
        self.student_page.when_present(self.student_page.edit_note_button_loc(self.note_1))
        self.student_page.expand_item(self.note_2)
        self.student_page.when_present(self.student_page.edit_note_button_loc(self.note_2))
        self.student_page.click_edit_note_button(self.note_1)
        assert not self.student_page.is_present(self.student_page.edit_note_button_loc(self.note_2))
        assert not self.student_page.element(self.student_page.NEW_NOTE_BUTTON).is_enabled()

    def test_edit_note_no_removing_subject(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_2)
        self.student_page.click_edit_note_button(self.note_2)
        self.student_page.wait_for_textbox_and_type(self.student_page.EDIT_NOTE_SUBJECT_INPUT, ' ')
        assert not self.student_page.element(self.student_page.EDIT_NOTE_SAVE_BUTTON).is_enabled()
        self.student_page.click_cancel_note_edit()
        self.student_page.confirm_delete_or_discard()

    def test_edit_note_no_dupe_attach_names(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_4)
        Wait(self.driver, 1).until(ec.presence_of_element_located(self.student_page.existing_note_attachment_input(self.note_4)))
        path = f'{utils.attachments_dir()}/{self.valid_attachments[5].file_name}'
        self.student_page.element(self.student_page.existing_note_attachment_input(self.note_4)).send_keys(path)
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_element_located(self.student_page.NOTE_DUPE_ATTACHMENT_MSG))

    def test_edit_note_no_big_attachments(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_2)
        Wait(self.driver, 1).until(ec.presence_of_element_located(self.student_page.existing_note_attachment_input(self.note_2)))
        path = f'{utils.attachments_dir()}/{self.too_big_attachments[0].file_name}'
        self.student_page.element(self.student_page.existing_note_attachment_input(self.note_2)).send_keys(path)
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_element_located(self.student_page.NOTE_ATTACHMENT_SIZE_MSG))

    def test_edited_notes_sort_order(self):
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        test_note_ids = list(map(lambda n: n.record_id, self.notes))
        visible_note_ids = self.student_page.visible_collapsed_note_ids()
        visible_test_note_ids = [record_id for record_id in visible_note_ids if record_id in test_note_ids]
        assert visible_test_note_ids == self.student_page.expected_note_id_sort_order(self.notes)

    def test_no_advisor_note_deletion(self):
        self.student_page.expand_item(self.note_1)
        assert not self.student_page.is_present(self.student_page.delete_note_button_loc(self.note_1))

    def test_search_edited_note(self):
        self.student_page.load_page(self.test_student)
        self.student_page.log_out()
        self.homepage.dev_auth()
        self.api_admin_page.reindex_notes()
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(self.test.advisor)
        self.homepage.enter_simple_search_and_hit_enter(self.note_1.subject)
        assert self.search_results_page.is_note_in_search_result(self.note_1)

    def test_no_deleted_attachment_downloads(self):
        utils.prepare_download_dir()
        self.api_notes_page.load_attachment_page(self.deleted_attachments[0].attachment_id)
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_element_located(self.api_notes_page.NOTE_NOT_FOUND_MSG),
        )
        assert not os.listdir(utils.default_download_dir())

    def test_no_non_author_edits(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(self.other_advisor)
        self.student_page.load_page(self.test_student)
        self.student_page.expand_item(self.note_5)
        assert not self.student_page.is_present(self.student_page.edit_note_button_loc(self.note_5))

    def test_no_non_author_attachment_deletion(self):
        self.student_page.expand_item(self.note_5)
        current_attachments = list(filter(lambda attach: not attach.deleted_at, self.note_5.attachments))
        for a in current_attachments:
            assert not self.student_page.is_present(self.student_page.existing_note_attachment_delete_button(self.note_5, a))

    def test_non_author_download_attachments(self):
        current_attachments = list(filter(lambda attach: not attach.deleted_at, self.note_5.attachments))
        for a in current_attachments:
            self.student_page.download_attachment(self.note_5, a)

    def test_non_author_search_anyone_for_edited_note(self):
        self.student_page.reopen_and_reset_adv_search()
        self.student_page.select_notes_posted_by_anyone()
        self.student_page.enter_adv_search_and_hit_enter(self.note_1.subject)
        assert self.search_results_page.is_note_in_search_result(self.note_1)

    def test_non_author_search_self_for_edited_note(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.student_page.select_notes_posted_by_you()
        self.student_page.enter_adv_search_and_hit_enter(self.note_1.subject)
        self.search_results_page.wait_for_no_results()

    def test_non_author_view_all_student_notes(self):
        asc_notes = nessie_timeline_utils.get_asc_notes(self.test_student)
        boa_notes = boa_utils.get_student_notes(self.test_student)
        expected_boa_notes = [n for n in boa_notes if
                              not ((n.is_draft and n.advisor.uid != self.test.advisor.uid) or n.deleted_date)]
        data_sci_notes = nessie_timeline_utils.get_data_sci_notes(self.test_student)
        e_and_i_notes = nessie_timeline_utils.get_e_and_i_notes(self.test_student)
        eop_notes = nessie_timeline_utils.get_eop_notes(self.test_student)
        history_notes = nessie_timeline_utils.get_history_notes(self.test_student)
        sis_notes = nessie_timeline_utils.get_sis_notes(self.test_student)
        all_student_notes = asc_notes + expected_boa_notes + data_sci_notes + e_and_i_notes + eop_notes + history_notes + sis_notes

        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        expected = list(map(lambda n: n.record_id, all_student_notes))
        expected.sort()
        visible = self.student_page.visible_collapsed_note_ids()
        visible.sort()
        assert visible == expected

        self.student_page.toggle_my_notes()
        advisor_note_ids = [n.record_id for n in all_student_notes if n.advisor and n.advisor.uid == self.other_advisor.uid]
        advisor_note_ids.sort()
        visible_note_ids = self.student_page.visible_collapsed_note_ids()
        visible_note_ids.sort()
        assert visible_note_ids == advisor_note_ids

    def test_director_can_download_notes(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(self.director)
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located(self.student_page.NOTES_DOWNLOAD_LINK),
        )

    def test_admin_no_note_creation(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth()
        self.student_page.load_page(self.test_student)
        self.student_page.show_notes()
        assert not self.student_page.is_present(self.student_page.NEW_NOTE_BUTTON)

    def test_admin_no_batch_note_creation(self):
        assert not self.student_page.is_present(self.student_page.BATCH_NOTE_BUTTON)

    def test_admin_can_download_notes(self):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.visibility_of_element_located(self.student_page.NOTES_DOWNLOAD_LINK),
        )

    def test_admin_no_note_editing(self):
        self.student_page.expand_item(self.note_5)
        assert not self.student_page.is_present(self.student_page.edit_note_button_loc(self.note_5))

    def test_admin_can_delete_notes(self):
        self.student_page.delete_note(self.note_5)
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.invisibility_of_element_located(self.student_page.collapsed_item_loc(self.note_5)),
        )

    def test_no_deleted_notes_in_search_results(self):
        self.api_admin_page.reindex_notes()
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(self.test.advisor)
        self.student_page.open_adv_search()
        self.student_page.exclude_students()
        self.student_page.exclude_classes()
        self.student_page.enter_adv_search_and_hit_enter(self.note_5.subject)
        self.search_results_page.wait_for_no_results()

    def test_no_deleted_note_attachment_downloads(self):
        for a in self.note_5.attachments:
            utils.prepare_download_dir()
            self.homepage.load_page()
            record_id = boa_utils.get_attachment_id_by_file_name(self.note_5, a)
            self.api_notes_page.load_attachment_page(record_id)
            Wait(self.driver, utils.get_short_timeout()).until(
                ec.presence_of_element_located(self.api_notes_page.NOTE_NOT_FOUND_MSG),
            )
            assert not os.listdir(utils.default_download_dir())
