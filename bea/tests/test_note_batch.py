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

import random

from bea.config.bea_test_config import BEATestConfig
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.models.notes_and_appts.note_batch import NoteBatch
from bea.models.notes_and_appts.topic import Topic
from bea.models.notes_and_appts.topic import Topics
from bea.test_utils import boa_utils
from flask import current_app as app
import pytest


@pytest.mark.usefixtures('page_objects')
class TestNoteBatch:

    test = BEATestConfig()
    test.note_batch()

    batch_note_1 = NoteBatch({'advisor': test.advisor, 'subject': f'Batch note 1 subject {test.test_id}'})
    batch_note_2 = NoteBatch({'advisor': test.advisor, 'subject': f'Batch note 2 subject {test.test_id}'})
    batch_notes = [batch_note_1, batch_note_2]

    random.shuffle(test.students)
    students = test.students[0:9]
    bulk_batch_students_1 = test.students[0:49]
    bulk_batch_students_2 = test.students[50:99]

    cohorts = []

    groups = []
    group_members = test.students[-50:]
    group_1 = Cohort({'name': f'Group 1 {test.test_id}'})
    group_2 = Cohort({'name': f'Group 2 {test.test_id}'})

    def test_delete_cohorts_and_groups(self):
        self.homepage.load_page()
        self.homepage.dev_auth(self.test.advisor)

        pre_existing_cohorts = boa_utils.get_user_filtered_cohorts(self.test.advisor)
        for c in pre_existing_cohorts:
            self.filtered_students_page.load_and_delete_cohort(c)
        pre_existing_groups = boa_utils.get_user_curated_groups(self.test.advisor)
        for g in pre_existing_groups:
            self.curated_students_page.load_and_delete_group(g)

        self.homepage.click_create_note_batch()
        self.homepage.wait_for_student_input()

    def test_no_cohort_select_if_no_cohorts(self):
        assert not self.homepage.is_present(self.homepage.BATCH_COHORT_SELECT)

    def test_no_group_select_if_no_groups(self):
        assert not self.homepage.is_present(self.homepage.BATCH_GROUP_SELECT)

    def test_create_cohort(self):
        self.homepage.load_page()
        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(self.test.default_cohort)
        self.filtered_students_page.create_new_cohort(self.test.default_cohort)
        self.cohorts.append(self.test.default_cohort)

    def test_create_groups(self):
        for group in [self.group_1, self.group_2]:
            self.homepage.click_sidebar_create_student_group()
            self.curated_students_page.create_group_with_bulk_sids(group, self.group_members)
            self.groups.append(group)

    def test_no_batch_if_no_subject(self):
        self.homepage.click_create_note_batch()
        self.homepage.when_present(self.homepage.NEW_NOTE_SAVE_BUTTON, 1)
        assert not self.homepage.element(self.homepage.NEW_NOTE_SAVE_BUTTON).is_enabled()

    def test_cancel_batch(self):
        self.homepage.click_cancel_new_note()
        self.homepage.when_not_present(self.homepage.NEW_NOTE_SAVE_BUTTON, 1)

    def test_add_comma_separated_sids(self):
        self.homepage.click_create_note_batch()
        self.homepage.add_comma_sep_sids_to_batch(self.bulk_batch_students_1)

    def test_add_space_separated_sids(self):
        self.homepage.add_space_sep_sids_to_batch(self.bulk_batch_students_2)

    def test_add_cohorts(self):
        self.homepage.click_cancel_new_note()
        self.homepage.confirm_delete_or_discard()
        self.homepage.click_create_note_batch()
        self.homepage.add_cohorts_to_batch(self.batch_note_1, self.cohorts)

    def test_add_students(self):
        # TODO - remove the following once the auto-suggest behaves itself
        self.homepage.add_space_sep_sids_to_batch(self.students)
        for student in self.students:
            self.homepage.append_student_to_batch(self.batch_note_1, student)
        # TODO - use the following once the auto-suggest behaves itself
        # self.homepage.add_students_to_batch(self.batch_note_1, self.students)

    def test_add_groups(self):
        self.homepage.add_groups_to_batch(self.batch_note_1, self.groups)

    def test_remove_students(self):
        self.homepage.remove_students_from_batch(self.batch_note_1, self.students)

    def test_remove_cohorts(self):
        self.homepage.remove_cohorts_from_batch(self.batch_note_1, self.cohorts)

    def test_remove_groups(self):
        self.homepage.remove_groups_from_batch(self.batch_note_1, self.groups)

    def test_one_student_required(self):
        self.homepage.enter_new_note_subject(self.batch_note_1)
        assert not self.homepage.element(self.homepage.NEW_NOTE_SAVE_BUTTON).is_enabled()

    def test_note_count_alert(self):
        # TODO - remove the following once the auto-suggest behaves itself
        self.homepage.add_space_sep_sids_to_batch(self.students)
        for student in self.students:
            self.homepage.append_student_to_batch(self.batch_note_1, student)
        # TODO - use the following once the auto-suggest behaves itself
        # self.homepage.add_students_to_batch(self.batch_note_1, self.students)
        self.homepage.add_cohorts_to_batch(self.batch_note_1, self.cohorts)
        self.homepage.add_groups_to_batch(self.batch_note_1, self.groups)
        self.homepage.verify_batch_note_alert(self.students, self.cohorts, self.groups)

    def test_delete_note_batch_draft(self):
        self.homepage.click_cancel_new_note()
        self.homepage.confirm_delete_or_discard()

    def test_create_batch_o_notes(self):
        topics = [Topic(Topics.ACADEMIC_PROGRESS.value), Topic(Topics.PROBATION.value)]
        attachments = self.test.attachments[0:1]
        self.homepage.create_note_batch(note_batch=self.batch_note_1,
                                        students=self.students,
                                        cohorts=self.cohorts,
                                        groups=self.groups,
                                        topics=topics,
                                        attachments=attachments)

    def test_batch_has_right_students(self):
        expected_students = self.homepage.unique_students_in_batch(self.students, self.cohorts, self.groups)
        expected_sids = list(map(lambda s: s.sid, expected_students))
        expected_sids.sort()
        actual_sids = boa_utils.get_note_sids_by_subject(self.batch_note_1)
        missing = list(set(expected_sids) - set(actual_sids))
        unexpected = list(set(actual_sids) - set(expected_sids))
        app.logger.info(f'Missing: {missing}. Unexpected: {unexpected}')
        assert not missing
        assert not unexpected

    def test_batch_has_right_note_content(self):
        studs = self.homepage.unique_students_in_batch(self.students, self.cohorts, self.groups)
        for student in studs[0:4]:
            self.student_page.set_new_note_id(self.batch_note_1, student)
            self.student_page.load_page(student)
            self.student_page.verify_note(self.batch_note_1, self.test.advisor)

    def test_batch_from_group(self):
        student = self.group_1.members[-1]
        self.student_page.load_page(student)
        self.student_page.create_note_batch(note_batch=self.batch_note_2,
                                            students=[],
                                            cohorts=[],
                                            groups=[self.group_1],
                                            topics=[],
                                            attachments=[])
        self.student_page.set_new_note_id(self.batch_note_2, student)
        self.student_page.verify_note(self.batch_note_2, self.test.advisor)

    def test_index_notes(self):
        self.student_page.log_out()
        self.homepage.dev_auth()
        self.api_admin_page.reindex_notes()
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(self.test.advisor)

    def test_search_batch_note_by_student_and_subject(self):
        student = self.homepage.unique_students_in_batch(self.students, self.cohorts, self.groups)[-1]
        self.homepage.set_new_note_id(self.batch_note_1, student)
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(student)
        self.homepage.enter_adv_search_and_hit_enter(self.batch_note_1.subject)
        assert self.search_results_page.is_note_in_search_result(self.batch_note_1, is_batch=True)
