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

from datetime import timedelta

from bea.config.bea_test_config import BEATestConfig
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.models.notes_and_appts.topic import Topics
from bea.test_utils import nessie_timeline_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest


test = BEATestConfig()
test.search_notes()
# Tests for Posted by Your Departments(s) will be found in the user_role_advisor test script


@pytest.mark.usefixtures('page_objects')
class TestLogin:

    def test_reindex_notes(self):
        self.homepage.load_page()
        self.homepage.dev_auth()
        self.api_admin_page.reindex_notes()

    def test_advisor_log_in(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(test.advisor)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=test.test_cases,
                         ids=[tc.test_case_id for tc in test.test_cases],
                         scope='class')
class TestSearchNote:

    def test_simple_search(self, tc):
        app.logger.info(f'Begin tests with UID {tc.student.uid} note {tc.note.record_id} string {tc.search_string}')
        self.homepage.load_page()
        self.homepage.close_adv_search_if_open()
        self.homepage.enter_simple_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_matching_topics(self, tc):
        if tc.note.source in [TimelineRecordSource.ASC, TimelineRecordSource.DATA]:
            app.logger.info('Skipping topic search since note source is ASC or Data Science, unable to search by topic')
        else:
            if tc.note.topics:
                all_topics = [t.value['name'].title() for t in Topics]
                if tc.note.topics[0] in all_topics:
                    self.homepage.reopen_and_reset_adv_search()
                    self.homepage.select_note_topic(tc.note.topics[0])
                    self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
                    self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_non_matching_topics(self, tc):
        if tc.note.source in [TimelineRecordSource.ASC, TimelineRecordSource.DATA]:
            app.logger.info('Skipping topic search since note source is ASC or Data Science, unable to search by topic')
        else:
            all_topics = [t.value['name'].title() for t in Topics]
            note_topics = [t for t in all_topics if t in tc.note.topics]
            non_note_topics = list(set(all_topics) - set(note_topics))
            self.homepage.reopen_and_reset_adv_search()
            self.homepage.select_note_topic(non_note_topics[0])
            self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
            self.search_results_page.assert_note_result_not_present(tc.note)

    def test_adv_search_posted_by_you(self, tc):
        if tc.note.advisor:
            if tc.note.advisor.uid == 'UCBCONVERSION':
                app.logger.info('Skipping note author search since UID is UCBCONVERSION')
            else:
                self.homepage.reopen_and_reset_adv_search()
                self.homepage.select_notes_posted_by_you()
                self.homepage.enter_adv_search(tc.search_string)
                self.homepage.click_adv_search_button()
                if tc.note.advisor.uid == test.advisor.uid:
                    self.search_results_page.assert_note_result_present(tc.note)
                else:
                    self.search_results_page.assert_note_result_not_present(tc.note)

    def test_adv_search_posted_by_anyone(self, tc):
        if tc.note.advisor:
            self.homepage.reopen_and_reset_adv_search()
            self.homepage.select_notes_posted_by_anyone()
            self.homepage.enter_adv_search(tc.search_string)
            self.homepage.click_adv_search_button()
            self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_posted_by_anyone_no_string(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.reset_adv_search()
        self.homepage.select_notes_posted_by_anyone()
        assert not self.homepage.element(self.homepage.ADV_SEARCH_BUTTON).is_enabled()

    def test_adv_search_matching_author(self, tc):
        if tc.note.advisor:
            author = nessie_timeline_utils.get_advising_note_author(tc.note.advisor.uid)
            if author:
                name = f'{author.first_name} {author.last_name}'
                self.homepage.reopen_and_reset_adv_search()
                self.homepage.set_notes_author(name)
                self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
                self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_non_matching_author(self, tc):
        if tc.note.advisor:
            authors = nessie_timeline_utils.get_all_advising_note_authors()
            author = next(filter(lambda a: a.uid != tc.note.advisor.uid, authors))
            author_name = f'{author.first_name} {author.last_name}'
            self.search_results_page.reopen_and_reset_adv_search()
            self.homepage.set_notes_author(author_name)
            self.homepage.enter_adv_search(tc.search_string)
            self.homepage.click_adv_search_button()
            self.search_results_page.assert_note_result_not_present(tc.note)

    def test_adv_search_matching_student(self, tc):
        self.search_results_page.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_note_result_present(tc.note)

    def test_search_result_name(self, tc):
        utils.assert_equivalence(self.search_results_page.note_result_student_name(tc.note), tc.student.full_name)

    def test_search_result_sid(self, tc):
        utils.assert_equivalence(self.search_results_page.note_result_sid(tc.student, tc.note), tc.student.sid)

    def test_search_result_date(self, tc):
        show_update_date = self.student_page.is_updated_date_expected(tc.note)
        expected_date = tc.note.set_date or (tc.note.updated_date if show_update_date else tc.note.created_date)
        expected = self.search_results_page.expected_note_or_appt_date_format(expected_date)
        utils.assert_equivalence(self.search_results_page.note_result_date(tc.note), expected)

    def test_adv_search_matching_date_future_range(self, tc):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.set_notes_date_range(date_from=tc.note.updated_date,
                                           date_to=(tc.note.updated_date + timedelta(days=1)))
        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_matching_date_past_range(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.set_notes_date_range(date_from=(tc.note.updated_date - timedelta(days=1)),
                                           date_to=tc.note.updated_date)
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_non_matching_date_past_range(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.set_notes_date_range(date_from=(tc.note.updated_date - timedelta(days=30)),
                                           date_to=(tc.note.updated_date - timedelta(days=1)))
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_note_result_not_present(tc.note)

    def test_adv_search_non_matching_date_future_range(self, tc):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.set_notes_date_range(date_from=(tc.note.updated_date + timedelta(days=1)),
                                           date_to=(tc.note.updated_date + timedelta(days=30)))
        self.homepage.enter_adv_search(tc.search_string)
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_note_result_not_present(tc.note)
