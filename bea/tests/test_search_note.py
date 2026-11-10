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
import datetime
import time
from datetime import timedelta

import pytest
from flask import current_app as app
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait

from bea.config.bea_test_config import BEATestConfig
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.models.notes_and_appts.topic import Topics
from bea.test_utils import nessie_timeline_utils, utils

test = BEATestConfig()
test.search_notes()
# Tests for Posted by Your Departments(s) will be found in the user_role_advisor test script


@pytest.mark.usefixtures('page_objects')
class TestLogin:

    def test_advisor_log_in(self):
        self.homepage.load_page()
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
        self.homepage.enter_simple_search(tc.search_string)
        self.homepage.click_simple_search_button()
        self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_matching_topics(self, tc):
        if tc.note.source in [TimelineRecordSource.ASC, TimelineRecordSource.DATA, TimelineRecordSource.HISTORY]:
            app.logger.info('Skipping topic search since note source is ASC, Data Science, or History, unable to search by topic')
        else:
            if tc.note.topics:
                all_topics = [t.value['name'].title() for t in Topics]
                if tc.note.topics[0] in all_topics:
                    self.homepage.reopen_and_reset_adv_search()
                    self.homepage.select_note_topic(tc.note.topics[0])
                    self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
                    if tc.note.is_private:
                        self.search_results_page.assert_note_result_not_present(tc.note)
                    else:
                        self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_non_matching_topics(self, tc):
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
            if tc.note.is_private:
                self.search_results_page.assert_note_result_not_present(tc.note)
            else:
                self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_posted_by_anyone_no_string(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.reset_adv_search()
        self.homepage.select_notes_posted_by_anyone()
        assert not self.homepage.element(self.homepage.ADV_SEARCH_BUTTON).is_enabled()

    def test_adv_search_matching_author(self, tc):
        if tc.note.advisor:
            if tc.note.advisor.uid == 'UCBCONVERSION':
                app.logger.info('Skipping note author search since UID is UCBCONVERSION')
            else:
                author = nessie_timeline_utils.get_advising_note_author(tc.note.advisor.uid)
                if author and author.first_name and author.last_name:
                    name = f'{author.first_name} {author.last_name}'
                    self.homepage.reopen_and_reset_adv_search()
                    self.homepage.set_notes_author(name)
                    self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
                    if tc.note.is_private:
                        self.search_results_page.assert_note_result_not_present(tc.note)
                    else:
                        self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_non_matching_author(self, tc):
        if tc.note.advisor:
            authors = nessie_timeline_utils.get_all_advising_note_authors()
            author = next(filter(lambda a: a.uid != tc.note.advisor.uid, authors))
            if author and author.first_name and author.last_name:
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
        if tc.note.is_private:
            self.search_results_page.assert_note_result_not_present(tc.note)
        else:
            self.search_results_page.assert_note_result_present(tc.note)

    def test_search_result_name(self, tc):
        if not tc.note.is_private:
            utils.assert_equivalence(self.search_results_page.note_result_student_name(tc.note), tc.student.full_name)

    def test_search_result_sid(self, tc):
        if not tc.note.is_private:
            utils.assert_equivalence(self.search_results_page.note_result_sid(tc.student, tc.note), tc.student.sid)

    def test_search_result_date(self, tc):
        if not tc.note.is_private:
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
        if tc.note.is_private:
            self.search_results_page.assert_note_result_not_present(tc.note)
        else:
            self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_matching_date_past_range(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.set_notes_date_range(date_from=(tc.note.updated_date - timedelta(days=1)),
                                           date_to=tc.note.updated_date)
        self.homepage.click_adv_search_button()
        if tc.note.is_private:
            self.search_results_page.assert_note_result_not_present(tc.note)
        else:
            self.search_results_page.assert_note_result_present(tc.note)

    def test_adv_search_non_matching_date_past_range(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.set_notes_date_range(date_from=(tc.note.updated_date - timedelta(days=30)),
                                           date_to=(tc.note.updated_date - timedelta(days=1)))
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_note_result_not_present(tc.note)

    def test_adv_search_non_matching_date_future_range(self, tc):
        if tc.note.updated_date + timedelta(days=30) < utils.date_to_local_tz(datetime.datetime.now()):
            self.homepage.reopen_and_reset_adv_search()
            self.homepage.set_notes_student(tc.student)
            self.homepage.set_notes_date_range(date_from=(tc.note.updated_date + timedelta(days=1)),
                                               date_to=(tc.note.updated_date + timedelta(days=30)))
            self.homepage.enter_adv_search(tc.search_string)
            self.homepage.click_adv_search_button()
            self.search_results_page.assert_note_result_not_present(tc.note)


@pytest.mark.usefixtures('page_objects')
class TestSearchNoteOrder:

    # Search ranks a stronger text match above a weaker one, and a newer match above an older one of the same strength.
    # These tests create their own notes so that the expected order doesn't depend on other data in the environment. The
    # timestamp in the search phrase keeps every other note out of the results.
    unique_id = str(int(time.time()))
    phrase = f'zephyr quartz {unique_id}'
    student = test.test_students[0]
    exact_note = Note({'advisor': test.advisor})
    loose_note = Note({'advisor': test.advisor})

    # The recency test copies the search string of an existing note at least two years old into a new note. At that age
    # the old note's ranking is cut by more than half, so the new note should come first even though both match exactly.
    old = next(
        (
            tc for tc in test.test_cases
            if not tc.note.is_private
            and tc.note.created_date
            and tc.note.created_date < utils.date_to_local_tz(datetime.datetime.now()) - timedelta(days=730)
        ),
        None,
    )
    recent_note = Note({'advisor': test.advisor})

    def test_create_exact_match_note(self):
        self.student_page.load_page(self.student)
        self.exact_note.subject = f'Search order exact {self.unique_id}'
        self.exact_note.body = f'Discussed the {self.phrase} plan.'
        self.student_page.create_note(self.exact_note, [], [])
        self.student_page.verify_note(self.exact_note, test.advisor)

    def test_create_newer_loose_match_note(self):
        # Created after the exact match, so it is newer, but its words are not in phrase order.
        self.loose_note.subject = f'Search order loose {self.unique_id}'
        self.loose_note.body = 'The plan covers quartz first and zephyr later.'
        self.student_page.create_note(self.loose_note, [], [])
        self.student_page.verify_note(self.loose_note, test.advisor)

    def test_exact_match_ranked_above_newer_loose_match(self):
        nessie_timeline_utils.wait_for_cdc_upsert(self.exact_note.record_id, 'create')
        nessie_timeline_utils.wait_for_cdc_upsert(self.loose_note.record_id, 'create')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(self.phrase)
        result_ids = self.search_results_page.note_search_result_ids()
        utils.assert_equivalence(result_ids, [self.exact_note.record_id, self.loose_note.record_id])

    def test_loose_match_ranked_below_exact_match_in_adv_search(self):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(self.student)
        self.homepage.enter_adv_search_and_hit_enter(self.phrase)
        result_ids = self.search_results_page.note_search_result_ids()
        utils.assert_equivalence(result_ids, [self.exact_note.record_id, self.loose_note.record_id])

    def test_create_recent_copy_of_old_note(self):
        if self.old:
            app.logger.info(f'Copying search string of note {self.old.note.record_id}: {self.old.search_string}')
            self.student_page.load_page(self.old.student)
            self.recent_note.subject = f'Search order recent {self.unique_id}'
            self.recent_note.body = self.old.search_string
            self.student_page.create_note(self.recent_note, [], [])
            self.student_page.verify_note(self.recent_note, test.advisor)
        else:
            app.logger.info('Skipping recency test since no test note is at least two years old')

    def test_newer_match_ranked_above_older_match(self):
        if self.old:
            nessie_timeline_utils.wait_for_cdc_upsert(self.recent_note.record_id, 'create')
            self.homepage.load_page()
            self.homepage.enter_simple_search_and_hit_enter(self.old.search_string)
            result_ids = self.search_results_page.note_search_result_ids()
            assert result_ids
            utils.assert_equivalence(result_ids[0], self.recent_note.record_id)
            # The old note may be past the first page of results; when it is listed, it must come after the new one.
            if self.old.note.record_id in result_ids:
                assert result_ids.index(self.old.note.record_id) > result_ids.index(self.recent_note.record_id)

    def test_delete_search_order_notes(self):
        # Advisors can't delete notes, so the admin removes the notes these tests created.
        self.homepage.switch_user()
        notes = [(self.exact_note, self.student), (self.loose_note, self.student)]
        if self.old:
            notes.append((self.recent_note, self.old.student))
        for note, student in notes:
            if note.record_id:
                self.student_page.load_page(student)
                self.student_page.show_notes()
                self.student_page.expand_item(note)
                self.student_page.delete_note(note)
                Wait(self.driver, utils.get_short_timeout()).until(
                    ec.invisibility_of_element_located(self.student_page.collapsed_item_loc(note)),
                )
