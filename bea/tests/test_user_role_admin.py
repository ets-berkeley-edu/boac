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
import time

from bea.config.bea_test_config import BEATestConfig
from bea.models.department import Department
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.note_template import NoteTemplate
from bea.models.notes_and_appts.topic import Topic, Topics
from bea.test_utils import boa_utils
from bea.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestAdminUserRole:

    test = BEATestConfig()
    test.user_role_admin()
    alert = (f'This is a BEA service alert {test.test_id} ' * 10).strip()
    random.shuffle(test.students)
    student = test.students[0]
    topic = Topic({'name': f'Topic test {test.test_id}'})
    note = Note({'student': student, 'subject': f'Topic test {test.test_id}'})
    template = NoteTemplate({'title': f'Template {test.test_id}', 'subject': 'Template subj', 'body': 'Template body'})

    def test_admin_has_degree_checks_link(self):
        self.homepage.dev_auth()
        self.homepage.click_header_dropdown()
        self.homepage.when_present(self.homepage.DEGREE_CHECKS_LINK, 1)

    # EVERYONE'S COHORTS AND GROUPS

    def test_everyone_student_cohorts(self):
        all_student_cohorts = boa_utils.get_everyone_filtered_cohorts()
        self.homepage.hit_escape()
        self.homepage.click_view_everyone_cohorts()
        expected = [c.name for c in all_student_cohorts]
        expected.sort()
        visible = self.cohorts_all_page.visible_student_cohorts()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_everyone_admit_cohorts(self):
        all_admit_cohorts = boa_utils.get_everyone_filtered_cohorts(admits=True)
        expected = [c.name for c in all_admit_cohorts]
        expected.sort()
        visible = self.cohorts_all_page.visible_admit_cohorts()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_everyone_student_groups(self):
        all_student_groups = boa_utils.get_everyone_curated_groups()
        self.cohorts_all_page.click_view_everyone_groups()
        expected = [g.name for g in all_student_groups]
        expected.sort()
        visible = self.curated_all_page.visible_student_groups()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_everyone_admit_groups(self):
        all_admit_groups = boa_utils.get_everyone_curated_groups(admits=True)
        expected = [g.name for g in all_admit_groups]
        expected.sort()
        visible = self.curated_all_page.visible_admit_groups()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    # SERVICE ALERTS

    def test_post_service_alert(self):
        self.curated_all_page.click_flight_deck_link()
        self.flight_deck_page.unpost_service_alert()
        self.flight_deck_page.update_service_alert(self.alert)
        self.flight_deck_page.post_service_alert()
        self.flight_deck_page.when_visible(self.flight_deck_page.SERVICE_ALERT_BANNER, 2)
        utils.assert_equivalence(self.flight_deck_page.visible_service_alert(), self.alert)

    def test_updated_posted_service_alert(self):
        self.alert = f'UPDATE - {self.alert}'
        self.flight_deck_page.update_service_alert(self.alert)
        time.sleep(1)
        utils.assert_equivalence(self.flight_deck_page.visible_service_alert(), self.alert)

    def test_dismiss_service_alert(self):
        self.flight_deck_page.dismiss_service_alert()

    def test_unpost_service_alert(self):
        self.flight_deck_page.load_admin_page()
        self.flight_deck_page.when_visible(self.flight_deck_page.SERVICE_ALERT_BANNER, 2)
        self.flight_deck_page.unpost_service_alert()
        self.flight_deck_page.when_not_visible(self.flight_deck_page.SERVICE_ALERT_BANNER, 2)

    # NOTE TOPIC MANAGEMENT

    def test_new_note_topic_must_be_unique(self):
        existing_topic = Topic(Topics.ACADEMIC_DIFFICULTY.value)
        self.flight_deck_page.click_create_topic()
        self.flight_deck_page.enter_topic_label(existing_topic.name)
        expected = f"Sorry, the label '{existing_topic.name}' is assigned to an existing topic."
        utils.assert_equivalence(self.flight_deck_page.label_validation_error(), expected)
        assert not self.flight_deck_page.element(self.flight_deck_page.TOPIC_SAVE_BUTTON).is_enabled()

    def test_new_note_topic_max_chars(self):
        long_label = 'A long label ' * 4
        self.flight_deck_page.enter_topic_label(long_label[0:50])
        utils.assert_actual_includes_expected(self.flight_deck_page.label_length_error(), '0 left')

    def test_new_note_topic_cancel(self):
        self.flight_deck_page.click_cancel_topic()

    def test_new_note_topic_save(self):
        self.flight_deck_page.create_topic(self.topic)

    def test_search_topic(self):
        self.flight_deck_page.search_for_topic(self.topic)
        self.flight_deck_page.when_visible(self.flight_deck_page.topic_row(self.topic), 1)

    def test_topic_status(self):
        assert not self.flight_deck_page.is_topic_deleted(self.topic)
        utils.assert_equivalence(self.flight_deck_page.topic_in_notes_count(self.topic), '0')

    def test_note_and_template_setup(self):
        self.flight_deck_page.log_out()
        self.test.dept = Department.L_AND_S
        self.test.set_advisor()
        self.note.advisor = self.test.advisor
        self.homepage.dev_auth(self.test.advisor)
        self.homepage.click_create_note_batch()
        self.homepage.enter_new_note_subject(self.note)
        self.homepage.create_template(self.template, self.note)

    def test_topic_available_to_individual_note(self):
        self.student_page.load_page(self.student)
        self.student_page.click_create_new_note()
        utils.assert_actual_includes_expected(self.student_page.topic_options(), self.topic.name)

    def test_topic_available_to_batch_note(self):
        self.student_page.hit_escape()
        self.student_page.confirm_delete_or_discard()
        self.student_page.click_create_note_batch()
        utils.assert_actual_includes_expected(self.student_page.topic_options(), self.topic.name)

    def test_topic_available_to_template(self):
        self.student_page.click_templates_button()
        self.student_page.click_edit_template(self.template)
        utils.assert_actual_includes_expected(self.student_page.topic_options(), self.topic.name)

    def test_search_note_by_new_topic(self):
        self.student_page.load_page(self.student)
        self.student_page.create_note(self.note, topics=[self.topic], attachments=None)
        self.student_page.log_out()
        self.homepage.dev_auth()
        self.api_admin_page.reindex_notes()
        self.homepage.load_page()
        self.homepage.open_adv_search()
        self.homepage.select_note_topic(self.topic)
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_note_result_present(self.note)

    def test_topic_usage_count(self):
        self.search_results_page.log_out()
        self.homepage.dev_auth()
        self.homepage.click_flight_deck_link()
        self.flight_deck_page.search_for_topic(self.topic)
        utils.assert_equivalence(self.flight_deck_page.topic_in_notes_count(self.topic), '1')

    def test_delete_topic(self):
        self.flight_deck_page.delete_or_undelete_topic(self.topic)
        self.flight_deck_page.confirm_delete_or_discard()
        assert self.flight_deck_page.is_topic_deleted(self.topic)
        utils.assert_equivalence(self.flight_deck_page.topic_in_notes_count(self.topic), '1')

    def test_deleted_topic_not_available_to_individual_note(self):
        self.flight_deck_page.log_out()
        self.homepage.dev_auth(self.test.advisor)
        self.student_page.load_page(self.student)
        self.student_page.click_create_new_note()
        assert self.topic.name not in self.student_page.topic_options()

    def test_deleted_topic_not_available_to_batch_note(self):
        self.student_page.hit_escape()
        self.student_page.confirm_delete_or_discard()
        self.student_page.click_create_note_batch()
        assert self.topic.name not in self.student_page.topic_options()

    def test_deleted_topic_not_available_to_template(self):
        self.student_page.click_templates_button()
        self.student_page.click_edit_template(self.template)
        assert self.topic.name not in self.student_page.topic_options()

    def test_deleted_topic_notes_searchable(self):
        self.homepage.load_page()
        self.homepage.open_adv_search()
        self.homepage.select_note_topic(self.topic)
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_note_result_present(self.note)

    def test_undelete_topic(self):
        self.student_page.log_out()
        self.homepage.dev_auth()
        self.homepage.click_flight_deck_link()
        self.flight_deck_page.search_for_topic(self.topic)
        self.flight_deck_page.delete_or_undelete_topic(self.topic)
        assert not self.flight_deck_page.is_topic_deleted(self.topic)

    def test_undeleted_topic_available_to_individual_note(self):
        self.flight_deck_page.log_out()
        self.homepage.dev_auth(self.test.advisor)
        self.student_page.load_page(self.student)
        self.student_page.click_create_new_note()
        utils.assert_actual_includes_expected(self.student_page.topic_options(), self.topic.name)

    def test_undeleted_topic_available_to_batch_note(self):
        self.student_page.hit_escape()
        self.student_page.confirm_delete_or_discard()
        self.student_page.click_create_note_batch()
        utils.assert_actual_includes_expected(self.student_page.topic_options(), self.topic.name)

    def test_undeleted_topic_available_to_template(self):
        self.student_page.click_templates_button()
        self.student_page.click_edit_template(self.template)
        utils.assert_actual_includes_expected(self.student_page.topic_options(), self.topic.name)
