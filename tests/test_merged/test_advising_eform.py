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


from boac import std_commit
from boac.externals import data_loch
from boac.merged.advising_eform import search_advising_eforms
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent
from tests.util import (
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
            expected_keys=_expected_eform_ids,
            limit=SEARCH_RESULTS_LIMIT,
        )

    def test_filters_are_not_vacuous(self, mock_searchable_eform_comments):  # noqa: ARG002
        """Each filter, applied alone, narrows the results and leaves at least one match."""
        assert_search_filters_not_vacuous(EFORM_SEARCH_FILTERS, _expected_eform_ids)

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
        refresh_loch_eform_search_index(app, comment=second_comment)
        try:
            results = search_advising_eforms(search_phrase='design', limit=SEARCH_RESULTS_LIMIT)
            comment_ids = [row['id'] for row in results['eforms'] if row['kind'] == 'commentOnEform']
            assert sorted(comment_ids) == sorted(set(comment_ids))
        finally:
            second_comment.soft_delete()
            std_commit(allow_test_environment=True)
            refresh_loch_eform_search_index(app, deleted_comment=second_comment)


def _expected_eform_ids(search_phrase=None, student_csid=None, datetime_from=None, datetime_to=None):
    boa_cdc = data_loch.boa_cdc_schema()
    sis_advising = data_loch.sis_advising_notes_schema()
    # search_eforms adds a prefix operator to each token, which plainto_tsquery then discards as punctuation.
    search_phrase = f'{search_phrase}:*' if search_phrase else None
    all_student_sids = {row['sid'] for row in data_loch.safe_execute_rds(f'SELECT sid FROM {data_loch.student_schema()}.student_profile_index')}
    eform_ids = []

    comment_text_matches = expected_fts_results(f'{boa_cdc}.eform_comments_search_index', 'boa_id', search_phrase, data_loch.safe_execute_rds)
    comments = data_loch.safe_execute_rds(f"""
        SELECT c.boa_id, c.parent_eform_id, c.updated_at, e.student_sid
          FROM {boa_cdc}.eform_comments c
          JOIN {sis_advising}.student_eforms e ON e.id = c.parent_eform_id""")
    for row in comments:
        if (
            (not comment_text_matches or row['boa_id'] in comment_text_matches)
            and (not student_csid or row['student_sid'] == student_csid)
            and (row['student_sid'] in all_student_sids)
            and in_date_range(row['updated_at'], datetime_from, datetime_to)
        ):
            eform_ids.append(row['boa_id'])

    eform_text_matches = expected_fts_results(f'{sis_advising}.student_eforms_search_index', 'id', search_phrase, data_loch.safe_execute_rds)
    eforms = data_loch.safe_execute_rds(f'SELECT id, student_sid, created_at FROM {sis_advising}.student_eforms')
    for row in eforms:
        if (
            (not eform_text_matches or row['id'] in eform_text_matches)
            and (not student_csid or row['student_sid'] == student_csid)
            and (row['student_sid'] in all_student_sids)
            and in_date_range(row['created_at'], datetime_from, datetime_to)
        ):
            eform_ids.append(row['id'])
    return eform_ids
