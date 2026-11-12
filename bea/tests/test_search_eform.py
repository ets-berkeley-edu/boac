"""
Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.

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
test.search_e_forms()

comments_by_test_case = {}

# Topic and author filters apply to notes and appointments only. eForms have no topics or BOA authors, so eForm search
# ignores those filters, and an eForm or eForm comment that matches the search phrase stays in the results.
filter_topic = [t.value['name'].title() for t in Topics][0]
filter_author = next(
    (a for a in nessie_timeline_utils.get_all_advising_note_authors()
     if a.uid != test.advisor.uid and a.first_name and a.last_name),
    None,
)


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
class TestSearchEForm:

    def test_simple_search(self, tc):
        app.logger.info(f'Begin tests with UID {tc.student.uid} eForm {tc.e_form.record_id} string {tc.search_string}')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_eform_result_present(tc.e_form)

    def test_adv_search_matching_student(self, tc):
        self.search_results_page.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_eform_result_present(tc.e_form)

    def test_search_result_name(self, tc):
        utils.assert_equivalence(self.search_results_page.eform_result_student_name(tc.e_form), tc.student.full_name)

    def test_search_result_sid(self, tc):
        utils.assert_equivalence(self.search_results_page.eform_result_sid(tc.student, tc.e_form), tc.student.sid)

    def test_search_result_date(self, tc):
        expected = self.search_results_page.expected_note_or_appt_date_format(tc.e_form.created_date)
        utils.assert_equivalence(self.search_results_page.eform_result_date(tc.e_form), expected)

    # Date filters match an eForm on its created date.

    def test_adv_search_matching_date_future_range(self, tc):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.set_notes_date_range(date_from=tc.e_form.created_date,
                                           date_to=(tc.e_form.created_date + timedelta(days=1)))
        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_eform_result_present(tc.e_form)

    def test_adv_search_matching_date_past_range(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.set_notes_date_range(date_from=(tc.e_form.created_date - timedelta(days=1)),
                                           date_to=tc.e_form.created_date)
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_eform_result_present(tc.e_form)

    def test_adv_search_non_matching_date_past_range(self, tc):
        self.search_results_page.click_edit_search()
        self.homepage.set_notes_date_range(date_from=(tc.e_form.created_date - timedelta(days=30)),
                                           date_to=(tc.e_form.created_date - timedelta(days=1)))
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_eform_result_not_present(tc.e_form)

    def test_adv_search_non_matching_date_future_range(self, tc):
        if tc.e_form.created_date + timedelta(days=30) < utils.date_to_local_tz(datetime.datetime.now()):
            self.homepage.reopen_and_reset_adv_search()
            self.homepage.set_notes_student(tc.student)
            self.homepage.set_notes_date_range(date_from=(tc.e_form.created_date + timedelta(days=1)),
                                               date_to=(tc.e_form.created_date + timedelta(days=30)))
            self.homepage.enter_adv_search(tc.search_string)
            self.homepage.click_adv_search_button()
            self.search_results_page.assert_eform_result_not_present(tc.e_form)

    def test_adv_search_topic_not_applied(self, tc):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.select_note_topic(filter_topic)
        self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
        self.search_results_page.assert_eform_result_present(tc.e_form)

    def test_adv_search_posted_by_you_not_applied(self, tc):
        # The test advisor didn't create the eForm, so the result shows that the "Posted by you" filter was skipped.
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.select_notes_posted_by_you()
        self.homepage.enter_adv_search(tc.search_string)
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_eform_result_present(tc.e_form)

    def test_adv_search_author_not_applied(self, tc):
        if filter_author:
            self.homepage.reopen_and_reset_adv_search()
            self.homepage.set_notes_author(f'{filter_author.first_name} {filter_author.last_name}')
            self.homepage.enter_adv_search_and_hit_enter(tc.search_string)
            self.search_results_page.assert_eform_result_present(tc.e_form)
        else:
            app.logger.info('Skipping eForm author filter test since no note author other than the test advisor has a name')

    # COMMENTS

    def test_add_comment(self, tc):
        comment = NoteComment()
        comment.body = f'Comment on {tc.e_form.data_source} eForm {utils.get_test_identifier()}'
        self.student_page.load_page(tc.student)
        self.student_page.show_e_forms()
        self.student_page.expand_item(tc.e_form)
        self.student_page.add_e_form_comment(tc.e_form, comment)
        matching = [c for c in boa_utils.get_e_form_comments(tc.e_form) if c.body == comment.body]
        assert len(matching) == 1
        comment.comment_id = matching[0].comment_id
        comments_by_test_case[tc.test_case_id] = comment

    def test_simple_search_comment(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        nessie_timeline_utils.wait_for_cdc_upsert(comment.comment_id, 'create', table_name='comments')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(comment.body)
        self.search_results_page.assert_eform_comment_result_present(comment)

    def test_adv_search_comment_matching_student(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(tc.student)
        self.homepage.enter_adv_search_and_hit_enter(comment.body)
        self.search_results_page.assert_eform_comment_result_present(comment)

    def test_adv_search_comment_topic_not_applied(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.select_note_topic(filter_topic)
        self.homepage.enter_adv_search_and_hit_enter(comment.body)
        self.search_results_page.assert_eform_comment_result_present(comment)

    def test_adv_search_comment_posted_by_you_not_applied(self, tc):
        # The test advisor wrote the comment, so this would pass either way; it checks that the filter doesn't break the
        # search. The non-matching author test below is the one that shows the filter is skipped.
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.select_notes_posted_by_you()
        self.homepage.enter_adv_search_and_hit_enter(comment.body)
        self.search_results_page.assert_eform_comment_result_present(comment)

    def test_adv_search_comment_non_matching_author_not_applied(self, tc):
        # The comment's author is the test advisor, not filter_author, so a working author filter would hide it.
        comment = comments_by_test_case[tc.test_case_id]
        if filter_author:
            self.homepage.reopen_and_reset_adv_search()
            self.homepage.set_notes_author(f'{filter_author.first_name} {filter_author.last_name}')
            self.homepage.enter_adv_search_and_hit_enter(comment.body)
            self.search_results_page.assert_eform_comment_result_present(comment)
        else:
            app.logger.info('Skipping eForm comment author filter test since no note author other than the test advisor has a name')

    def test_comment_result_is_only_result(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(comment.body)
        utils.assert_equivalence(self.search_results_page.eform_search_result_ids(), [('comment', comment.comment_id)])

    def test_delete_comment(self, tc):
        # Admin removes the comment. The advisor then logs back in, so that the next test case runs as the advisor.
        comment = comments_by_test_case[tc.test_case_id]
        self.homepage.switch_user()
        self.student_page.load_page(tc.student)
        self.student_page.show_e_forms()
        self.student_page.expand_item(tc.e_form)
        self.student_page.delete_e_form_comment(tc.e_form, comment)
        self.homepage.switch_user(test.advisor)

    def test_deleted_comment_not_in_search_results(self, tc):
        comment = comments_by_test_case[tc.test_case_id]
        nessie_timeline_utils.wait_for_cdc_upsert(comment.comment_id, 'delete', table_name='comments')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(comment.body)
        assert ('comment', comment.comment_id) not in self.search_results_page.eform_search_result_ids()


@pytest.mark.usefixtures('page_objects')
class TestSearchEFormOrder:

    # Search ranks a stronger text match above a weaker one, and a newer match above an older one of the same strength.
    # Advisors can't create eForms, but they can comment on them, so these tests add comments to existing eForms. The
    # timestamp in the search phrase keeps every other eForm and comment out of the results.
    unique_id = str(int(time.time()))
    phrase = f'zephyr quartz {unique_id}'
    tc = test.test_cases[0]
    exact_comment = NoteComment()
    loose_comment = NoteComment()

    # The mixed-results tests use an existing eForm at least two years old. A new comment that copies its search string
    # should outrank it, since the old eForm's ranking is cut by more than half at that age. A new comment with the same
    # words in reverse order should rank below it, since an exact match outweighs any recency advantage.
    old = next(
        (
            _tc for _tc in test.test_cases
            if _tc.e_form.created_date
            and _tc.e_form.created_date < utils.date_to_local_tz(datetime.datetime.now()) - timedelta(days=730)
            and ' '.join(reversed(_tc.search_string.split())) != _tc.search_string
        ),
        None,
    )
    recent_comment = NoteComment()
    reversed_comment = NoteComment()

    def add_comment_and_set_id(self, e_form, comment):
        self.student_page.add_e_form_comment(e_form, comment)
        matching = [c for c in boa_utils.get_e_form_comments(e_form) if c.body == comment.body]
        assert len(matching) == 1
        comment.comment_id = matching[0].comment_id

    def test_create_exact_match_comment(self):
        self.student_page.load_page(self.tc.student)
        self.student_page.show_e_forms()
        self.student_page.expand_item(self.tc.e_form)
        self.exact_comment.body = f'Discussed the {self.phrase} plan.'
        self.add_comment_and_set_id(self.tc.e_form, self.exact_comment)

    def test_create_newer_loose_match_comment(self):
        # Created after the exact match, so it is newer, but its words are not in phrase order.
        self.loose_comment.body = f'The {self.unique_id} plan covers quartz first and zephyr later.'
        self.add_comment_and_set_id(self.tc.e_form, self.loose_comment)

    def test_exact_match_comment_ranked_above_newer_loose_match_comment(self):
        nessie_timeline_utils.wait_for_cdc_upsert(self.exact_comment.comment_id, 'create', table_name='comments')
        nessie_timeline_utils.wait_for_cdc_upsert(self.loose_comment.comment_id, 'create', table_name='comments')
        self.homepage.load_page()
        self.homepage.enter_simple_search_and_hit_enter(self.phrase)
        result_ids = self.search_results_page.eform_search_result_ids()
        expected = [('comment', self.exact_comment.comment_id), ('comment', self.loose_comment.comment_id)]
        utils.assert_equivalence(result_ids, expected)

    def test_exact_match_comment_ranked_above_newer_loose_match_comment_in_adv_search(self):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(self.tc.student)
        self.homepage.enter_adv_search_and_hit_enter(self.phrase)
        result_ids = self.search_results_page.eform_search_result_ids()
        expected = [('comment', self.exact_comment.comment_id), ('comment', self.loose_comment.comment_id)]
        utils.assert_equivalence(result_ids, expected)

    def test_create_comments_on_old_e_form(self):
        if self.old:
            app.logger.info(f'Copying search string of eForm {self.old.e_form.record_id}: {self.old.search_string}')
            self.student_page.load_page(self.old.student)
            self.student_page.show_e_forms()
            self.student_page.expand_item(self.old.e_form)
            self.recent_comment.body = self.old.search_string
            self.add_comment_and_set_id(self.old.e_form, self.recent_comment)
            self.reversed_comment.body = ' '.join(reversed(self.old.search_string.split()))
            self.add_comment_and_set_id(self.old.e_form, self.reversed_comment)
        else:
            app.logger.info('Skipping mixed results tests since no test eForm is at least two years old')

    def test_newer_comment_ranked_above_older_e_form(self):
        if self.old:
            nessie_timeline_utils.wait_for_cdc_upsert(self.recent_comment.comment_id, 'create', table_name='comments')
            nessie_timeline_utils.wait_for_cdc_upsert(self.reversed_comment.comment_id, 'create', table_name='comments')
            self.homepage.load_page()
            self.homepage.enter_simple_search_and_hit_enter(self.old.search_string)
            result_ids = self.search_results_page.eform_search_result_ids()
            assert result_ids
            utils.assert_equivalence(result_ids[0], ('comment', self.recent_comment.comment_id))
            # The old eForm may be past the first page of results; when it is listed, it must come after the new comment.
            old_e_form = ('eform', self.old.e_form.record_id)
            if old_e_form in result_ids:
                assert result_ids.index(old_e_form) > 0

    def test_older_e_form_ranked_above_newer_loose_match_comment(self):
        if self.old:
            result_ids = self.search_results_page.eform_search_result_ids()
            old_e_form = ('eform', self.old.e_form.record_id)
            reversed_comment = ('comment', self.reversed_comment.comment_id)
            if old_e_form in result_ids:
                # The reversed comment ranks too low to be guaranteed a place on the first page of results.
                if reversed_comment in result_ids:
                    assert result_ids.index(old_e_form) < result_ids.index(reversed_comment)
            else:
                app.logger.info(f'Skipping test since eForm {self.old.e_form.record_id} is not on the first page')

    def test_delete_search_order_comments(self):
        # As in test_e_form_mgmt, the admin removes the comments these tests created.
        self.homepage.switch_user()
        comments = [(self.tc, self.exact_comment), (self.tc, self.loose_comment)]
        if self.old:
            comments.extend([(self.old, self.recent_comment), (self.old, self.reversed_comment)])
        for _tc, comment in comments:
            if comment.comment_id:
                self.student_page.load_page(_tc.student)
                self.student_page.show_e_forms()
                self.student_page.expand_item(_tc.e_form)
                self.student_page.delete_e_form_comment(_tc.e_form, comment)
