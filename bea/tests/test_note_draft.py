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
from datetime import date
from datetime import datetime
from datetime import timedelta
import random
import time

from bea.config.bea_test_config import BEATestConfig
from bea.models.advisor_role import AdvisorRole
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.models.department import Department
from bea.models.department_membership import DepartmentMembership
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.note_batch import NoteBatch
from bea.models.notes_and_appts.topic import Topic, Topics
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest


@pytest.mark.usefixtures('page_objects')
class TestNoteDraft:
    test = BEATestConfig()
    test.note_draft()
    today = date.today().strftime('%Y-%m-%d')

    auth_users = boa_utils.get_authorized_users()
    director = boa_utils.get_director(auth_users)
    other_advisor = boa_utils.get_advising_data_advisor(test.dept, test.advisor)
    random.shuffle(test.test_students)
    student = test.test_students[0]

    app.logger.info(
        f'Advisor UID {test.advisor.uid}, director UID {director.uid}, other advisor UID {other_advisor.uid}')

    note_1 = Note({'advisor': test.advisor, 'is_draft': True})
    note_2 = NoteBatch({'advisor': other_advisor, 'is_draft': True})
    note_3 = Note({'advisor': test.advisor, 'is_draft': True})
    note_4 = NoteBatch({'advisor': test.advisor, 'is_draft': True})
    note_5 = NoteBatch({'advisor': test.advisor, 'is_draft': True})
    note_6 = NoteBatch({'advisor': test.advisor, 'is_draft': True})
    notes = [note_1, note_2, note_3, note_4, note_5, note_6]

    test.attachments.sort(key=lambda a: a.file_size)
    attachments = test.attachments[0:10]
    topics = [Topic(Topics.COURSE_DROP.value), Topic(Topics.PROBATION.value)]

    cohort = test.default_cohort
    random.shuffle(test.students)
    group_members = test.students[-50:]
    group = Cohort({'name': f'Group 1 {test.test_id}'})

    # CREATION

    def test_setup(self):
        self.homepage.load_page()
        self.homepage.dev_auth(self.test.advisor)

        pre_existing_cohorts = boa_utils.get_user_filtered_cohorts(self.test.advisor)
        for c in pre_existing_cohorts:
            self.filtered_students_page.load_and_delete_cohort(c)
        pre_existing_groups = boa_utils.get_user_curated_groups(self.test.advisor)
        for g in pre_existing_groups:
            self.curated_students_page.load_and_delete_group(g)

        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(self.cohort)
        self.filtered_students_page.create_new_cohort(self.cohort)

        self.homepage.click_sidebar_create_student_group()
        self.curated_students_page.create_group_with_bulk_sids(self.group, self.group_members)

        self.homepage.click_draft_notes()
        self.draft_notes_page.delete_all_drafts()

    def test_canceling_note_deletes_draft(self):
        self.student_page.load_page(self.student)
        self.student_page.click_create_new_note()
        self.note_1.subject = f'Draft note 1 {self.test.test_id} subject'
        self.student_page.enter_new_note_subject(self.note_1)
        self.student_page.wait_for_draft_note(self.note_1)
        self.student_page.click_cancel_new_note()
        self.student_page.confirm_delete_or_discard()
        self.student_page.show_notes()
        assert self.note_1.record_id not in self.student_page.visible_collapsed_note_ids()

    # Draft notes on student page

    def test_draft_subject_added(self):
        self.student_page.load_page(self.student)
        self.student_page.click_create_new_note()
        self.note_1.subject = f'Draft note 1 {self.test.test_id} subject'
        self.student_page.enter_new_note_subject(self.note_1)
        self.student_page.wait_for_draft_note(self.note_1)

    def test_draft_subject_removed(self):
        self.note_1.subject = None
        self.student_page.enter_new_note_subject(self.note_1)
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_body_added(self):
        self.note_1.subject = f'Draft note 1 {self.test.test_id} subject'
        self.note_1.body = f'Draft note 1 {self.test.test_id} body'
        self.student_page.enter_new_note_subject(self.note_1)
        self.student_page.enter_note_body(self.note_1)
        self.student_page.click_save_as_draft()
        self.student_page.wait_for_draft_note_update(self.note_1, manual_update=True)

    def test_draft_body_removed(self):
        self.note_1.body = None
        self.student_page.expand_item(self.note_1)
        self.student_page.click_edit_note_button(self.note_1)
        self.student_page.enter_note_body(self.note_1)
        self.student_page.click_update_note_draft()
        self.student_page.wait_for_draft_note_update(self.note_1, manual_update=True)

    def test_draft_attachments_added(self):
        self.student_page.add_attachments_to_existing_note(self.note_1, [self.attachments[0]])
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_attachments_removed(self):
        self.student_page.remove_attachments_from_existing_note(self.note_1, [self.note_1.attachments[0]])
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_attachments_re_added(self):
        self.student_page.add_attachments_to_existing_note(self.note_1, [self.attachments[0]])
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_topics_added(self):
        self.student_page.click_edit_note_button(self.note_1)
        self.student_page.add_topics(self.note_1, self.topics)
        self.student_page.click_update_note_draft()
        self.student_page.wait_for_draft_note_update(self.note_1, manual_update=True)

    def test_draft_topics_removed(self):
        self.student_page.click_edit_note_button(self.note_1)
        self.student_page.remove_topics(self.note_1, self.topics)
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_set_date_added(self):
        self.note_1.set_date = datetime.strptime(self.today, '%Y-%m-%d') - timedelta(days=1)
        self.student_page.enter_set_date(self.note_1)
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_set_date_removed(self):
        self.note_1.set_date = None
        self.student_page.enter_set_date(self.note_1)
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_contact_method_added(self):
        self.note_1.contact_type = 'Phone'
        self.student_page.click_update_note_draft()
        self.student_page.click_edit_note_button(self.note_1)
        self.student_page.select_contact_type(self.note_1)
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_contact_method_removed(self):
        self.note_1.contact_type = None
        self.student_page.select_contact_type(self.note_1)
        self.student_page.wait_for_draft_note_update(self.note_1)

    def test_draft_privacy_added(self):
        self.note_1.is_private = True
        self.student_page.set_note_privacy(self.note_1)
        self.student_page.wait_for_draft_note_update(self.note_1)

    # Drafts of batch notes

    def test_batch_draft_subject_added(self):
        self.student_page.log_out()
        self.homepage.dev_auth(self.other_advisor)
        self.homepage.click_create_note_batch()
        self.note_2.subject = f'Draft note 2 {self.test.test_id} subject'
        self.homepage.enter_new_note_subject(self.note_2)
        self.homepage.wait_for_draft_note(self.note_2)

    def test_batch_draft_single_student_added(self):
        self.homepage.add_students_to_batch(self.note_2, [self.student])
        self.homepage.click_save_as_draft()
        self.homepage.wait_for_draft_note_update(self.note_2, manual_update=True)

    def test_batch_draft_subject_removed(self):
        self.note_2.subject = None
        self.homepage.click_draft_notes()
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.enter_new_note_subject(self.note_2)
        self.draft_notes_page.wait_for_draft_note_update(self.note_2)

    def test_batch_draft_body_added(self):
        self.note_2.subject = f'Draft note 2 {self.test.test_id} subject'
        self.note_2.body = f'Draft note 2 {self.test.test_id} body'
        self.draft_notes_page.enter_new_note_subject(self.note_2)
        self.draft_notes_page.enter_note_body(self.note_2)
        self.draft_notes_page.wait_for_draft_note_update(self.note_2)

    def test_batch_draft_attachments_added(self):
        self.draft_notes_page.add_attachments_to_new_note(self.note_2, self.attachments[1:2])
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_2, manual_update=True)

    def test_batch_draft_attachments_removed(self):
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.remove_attachments_from_new_note(self.note_2, [self.note_2.attachments[-1]])
        self.draft_notes_page.wait_for_draft_note_update(self.note_2)

    def test_batch_draft_topics_added(self):
        self.draft_notes_page.add_topics(self.note_2, self.topics)
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_2, manual_update=True)

    def test_batch_draft_topics_removed(self):
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.remove_topics(self.note_2, [self.topics[0]])
        self.draft_notes_page.wait_for_draft_note_update(self.note_2)

    def test_batch_draft_set_date_added(self):
        self.note_2.set_date = datetime.strptime(self.today, '%Y-%m-%d') - timedelta(days=1)
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.enter_set_date(self.note_2)
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_2, manual_update=True)

    def test_batch_draft_set_date_removed(self):
        self.note_2.set_date = None
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.enter_set_date(self.note_2)
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_2, manual_update=True)

    def test_batch_draft_contact_method_added(self):
        self.note_2.contact_type = 'Phone'
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.select_contact_type(self.note_2)
        self.draft_notes_page.wait_for_draft_note_update(self.note_2)

    def test_batch_draft_contact_method_removed(self):
        self.note_2.contact_type = None
        self.draft_notes_page.select_contact_type(self.note_2)
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_2, manual_update=True)

    def test_batch_draft_privacy_setting_added(self):
        self.note_2.is_private = True
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.set_note_privacy(self.note_2)
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_2, manual_update=True)

    def test_batch_draft_privacy_setting_removed(self):
        self.note_2.is_private = False
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.set_note_privacy(self.note_2)
        self.draft_notes_page.wait_for_draft_note_update(self.note_2)

    def test_batch_draft_single_student_removed(self):
        self.draft_notes_page.remove_students_from_batch(self.note_2, [self.student])
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_2, manual_update=True)

    def test_batch_draft_multiple_students_not_saved(self):
        students = self.test.students[0:2]
        self.draft_notes_page.click_draft_subject(self.note_2)
        self.draft_notes_page.add_students_to_batch(self.note_2, students)
        self.draft_notes_page.wait_for_draft_students_warning_msg()
        self.draft_notes_page.remove_students_from_batch(self.note_2, students)
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_2, manual_update=True)

    # VIEWING

    # As an admin

    def test_admin_draft_notes_page(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth()
        self.homepage.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_1)
        self.draft_notes_page.wait_for_draft_row(self.note_2)
        visible_note_1_subj = self.draft_notes_page.visible_draft_subject(self.note_1)
        expected_note_1_subject = self.draft_notes_page.expected_draft_note_subject(self.note_1)
        utils.assert_actual_includes_expected(visible_note_1_subj, expected_note_1_subject)
        visible_note_2_subj = self.draft_notes_page.visible_draft_subject(self.note_2)
        expected_note_2_subject = self.draft_notes_page.expected_draft_note_subject(self.note_2)
        utils.assert_actual_includes_expected(visible_note_2_subj, expected_note_2_subject)

    def test_admin_draft_student_page(self):
        self.draft_notes_page.click_draft_student_link(self.note_1)
        self.student_page.when_present(self.student_page.collapsed_item_loc(self.note_1), utils.get_short_timeout())
        visible = self.student_page.visible_collapsed_note_data(self.note_1)
        utils.assert_equivalence(visible['subject'], self.student_page.expected_draft_note_subject(self.note_1))
        assert visible['is_draft']

    # As advisor who is not the author

    def test_non_author_advisor_drafts_page(self):
        self.student_page.log_out()
        self.homepage.dev_auth(self.other_advisor)
        self.homepage.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_2)
        assert not self.draft_notes_page.is_present(self.draft_notes_page.draft_row_loc(self.note_1))

    def test_non_author_advisor_student_page(self):
        self.student_page.load_page(self.student)
        self.student_page.when_present(self.student_page.NOTES_BUTTON, utils.get_short_timeout())
        assert not self.student_page.is_present(self.student_page.collapsed_item_loc(self.note_1))

    def test_non_author_advisor_student_api(self):
        api_ids = [n['id'] for n in self.api_student_page.student_notes(self.student)]
        assert self.note_1.record_id not in api_ids

    def test_non_author_advisor_attachment_api(self):
        attach_id = boa_utils.get_attachment_id_by_file_name(self.note_1, self.note_1.attachments[0])
        self.api_notes_page.load_attachment_page(attach_id)
        self.api_notes_page.when_present(self.api_notes_page.ATTACH_NOT_FOUND_MSG, utils.get_short_timeout())

    # An advisor who is the author

    def test_author_advisor_drafts_page(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(self.test.advisor)
        self.homepage.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_1)
        assert not self.draft_notes_page.is_present(self.draft_notes_page.draft_row_loc(self.note_2))
        visible_note_1_subj = self.draft_notes_page.visible_draft_subject(self.note_1)
        expected_note_1_subject = self.draft_notes_page.expected_draft_note_subject(self.note_1)
        utils.assert_actual_includes_expected(visible_note_1_subj, expected_note_1_subject)

    def test_author_advisor_student_page(self):
        self.draft_notes_page.click_draft_student_link(self.note_1)
        self.student_page.when_present(self.student_page.collapsed_item_loc(self.note_1), utils.get_short_timeout())
        visible = self.student_page.visible_collapsed_note_data(self.note_1)
        utils.assert_equivalence(visible['subject'], self.student_page.expected_draft_note_subject(self.note_1))
        assert visible['is_draft']

    # SEARCH

    def test_search_draft_setup(self):
        self.note_3.subject = f'Draft note 3 {self.test.test_id} subject'
        self.note_3.body = f'Draft note 3 {self.test.test_id} body'
        self.student_page.load_page(self.student)
        self.student_page.click_create_new_note()
        self.student_page.enter_new_note_subject(self.note_3)
        self.student_page.enter_note_body(self.note_3)
        self.student_page.add_topics(self.note_3, self.topics)
        self.student_page.click_save_as_draft()
        self.student_page.wait_for_draft_note(self.note_3, manual_update=True)
        self.student_page.log_out()

        self.homepage.dev_auth()
        self.api_admin_page.reindex_notes()
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(self.test.advisor)

    def test_search_draft_by_subject_yields_no_result(self):
        self.homepage.close_adv_search_if_open()
        self.homepage.enter_simple_search_and_hit_enter(self.note_3.subject)
        self.search_results_page.wait_for_no_results()

    def test_search_draft_by_body_yields_no_result(self):
        self.search_results_page.enter_simple_search_and_hit_enter(self.note_3.body)
        self.search_results_page.wait_for_no_results()

    def test_search_draft_by_topic_yields_no_result(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.select_note_topic(self.note_3.topics[0])
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_3.subject)
        self.search_results_page.wait_for_no_results()

    def test_search_draft_by_date_yields_no_result(self):
        start_date = self.note_3.created_date - timedelta(days=1)
        end_date = self.note_3.created_date
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.set_notes_date_range(start_date, end_date)
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_3.subject)
        self.search_results_page.wait_for_no_results()

    def test_search_draft_by_author_yields_no_result(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.set_notes_author(self.test.advisor.full_name, self.test.advisor.alt_names)
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_3.subject)
        self.search_results_page.wait_for_no_results()

    def test_search_draft_by_student_yields_no_result(self):
        self.search_results_page.reopen_and_reset_adv_search()
        self.search_results_page.set_notes_student(self.student)
        self.search_results_page.enter_adv_search_and_hit_enter(self.note_3.subject)
        self.search_results_page.wait_for_no_results()

    # DRAFT NOTES PAGE

    def test_list_view_draft_setup(self):
        self.search_results_page.click_create_note_batch()
        self.note_4.subject = f'Draft note 4 {self.test.test_id} subject'
        self.homepage.enter_new_note_subject(self.note_4)
        self.homepage.click_save_as_draft()
        self.homepage.wait_for_draft_note(self.note_4, manual_update=True)

        self.homepage.click_create_note_batch()
        self.note_5.subject = f'Draft note 5 {self.test.test_id} subject'
        self.note_5.body = f'Draft note 5 {self.test.test_id} body'
        self.note_5.set_date = datetime.strptime(self.today, '%Y-%m-%d') - timedelta(days=1)
        self.homepage.enter_new_note_subject(self.note_5)
        self.homepage.enter_note_body(self.note_5)
        self.homepage.add_students_to_batch(self.note_5, [self.student])
        self.homepage.enter_set_date(self.note_5)
        self.homepage.click_save_as_draft()
        self.homepage.wait_for_draft_note(self.note_5, manual_update=True)

        self.homepage.click_draft_notes()
        self.draft_notes_page.click_draft_subject(self.note_5)
        self.note_5.subject = None
        self.draft_notes_page.enter_new_note_subject(self.note_5)
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_note_update(self.note_5, manual_update=True)

        self.homepage.click_create_note_batch()
        self.note_6.subject = f'Draft note 6 {self.test.test_id} subject'
        self.homepage.enter_new_note_subject(self.note_6)
        self.homepage.add_students_to_batch(self.note_6, [self.student])
        self.homepage.add_attachments_to_new_note(self.note_6, self.attachments[1:2])
        self.homepage.click_save_as_draft()
        self.homepage.wait_for_draft_note(self.note_6, manual_update=True)

    # Advisor view

    def test_advisor_draft_list_view_ids(self):
        self.homepage.click_draft_notes()
        visible_ids = self.draft_notes_page.visible_draft_ids()
        assert str(self.note_1.record_id) in visible_ids
        assert str(self.note_2.record_id) not in visible_ids
        assert str(self.note_3.record_id) in visible_ids
        assert str(self.note_4.record_id) in visible_ids
        assert str(self.note_5.record_id) in visible_ids
        assert str(self.note_6.record_id) in visible_ids

    def test_advisor_draft_list_view_order(self):
        my_drafts = boa_utils.get_advisor_note_drafts(self.test.advisor)
        my_drafts.sort(key=lambda d: d.updated_date, reverse=True)
        expected_ids = [str(d.record_id) for d in my_drafts]
        visible_ids = self.draft_notes_page.visible_draft_ids()
        utils.assert_equivalence(visible_ids, expected_ids)

    def test_advisor_draft_list_view_students(self):
        utils.assert_equivalence(self.draft_notes_page.visible_draft_student(self.note_4),
                                 '—')
        utils.assert_equivalence(self.draft_notes_page.visible_draft_student(self.note_5),
                                 f'{self.student.first_name} {self.student.last_name}')
        utils.assert_equivalence(self.draft_notes_page.visible_draft_student(self.note_6),
                                 f'{self.student.first_name} {self.student.last_name}')

    def test_advisor_draft_list_view_sids(self):
        utils.assert_equivalence(self.draft_notes_page.visible_draft_sid(self.note_4), '—')
        utils.assert_equivalence(self.draft_notes_page.visible_draft_sid(self.note_5), str(self.student.sid))
        utils.assert_equivalence(self.draft_notes_page.visible_draft_sid(self.note_6), str(self.student.sid))

    def test_advisor_draft_list_view_subjects(self):
        utils.assert_equivalence(self.draft_notes_page.visible_draft_subject(self.note_4), self.note_4.subject)
        utils.assert_equivalence(self.draft_notes_page.visible_draft_subject(self.note_5), '[DRAFT NOTE]')
        utils.assert_equivalence(self.draft_notes_page.visible_draft_subject(self.note_6), self.note_6.subject)

    def test_advisor_draft_list_view_dates(self):
        today = datetime.today().strftime('%b %-d')
        utils.assert_actual_includes_expected(self.draft_notes_page.visible_draft_date(self.note_4, self.test.advisor),
                                              today)
        utils.assert_actual_includes_expected(self.draft_notes_page.visible_draft_date(self.note_5, self.test.advisor),
                                              today)
        utils.assert_actual_includes_expected(self.draft_notes_page.visible_draft_date(self.note_6, self.test.advisor),
                                              today)

    def test_advisor_draft_list_view_student_links(self):
        self.draft_notes_page.click_draft_student_link(self.note_5)
        self.student_page.wait_for_spinner()
        self.student_page.wait_for_boa_title(f'{self.student.first_name} {self.student.last_name}')

    def test_advisor_draft_list_view_edit_modal(self):
        self.student_page.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_4)
        self.draft_notes_page.click_draft_subject(self.note_4)
        self.draft_notes_page.when_present(self.draft_notes_page.EDIT_DRAFT_HEADING, 3)
        self.draft_notes_page.click_save_as_draft()

    # Admin view

    def test_admin_draft_list_view_ids(self):
        self.draft_notes_page.log_out()
        self.homepage.dev_auth()
        self.homepage.click_draft_notes()
        visible_ids = self.draft_notes_page.visible_draft_ids()
        assert str(self.note_1.record_id) in visible_ids
        assert str(self.note_2.record_id) in visible_ids
        assert str(self.note_3.record_id) in visible_ids
        assert str(self.note_4.record_id) in visible_ids
        assert str(self.note_5.record_id) in visible_ids
        assert str(self.note_6.record_id) in visible_ids

    def test_admin_draft_list_view_order(self):
        all_drafts = boa_utils.get_advisor_note_drafts()
        all_drafts.sort(key=lambda d: d.updated_date, reverse=True)
        expected_ids = [str(d.record_id) for d in all_drafts]
        visible_ids = self.draft_notes_page.visible_draft_ids()
        utils.assert_equivalence(visible_ids, expected_ids)

    def test_admin_draft_list_view_students(self):
        utils.assert_equivalence(self.draft_notes_page.visible_draft_student(self.note_4),
                                 '—')
        utils.assert_equivalence(self.draft_notes_page.visible_draft_student(self.note_5),
                                 f'{self.student.first_name} {self.student.last_name}')
        utils.assert_equivalence(self.draft_notes_page.visible_draft_student(self.note_6),
                                 f'{self.student.first_name} {self.student.last_name}')

    def test_admin_draft_list_view_sids(self):
        utils.assert_equivalence(self.draft_notes_page.visible_draft_sid(self.note_4), '—')
        utils.assert_equivalence(self.draft_notes_page.visible_draft_sid(self.note_5), str(self.student.sid))
        utils.assert_equivalence(self.draft_notes_page.visible_draft_sid(self.note_6), str(self.student.sid))

    def test_admin_draft_list_view_subjects(self):
        utils.assert_equivalence(self.draft_notes_page.visible_draft_subject(self.note_4), self.note_4.subject)
        utils.assert_equivalence(self.draft_notes_page.visible_draft_subject(self.note_5), '[DRAFT NOTE]')
        utils.assert_equivalence(self.draft_notes_page.visible_draft_subject(self.note_6), self.note_6.subject)

    def test_admin_draft_list_view_authors(self):
        visible_note_4_author = self.draft_notes_page.visible_draft_author(self.note_4, self.test.admin).lower()
        visible_note_5_author = self.draft_notes_page.visible_draft_author(self.note_5, self.test.admin).lower()
        visible_note_6_author = self.draft_notes_page.visible_draft_author(self.note_6, self.test.admin).lower()
        utils.assert_equivalence(visible_note_4_author, self.test.advisor.full_name.lower())
        utils.assert_equivalence(visible_note_5_author, self.test.advisor.full_name.lower())
        utils.assert_equivalence(visible_note_6_author, self.test.advisor.full_name.lower())

    def test_admin_draft_list_view_dates(self):
        today = datetime.today().strftime('%b %-d')
        utils.assert_actual_includes_expected(self.draft_notes_page.visible_draft_date(self.note_4, self.test.admin),
                                              today)
        utils.assert_actual_includes_expected(self.draft_notes_page.visible_draft_date(self.note_5, self.test.admin),
                                              today)
        utils.assert_actual_includes_expected(self.draft_notes_page.visible_draft_date(self.note_6, self.test.admin),
                                              today)

    def test_admin_draft_list_view_student_links(self):
        self.draft_notes_page.click_draft_student_link(self.note_5)
        self.student_page.wait_for_spinner()
        self.student_page.wait_for_boa_title(f'{self.student.first_name} {self.student.last_name}')

    def test_admin_no_draft_list_view_edit_modal(self):
        self.student_page.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_4)
        assert not self.draft_notes_page.is_present(self.draft_notes_page.draft_subject_button_loc(self.note_4))

    # DIRECTOR / ADMIN PERMISSIONS

    def test_convert_advisor_to_director(self):
        director_dept_membership = DepartmentMembership(
            dept=Department.L_AND_S,
            advisor_role=AdvisorRole.DIRECTOR,
            is_automated=True,
        )
        self.other_advisor.dept_memberships = [director_dept_membership]
        self.pax_manifest_page.load_page()
        self.pax_manifest_page.search_for_advisor(self.other_advisor)
        self.pax_manifest_page.edit_user(self.other_advisor)

    def test_director_cannot_see_drafts(self):
        self.pax_manifest_page.log_out()
        self.homepage.dev_auth(self.other_advisor)
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        assert self.note_5.record_id not in self.student_page.visible_collapsed_note_ids()

    def test_director_cannot_download_drafts(self):
        self.student_page.download_notes(self.student)
        assert not self.student_page.verify_note_in_export_csv(self.student, self.note_5, self.other_advisor)
        assert not self.student_page.verify_note_in_export_csv(self.student, self.note_6, self.other_advisor)

    def test_admin_cannot_download_drafts(self):
        self.student_page.log_out()
        self.homepage.dev_auth()
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        self.student_page.download_notes(self.student)
        assert not self.student_page.verify_note_in_export_csv(self.student, self.note_5, self.other_advisor)
        assert not self.student_page.verify_note_in_export_csv(self.student, self.note_6, self.other_advisor)

    # DRAFT EDITING

    # Student page

    def test_convert_advisor_to_ce3(self):
        ce3_dept_membership = DepartmentMembership(
            dept=Department.ZCEEE,
            advisor_role=AdvisorRole.ADVISOR,
            is_automated=True,
        )
        self.other_advisor.dept_memberships = [ce3_dept_membership]
        self.pax_manifest_page.load_page()
        self.pax_manifest_page.search_for_advisor(self.other_advisor)
        self.pax_manifest_page.edit_user(self.other_advisor)

    def test_admin_cannot_edit_drafts(self):
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_5)
        assert not self.student_page.is_present(self.student_page.edit_note_button_loc(self.note_5))

    def test_edit_draft_setup(self):
        self.student_page.log_out()
        self.homepage.dev_auth(self.test.advisor)
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_5)

        self.note_5.subject = f'{self.note_5.subject} EDITED'
        self.note_5.body = f'{self.note_5.body} EDITED'
        self.note_5.set_date = datetime.strptime(self.today, '%Y-%m-%d')
        self.note_5.contact_type = 'Phone'
        self.note_5.is_private = True

        self.student_page.click_edit_note_button(self.note_5)
        self.student_page.enter_edit_note_subject(self.note_5)
        self.student_page.enter_note_body(self.note_5)
        self.student_page.select_contact_type(self.note_5)
        self.student_page.set_note_privacy(self.note_5)
        self.student_page.add_topics(self.note_5, [Topic(Topics.ACADEMIC_PROGRESS.value)])
        self.student_page.enter_set_date(self.note_5)
        self.student_page.click_update_note_draft()
        self.student_page.add_attachments_to_existing_note(self.note_5, [self.attachments[0]])

    def test_edit_draft_saves_draft_state(self):
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        utils.assert_existence(self.student_page.collapsed_note_is_draft(self.note_5))

    def test_edit_draft_saves_subject(self):
        utils.assert_equivalence(self.student_page.collapsed_note_subject(self.note_5), self.note_5.subject)

    def test_edit_draft_saves_body(self):
        self.student_page.expand_item(self.note_5)
        utils.assert_equivalence(self.student_page.expanded_note_body(self.note_5), self.note_5.body)

    def test_edit_draft_saves_attachments(self):
        expected = [a.file_name for a in self.note_5.attachments]
        utils.assert_equivalence(self.student_page.expanded_note_attachments(self.note_5), expected)

    def test_edit_draft_saves_topics(self):
        expected = [t.name.upper() for t in self.note_5.topics]
        utils.assert_equivalence(self.student_page.expanded_note_topics(self.note_5), expected)

    def test_edit_draft_saves_set_date(self):
        expected = self.student_page.expected_item_short_date_format(self.note_5.set_date)
        utils.assert_equivalence(self.student_page.expanded_note_set_date(self.note_5), expected)

    def test_edit_draft_saves_contact_method(self):
        utils.assert_equivalence(self.student_page.expanded_note_contact_type(self.note_5), self.note_5.contact_type)

    # Batch note edit modal

    def test_edit_batch_draft_setup(self):
        self.student_page.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_4)
        self.draft_notes_page.click_draft_subject(self.note_4)

        self.note_4.subject = f'{self.note_4.subject} EDITED'
        self.note_4.body = f'Draft note 4 {self.test.test_id} body'
        self.note_4.set_date = datetime.strptime(self.today, '%Y-%m-%d') - timedelta(days=1)
        self.note_4.contact_type = 'Admin'
        self.note_4.is_private = True

        self.draft_notes_page.add_students_to_batch(self.note_4, [self.student])
        self.draft_notes_page.enter_new_note_subject(self.note_4)
        self.draft_notes_page.enter_note_body(self.note_4)
        self.draft_notes_page.select_contact_type(self.note_4)
        self.draft_notes_page.set_note_privacy(self.note_4)
        self.draft_notes_page.add_topics(self.note_4, [Topic(Topics.CHANGE_OF_COLLEGE.value)])
        self.draft_notes_page.add_attachments_to_new_note(self.note_4, [self.attachments[0]])
        self.draft_notes_page.enter_set_date(self.note_4)
        self.draft_notes_page.click_save_as_draft()
        self.draft_notes_page.wait_for_draft_row(self.note_4)

        self.draft_notes_page.click_draft_student_link(self.note_4)
        self.student_page.show_notes()

    def test_edit_batch_draft_saved_as_draft(self):
        assert self.student_page.collapsed_note_is_draft(self.note_4)

    def test_edit_batch_draft_subject(self):
        utils.assert_equivalence(self.student_page.collapsed_note_subject(self.note_4), self.note_4.subject)

    def test_edit_batch_draft_body(self):
        self.student_page.expand_item(self.note_4)
        utils.assert_equivalence(self.student_page.expanded_note_body(self.note_4), self.note_4.body)

    def test_edit_batch_draft_attachments(self):
        expected = [att.file_name for att in self.note_4.attachments]
        utils.assert_equivalence(self.student_page.expanded_note_attachments(self.note_4), expected)

    def test_edit_batch_draft_topics(self):
        expected = [topic.name.upper() for topic in self.note_4.topics]
        utils.assert_equivalence(self.student_page.expanded_note_topics(self.note_4), expected)

    def test_edit_batch_draft_set_date(self):
        expected = self.student_page.expected_item_short_date_format(self.note_4.set_date)
        utils.assert_equivalence(self.student_page.expanded_note_set_date(self.note_4), expected)

    def test_edit_batch_draft_contact_method(self):
        utils.assert_equivalence(self.student_page.expanded_note_contact_type(self.note_4), self.note_4.contact_type)

    # CONVERSION TO A NOTE

    def test_draft_to_note_conversion_on_student_page(self):
        self.student_page.click_edit_note_button(self.note_4)
        self.student_page.click_save_note_edit()
        self.note_4.is_draft = False
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        self.student_page.verify_note(self.note_4, self.test.advisor)

    def test_converted_draft_removed_from_drafts_page(self):
        self.student_page.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_5)
        assert not self.draft_notes_page.is_present(self.draft_notes_page.draft_row_loc(self.note_4))

    def test_batch_draft_to_notes(self):
        self.draft_notes_page.click_draft_subject(self.note_5)
        self.note_5.subject = f'Draft note 5 {self.test.test_id} subject'
        self.draft_notes_page.enter_new_note_subject(self.note_5)
        self.draft_notes_page.add_cohorts_to_batch(self.note_5, [self.cohort])
        self.draft_notes_page.add_groups_to_batch(self.note_5, [self.group])
        self.draft_notes_page.click_save_new_note()
        self.note_5.is_draft = False

    def test_converted_batch_draft_added_to_students(self):
        batch_students = self.draft_notes_page.unique_students_in_batch([self.student], [self.cohort], [self.group])
        expected_sids = [stu.sid for stu in batch_students]
        expected_sids.sort()
        # Give BOA a moment to make lotsa notes
        time.sleep(utils.get_short_timeout())
        actual_sids = boa_utils.get_note_sids_by_subject(self.note_5)
        missing = list(set(expected_sids) - set(actual_sids))
        unexpected = list(set(actual_sids) - set(expected_sids))
        app.logger.info(f'SIDS missing from batch: {missing}')
        app.logger.info(f'SIDS unexpected in batch: {unexpected}')
        assert not missing
        assert not unexpected

    def test_converted_batch_draft_removed_from_drafts_page(self):
        assert not self.draft_notes_page.is_present(self.draft_notes_page.draft_row_loc(self.note_5))

    def test_converted_batch_draft_added_with_right_content(self):
        batch_students = self.draft_notes_page.unique_students_in_batch([self.student], [self.cohort], [self.group])
        for student in batch_students[0:2]:
            self.student_page.set_new_note_id(self.note_5, student)
            self.student_page.load_page(student)
            self.student_page.verify_note(self.note_5, self.test.advisor)

    # DELETION

    def test_author_has_delete_draft_button_on_student_page(self):
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_6)
        assert self.student_page.is_present(self.student_page.delete_note_button_loc(self.note_6))

    def test_author_delete_draft_but_cancel(self):
        self.student_page.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_6)
        self.draft_notes_page.click_delete_draft(self.note_6)
        self.draft_notes_page.cancel_delete_or_discard()

    def test_author_delete_draft_and_confirm(self):
        self.draft_notes_page.click_delete_draft(self.note_6)
        self.draft_notes_page.confirm_delete_or_discard()
        assert self.note_6.record_id not in self.draft_notes_page.visible_draft_ids()

    def test_admin_delete_draft_on_student_page(self):
        self.draft_notes_page.log_out()
        self.homepage.dev_auth()
        self.student_page.load_page(self.student)
        self.student_page.show_notes()
        self.student_page.expand_item(self.note_1)
        self.student_page.delete_note(self.note_1)
        assert self.note_1.record_id not in self.student_page.visible_collapsed_note_ids()

    def test_admin_delete_draft_but_cancel(self):
        self.student_page.click_draft_notes()
        self.draft_notes_page.wait_for_draft_row(self.note_3)
        self.draft_notes_page.click_delete_draft(self.note_3)
        self.draft_notes_page.cancel_delete_or_discard()

    def test_admin_delete_draft_and_confirm(self):
        self.draft_notes_page.click_delete_draft(self.note_3)
        self.draft_notes_page.confirm_delete_or_discard()
        assert self.note_3.record_id not in self.draft_notes_page.visible_draft_ids()
