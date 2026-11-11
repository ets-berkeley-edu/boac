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

from bea.config.bea_test_config import BEATestConfig
from bea.models.notes_and_appts.note_comment import NoteComment
from bea.models.notes_and_appts.topic import Topics
from bea.test_utils import boa_utils, nessie_timeline_utils, utils

test = BEATestConfig()
test.search_appts()

comments_by_test_case = {}

def search_date(appt):
    # Date filters match an appointment on its updated date, except UCBCONVERSION appointments, which use the created
    # date; the SIS loader already sets those to the same value. YCBM appointments have no updated date, so their start
    # time stands in.
    return appt.updated_date or appt.created_date


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
class TestSearchAppointment:

    def test_simple_search(self, tc):
        app.logger.info(f'Begin tests with UID {tc.student.uid} appointment {tc.appt.record_id} string {tc.search_string}')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_appt_result_present(tc.appt)

    def test_adv_search_matching_topics(self, tc):
        if tc.appt.topics:
            all_topics = [t.value['name'].title() for t in Topics]
            if tc.appt.topics[0] in all_topics:
                self.homepage.reopen_and_reset_adv_search()
                self.homepage.select_note_topic(tc.appt.topics[0])
                self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
                self.search_results_page.assert_appt_result_present(tc.appt)

    def test_adv_search_non_matching_topics(self, tc):
        all_topics = [t.value['name'].title() for t in Topics]
        appt_topics = [t for t in all_topics if t in tc.appt.topics]
        non_appt_topics = list(set(all_topics) - set(appt_topics))
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.select_note_topic(non_appt_topics[0])
        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_appt_result_not_present(tc.appt)

    def test_adv_search_posted_by_you(self, tc):
        if tc.appt.advisor:
            self.homepage.reopen_and_reset_adv_search()
            self.homepage.select_notes_posted_by_you()
            self.homepage.enter_adv_search(tc.search_string)
            self.homepage.click_adv_search_button()
            if tc.appt.advisor.uid == test.advisor.uid:
                self.search_results_page.assert_appt_result_present(tc.appt)
            else:
                self.search_results_page.assert_appt_result_not_present(tc.appt)

    def test_adv_search_posted_by_anyone(self, tc):
        if tc.appt.advisor:
            self.homepage.reopen_and_reset_adv_search()
            self.homepage.select_notes_posted_by_anyone()
            self.homepage.enter_adv_search(tc.search_string)
            self.homepage.click_adv_search_button()
            self.search_results_page.assert_appt_result_present(tc.appt)

    def test_adv_search_matching_author(self, tc):
        if tc.appt.advisor:
            if tc.appt.advisor.uid == 'UCBCONVERSION':
                app.logger.info('Skipping appointment author search since UID is UCBCONVERSION')
            else:
                if not tc.appt.advisor.uid:
                    # Calendly hosts and YCBM advisors are linked to a UID only when the loch can match them to one.
                    app.logger.info(f'Skipping appointment author search since appointment {tc.appt.record_id} advisor has no UID')
                else:
                    author = nessie_timeline_utils.get_advising_note_author(tc.appt.advisor.uid)
                    if author and author.first_name and author.last_name:
                        name = f'{author.first_name} {author.last_name}'
                        self.homepage.reopen_and_reset_adv_search()
                        self.homepage.set_notes_author(name)
                        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
                        self.search_results_page.assert_appt_result_present(tc.appt)

    def test_adv_search_non_matching_author(self, tc):
        if tc.appt.advisor:
            if tc.appt.advisor.uid == 'UCBCONVERSION':
                app.logger.info('Skipping appointment author search since UID is UCBCONVERSION')
            else:
                authors = nessie_timeline_utils.get_all_advising_note_authors()
                author = next(filter(lambda a: a.uid != tc.appt.advisor.uid, authors))
                if author and author.first_name and author.last_name:
                    author_name = f'{author.first_name} {author.last_name}'
                    self.search_results_page.reopen_and_reset_adv_search()
                    self.homepage.set_notes_author(author_name)
                    self.homepage.enter_adv_search(tc.search_string)
                    self.homepage.click_adv_search_button()
                    self.search_results_page.assert_appt_result_not_present(tc.appt)

    def test_adv_search_matching_student(self, tc):
        self.search_results_page.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_appt_result_present(tc.appt)

    def test_search_result_name(self, tc):
        utils.assert_equivalence(self.search_results_page.appt_result_student_name(tc.appt), tc.student.full_name)

    def test_search_result_sid(self, tc):
        utils.assert_equivalence(self.search_results_page.appt_result_sid(tc.student, tc.appt), tc.student.sid)

    def test_search_result_date(self, tc):
        expected = self.search_results_page.expected_note_or_appt_date_format(tc.appt.created_date)
        utils.assert_equivalence(self.search_results_page.appt_result_date(tc.appt), expected)

    def test_adv_search_matching_date_future_range(self, tc):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.set_notes_date_range(date_from=search_date(tc.appt),
                                           date_to=(search_date(tc.appt) + timedelta(days=1)))
        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_appt_result_present(tc.appt)

    def test_adv_search_matching_date_past_range(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.set_notes_date_range(date_from=(search_date(tc.appt) - timedelta(days=1)),
                                           date_to=search_date(tc.appt))
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_appt_result_present(tc.appt)

    def test_adv_search_non_matching_date_past_range(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.set_notes_date_range(date_from=(search_date(tc.appt) - timedelta(days=30)),
                                           date_to=(search_date(tc.appt) - timedelta(days=1)))
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_appt_result_not_present(tc.appt)

    def test_adv_search_non_matching_date_future_range(self, tc):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.set_notes_date_range(date_from=(search_date(tc.appt) + timedelta(days=1)),
                                           date_to=(search_date(tc.appt) + timedelta(days=30)))
        self.homepage.enter_adv_search(tc.search_string)
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_appt_result_not_present(tc.appt)

    #COMMENTS

    def test_add_comment(self, tc):
        # The admin deletes each comment at the end of the previous test case, so log the advisor back in.
        self.homepage.switch_user(test.advisor)
        comment = NoteComment()
        comment.body = f"Comment on {tc.appt.source.value['name']} appointment {utils.get_test_identifier()}"
        self.student_page.load_page(tc.student)
        self.student_page.show_appts()
        self.student_page.expand_item(tc.appt)
        self.student_page.add_appt_comment(tc.appt, comment)
        matching = [c for c in boa_utils.get_appt_comments(tc.appt) if c.body == comment.body]
        assert len(matching) == 1
        comment.comment_id = matching[0].comment_id
        comments_by_test_case[tc.test_case_id] = comment

    def test_simple_search_comment(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        nessie_timeline_utils.wait_for_cdc_upsert(comment.comment_id, 'create', table_name='comments')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(comment.body)
        self.search_results_page.assert_appt_comment_result_present(comment)

    def test_adv_search_comment_matching_student(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.enter_adv_search_and_hit_enter(comment.body)
        self.search_results_page.assert_appt_comment_result_present(comment)

    def test_adv_search_comment_posted_by_you(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.select_notes_posted_by_you()
        self.homepage.enter_adv_search_and_hit_enter(comment.body)
        self.search_results_page.assert_appt_comment_result_present(comment)

    def test_comment_result_is_only_result(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(comment.body)
        utils.assert_equivalence(self.search_results_page.appt_search_result_ids(), [('comment', comment.comment_id)])

    def test_delete_comment(self, tc):
        # Admin removes the comment. The advisor then logs back in, so that the next test case runs as the advisor.
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.switch_user()
        self.student_page.load_page(tc.student)
        self.student_page.show_appts()
        self.student_page.expand_item(tc.appt)
        self.student_page.delete_appt_comment(tc.appt, comment)
        self.homepage.switch_user(test.advisor)

    def test_deleted_comment_not_in_search_results(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        nessie_timeline_utils.wait_for_cdc_upsert(comment.comment_id, 'delete', table_name='comments')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(comment.body)
        assert ('comment', comment.comment_id) not in self.search_results_page.appt_search_result_ids()


@pytest.mark.usefixtures('page_objects')
class TestSearchApptOrder:

    # Search ranks a stronger text match above a weaker one, and a newer match above an older one of the same strength.
    unique_id = str(int(time.time()))
    phrase = f'zephyr quartz {unique_id}'
    tc = test.test_cases[0]
    exact_comment = NoteComment()
    loose_comment = NoteComment()

    # The mixed-results tests use an existing appointment at least two years old. A new comment that copies its search
    # string should outrank it, since the old appointment's ranking is cut by more than half at that age. A new comment
    # with the same words in reverse order should rank below it, since an exact match outweighs any recency advantage.
    old = next(
        (
            _tc for _tc in test.test_cases
            if _tc.appt.created_date
            and _tc.appt.created_date < utils.date_to_local_tz(datetime.datetime.now()) - timedelta(days=730)
            and ' '.join(reversed(_tc.search_string.split())) != _tc.search_string
        ),
        None,
    )
    recent_comment = NoteComment()
    reversed_comment = NoteComment()

    def add_comment_and_set_id(self, appt, comment):
        self.student_page.add_appt_comment(appt, comment)
        matching = [c for c in boa_utils.get_appt_comments(appt) if c.body == comment.body]
        assert len(matching) == 1
        comment.comment_id = matching[0].comment_id

    def test_create_exact_match_comment(self):
        self.student_page.load_page(self.tc.student)
        self.student_page.show_appts()
        self.student_page.expand_item(self.tc.appt)
        self.exact_comment.body = f'Discussed the {self.phrase} plan.'
        self.add_comment_and_set_id(self.tc.appt, self.exact_comment)

    def test_create_newer_loose_match_comment(self):
        # Created after the exact match, so it is newer, but its words are not in phrase order.
        self.loose_comment.body = f'The {self.unique_id} plan covers quartz first and zephyr later.'
        self.add_comment_and_set_id(self.tc.appt, self.loose_comment)

    def test_exact_match_comment_ranked_above_newer_loose_match_comment(self):
        nessie_timeline_utils.wait_for_cdc_upsert(self.exact_comment.comment_id, 'create', table_name='comments')
        nessie_timeline_utils.wait_for_cdc_upsert(self.loose_comment.comment_id, 'create', table_name='comments')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(self.phrase)
        result_ids = self.search_results_page.appt_search_result_ids()
        expected = [('comment', self.exact_comment.comment_id), ('comment', self.loose_comment.comment_id)]
        utils.assert_equivalence(result_ids, expected)

    def test_exact_match_comment_ranked_above_newer_loose_match_comment_in_adv_search(self):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(self.tc.student)
        self.homepage.enter_adv_search_and_hit_enter(self.phrase)
        result_ids = self.search_results_page.appt_search_result_ids()
        expected = [('comment', self.exact_comment.comment_id), ('comment', self.loose_comment.comment_id)]
        utils.assert_equivalence(result_ids, expected)

    def test_create_comments_on_old_appt(self):
        if self.old:
            app.logger.info(f'Copying search string of appointment {self.old.appt.record_id}: {self.old.search_string}')
            self.student_page.load_page(self.old.student)
            self.student_page.show_appts()
            self.student_page.expand_item(self.old.appt)
            self.recent_comment.body = self.old.search_string
            self.add_comment_and_set_id(self.old.appt, self.recent_comment)
            self.reversed_comment.body = ' '.join(reversed(self.old.search_string.split()))
            self.add_comment_and_set_id(self.old.appt, self.reversed_comment)
        else:
            app.logger.info('Skipping mixed results tests since no test appointment is at least two years old')

    def test_newer_comment_ranked_above_older_appt(self):
        if self.old:
            nessie_timeline_utils.wait_for_cdc_upsert(self.recent_comment.comment_id, 'create', table_name='comments')
            nessie_timeline_utils.wait_for_cdc_upsert(self.reversed_comment.comment_id, 'create', table_name='comments')
            self.homepage.load_page()
            self.homepage.enter_simple_search_and_hit_enter(self.old.search_string)
            result_ids = self.search_results_page.appt_search_result_ids()
            assert result_ids
            utils.assert_equivalence(result_ids[0], ('comment', self.recent_comment.comment_id))
            # The old appointment may be past the first page of results; when it is listed, it must come after the
            # new comment.
            old_appt = ('appointment', self.old.appt.record_id)
            if old_appt in result_ids:
                assert result_ids.index(old_appt) > 0

    def test_older_appt_ranked_above_newer_loose_match_comment(self):
        if self.old:
            result_ids = self.search_results_page.appt_search_result_ids()
            old_appt = ('appointment', self.old.appt.record_id)
            reversed_comment = ('comment', self.reversed_comment.comment_id)
            if old_appt in result_ids:
                # The reversed comment ranks too low to be guaranteed a place on the first page of results.
                if reversed_comment in result_ids:
                    assert result_ids.index(old_appt) < result_ids.index(reversed_comment)
            else:
                app.logger.info(f'Skipping test since appointment {self.old.appt.record_id} is not on the first page')

    def test_delete_search_order_comments(self):
        # As in test_appt_mgmt, the admin removes the comments these tests created.
        self.homepage.switch_user()
        comments = [(self.tc, self.exact_comment), (self.tc, self.loose_comment)]
        if self.old:
            comments.extend([(self.old, self.recent_comment), (self.old, self.reversed_comment)])
        for _tc, comment in comments:
            if comment.comment_id:
                self.student_page.load_page(_tc.student)
                self.student_page.show_appts()
                self.student_page.expand_item(_tc.appt)
                self.student_page.delete_appt_comment(_tc.appt, comment)
