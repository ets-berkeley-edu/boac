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

from contextlib import contextmanager
from datetime import UTC, datetime

import pytest

from boac import std_commit
from boac.externals import data_loch
from boac.merged.advising_eform import _strip_labels_and_dashes, search_advising_eforms
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent
from tests.util import (
    ExpectedSearchResults,
    assert_every_search_filter_combination,
    assert_search_filters_not_vacuous,
    expected_fts_results,
    in_date_range,
    refresh_loch_eform_search_index,
)

coe_advisor_uid = '1133399'

# One value per filter, chosen so that filters overlap in fixture data and every combination is meaningful.
EFORM_SEARCH_FILTERS = {
    'search_phrase': 'design',
    'student_csid': '11667051',
    'datetime_from': '2020-12-05',
    'datetime_to': '2021-01-01',
}
SEARCH_RESULTS_LIMIT = 50

class TestEformSearch:
    """eForm search, every combination of filters."""

    def test_every_filter_combination(self, mock_searchable_eform_comments):  # noqa: ARG002
        """Returns exactly the BOA comments and SIS eForms matching all active filters, for all 16 combinations."""
        def _search_advising_eforms(criteria):
            results = search_advising_eforms(**criteria, offset=0, limit=SEARCH_RESULTS_LIMIT)
            return {
                'rows': results['eforms'],
                'total': results['totalEformCount'],
            }
        assert_every_search_filter_combination(
            filters=EFORM_SEARCH_FILTERS,
            search=_search_advising_eforms,
            expected_keys=_ExpectedEformIds(),
            limit=SEARCH_RESULTS_LIMIT,
        )

    def test_filters_are_not_vacuous(self, mock_searchable_eform_comments):  # noqa: ARG002
        """Each filter, applied alone, narrows the results and leaves at least one match."""
        assert_search_filters_not_vacuous(EFORM_SEARCH_FILTERS, _ExpectedEformIds())

    def test_multiple_comments_on_one_eform(self, app, mock_searchable_eform_comments):
        """Each matching comment on an eForm is returned exactly once."""
        comment_parent = CommentParent.find_by_id(mock_searchable_eform_comments[0].comment_parent_id)
        second_comment = Comment.create(
            comment_parent_id=comment_parent.id,
            author_uid=coe_advisor_uid,
            author_name='COE Advisor',
            author_role='advisor',
            author_dept_codes=['COENG'],
            body='The product of the skilled paper maker has more than quadrupled, in artistic variety, \
              during the few years last past, until it is now the fault of its designer if a book intended \
              to be harmoniously artistic is not as true to its motive in paper as in typography or binding.',
        )
        std_commit(allow_test_environment=True)
        refresh_loch_eform_search_index(app, comments=[second_comment])
        try:
            results = search_advising_eforms(search_phrase='design', limit=SEARCH_RESULTS_LIMIT)
            comment_ids = [row['id'] for row in results['eforms'] if row['kind'] == 'commentOnEform']
            assert sorted(comment_ids) == sorted(set(comment_ids))
        finally:
            second_comment.soft_delete()
            std_commit(allow_test_environment=True)
            refresh_loch_eform_search_index(app, deleted_comments=[second_comment])

    def test_search_eforms_ordered_by_relevance(self, app, db):
        """Ranks newer results higher but also prefers stronger text matches."""
        # Both SIS eForms carry the exact phrase 'Late Grading Basis Change' as their requested action. They are
        # older than the new comments but newer than the 2015 comment, so recency decides where they fall.
        with _create_eform_comments(app, db, [
            {'body': 'Late grading basis change approved.'},
            {'body': 'Late grading basis change approved.', 'created_at': datetime(2015, 11, 1, tzinfo=UTC)},
            {'body': 'Change of grading basis was late.', 'created_at': datetime(2026, 11, 1, tzinfo=UTC)},
        ]) as (exact_match, exact_match_old, loose_match):
            results = search_advising_eforms(search_phrase='late grading basis change')
            eforms = results['eforms']
            assert len(eforms) == 5
            assert results['totalEformCount'] == 5
            assert eforms[0]['id'] == exact_match.id
            assert eforms[0]['kind'] == 'commentOnEform'
            assert eforms[0]['snippet'] == '<strong>Late</strong> <strong>grading</strong> <strong>basis</strong> <strong>change</strong> approved.'
            # eform-10098 was created twelve hours after eform-10099, so its recency weight is slightly higher.
            assert eforms[1]['id'] == 'eform-10098'
            assert eforms[1]['kind'] == 'eform'
            assert eforms[1]['snippet'] == '<strong>Late</strong> <strong>Change</strong> of Schedule Request eForm: PSYCH 110 - \
<strong>Late</strong> <strong>Grading</strong> <strong>Basis</strong> <strong>Change</strong> - In Error'
            assert eforms[2]['id'] == 'eform-10099'
            assert eforms[2]['kind'] == 'eform'
            assert eforms[2]['snippet'] == '<strong>Late</strong> <strong>Change</strong> of Schedule Request eForm: EECS 16A - \
<strong>Late</strong> <strong>Grading</strong> <strong>Basis</strong> <strong>Change</strong> - Executed'
            assert eforms[3]['id'] == exact_match_old.id
            assert eforms[3]['kind'] == 'commentOnEform'
            assert eforms[3]['snippet'] == '<strong>Late</strong> <strong>grading</strong> <strong>basis</strong> <strong>change</strong> approved.'
            assert eforms[4]['id'] == loose_match.id
            assert eforms[4]['kind'] == 'commentOnEform'
            assert eforms[4]['snippet'] == '<strong>Change</strong> of <strong>grading</strong> <strong>basis</strong> was <strong>late</strong>.'


class TestStripLabelsAndDashes:
    """Cleaning an eForm search phrase before it is used to highlight snippets."""

    @pytest.mark.parametrize(
        ('search_phrase', 'expected'),
        [
            # Empty input yields an empty string, so snippet highlighting has nothing to match.
            (None, ''),
            ('', ''),
            ('   ', ''),
            # Without a display-title prefix, the phrase is returned as-is apart from trimming.
            ('  late grading basis change  ', 'late grading basis change'),
            # En and em dashes become spaces whether or not a prefix is present.
            ('EECS\u201316A\u2014Executed', 'EECS 16A Executed'),
            # A full display-title prefix drops its label-only tokens but keeps the rest of the query.
            ('Late Change of Schedule Request eForm: PSYCH 110', 'of : PSYCH 110'),
            # Prefix detection and token removal both ignore case.
            ('reduced course load eform rcl', 'reduced rcl'),
            # Only whole words are removed, so 'Careers' survives while 'Career' does not.
            ('Career Program Plan eForm \u2013 Careers in Change', 'Program Plan Careers in Change'),
            # Two prefixes in one query strip the union of their label tokens.
            ('Career Program Plan eForm Reduced Course Load eForm', 'Program Plan Reduced'),
            # Label tokens are kept when their prefix is incomplete, because they may be real search terms.
            ('Late change of plans', 'Late change of plans'),
            # Tokens from a prefix that is absent are kept, even if another prefix is present.
            ('Career Program Plan eForm: Late Change', 'Program Plan : Late Change'),
        ],
    )
    def test_strip_labels_and_dashes(self, search_phrase, expected):
        """Removes dashes, and label-only tokens when a known eForm display-title prefix is present."""
        assert _strip_labels_and_dashes(search_phrase) == expected


@contextmanager
def _create_eform_comments(app, db, comment_specs):
    comment_parent = CommentParent.find_or_create(parent_type='late_drop_eform', parent_id='eform-10099')
    comments = []
    for spec in comment_specs:
        comment = Comment.create(
            author_uid=coe_advisor_uid,
            author_name='COE Advisor',
            author_role='advisor',
            author_dept_codes=['COENG'],
            comment_parent_id=comment_parent.id,
            body=spec['body'],
        )
        # Backdating must happen before indexing, because the loch search index derives age_days from created_at.
        if spec.get('created_at'):
            comment.created_at = spec['created_at']
        db.session.add(comment)
        comments.append(comment)
    std_commit(allow_test_environment=True)
    refresh_loch_eform_search_index(app, comments=comments)
    try:
        yield comments
    finally:
        for comment in comments:
            comment.soft_delete()
        std_commit(allow_test_environment=True)
        refresh_loch_eform_search_index(app, deleted_comments=comments)


class _ExpectedEformIds(ExpectedSearchResults):
    """Expected eForm search results: loads comments and SIS eForms once, then filters them in Python per combination."""

    def __init__(self):
        super().__init__()
        self.boa_cdc = data_loch.boa_cdc_schema()
        self.sis_advising = data_loch.sis_advising_notes_schema()
        self.all_student_sids = {
            row['sid'] for row in data_loch.safe_execute_rds(f'SELECT sid FROM {data_loch.student_schema()}.student_profile_index')
        }
        self.comments = data_loch.safe_execute_rds(f"""
            SELECT c.boa_id, c.parent_eform_id, c.updated_at, e.student_sid
              FROM {self.boa_cdc}.eform_comments c
              JOIN {self.sis_advising}.student_eforms e ON e.id = c.parent_eform_id""")
        self.eforms = data_loch.safe_execute_rds(f'SELECT id, student_sid, created_at FROM {self.sis_advising}.student_eforms')

    def __call__(self, search_phrase=None, student_csid=None, datetime_from=None, datetime_to=None):
        # search_eforms adds a prefix operator to each token, which plainto_tsquery then discards as punctuation.
        search_phrase = f'{search_phrase}:*' if search_phrase else None
        eform_ids = []

        comment_text_matches = self._cached(
            'comment_text', search_phrase,
            compute=lambda: expected_fts_results(f'{self.boa_cdc}.eform_comments_search_index', 'boa_id', search_phrase, data_loch.safe_execute_rds),
        )
        for row in self.comments:
            if (
                (not comment_text_matches or row['boa_id'] in comment_text_matches)
                and (not student_csid or row['student_sid'] == student_csid)
                and (row['student_sid'] in self.all_student_sids)
                and in_date_range(row['updated_at'], datetime_from, datetime_to)
            ):
                eform_ids.append(row['boa_id'])

        eform_text_matches = self._cached(
            'eform_text', search_phrase,
            compute=lambda: expected_fts_results(f'{self.sis_advising}.student_eforms_search_index', 'id', search_phrase, data_loch.safe_execute_rds),
        )
        for row in self.eforms:
            if (
                (not eform_text_matches or row['id'] in eform_text_matches)
                and (not student_csid or row['student_sid'] == student_csid)
                and (row['student_sid'] in self.all_student_sids)
                and in_date_range(row['created_at'], datetime_from, datetime_to)
            ):
                eform_ids.append(row['id'])
        return eform_ids
