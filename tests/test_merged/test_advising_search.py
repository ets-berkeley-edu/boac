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
from datetime import UTC, datetime, timedelta

import pytz
from dateutil.parser import parse

from boac import std_commit
from boac.externals import data_loch
from boac.merged.advising_search import search_advising_notes
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.university_dept import UniversityDept
from tests.util import (
    active_search_criteria,
    assert_every_search_filter_combination,
    assert_search_filters_not_vacuous,
    expected_fts_results,
    get_topic_matches,
    in_date_range,
    legacy_advisor_match,
    legacy_timestamp,
    override_config,
    refresh_loch_note_search_index,
)

asc_advisor_uid = '6446'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'

# One value per filter, chosen so that filters overlap in fixture data and every combination is meaningful.
NOTE_SEARCH_FILTERS = {
    'search_phrase': 'make',
    'author_uid': coe_advisor_uid,
    'author_csid': '800700600',
    'student_csid': '11667051',
    'department_codes': ['COENG'],
    'topic': 'Good Show',
    'datetime_from': '2014-01-10',
    'datetime_to': '2020-01-01',
}
SEARCH_RESULTS_LIMIT = 50

class TestSearchAdvisingNote:
    """Search merged advising note data."""

    def test_search_advising_notes(self):
        results = search_advising_notes(search_phrase='herostratus')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert '<strong>Herostratus</strong> lives' in notes[0]['noteSnippet']
        assert notes[0]['noteSnippet'].startswith('...iniquity of oblivion blindely scattereth her poppy')
        assert notes[0]['noteSnippet'].endswith('confounded that of himself. In vain we...')
        assert notes[0]['studentSid'] == '11667051'
        assert notes[0]['studentUid'] == '61889'
        assert notes[0]['studentName'] == 'Deborah Davies'
        assert notes[0]['advisorSid'] == '600500400'
        assert notes[0]['id'] == '11667051-00003'
        assert parse(notes[0]['createdAt']) == parse('2017-11-05T12:00:00+00')
        assert notes[0]['updatedAt'] is None

    def test_search_for_private_advising_notes(self, mock_private_advising_note):  # noqa: ARG002
        results = search_advising_notes(search_phrase='neon', author_uid=ce3_advisor_uid)
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert total_note_count == 0
        assert notes == []

    def test_search_advising_notes_by_category(self):
        """Matches legacy category/subcategory for SIS advising notes only if body is blank."""
        results = search_advising_notes(search_phrase='Quick Question')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert notes[0]['noteSnippet'] == '<strong>Quick</strong> <strong>Question</strong>, Unanswered'

    def test_search_for_asc_advising_notes(self):
        results = search_advising_notes(search_phrase='kilmister')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert notes[0]['noteSnippet'] == ''
        assert notes[0]['advisorName'] == 'Lemmy Kilmister'
        assert parse(notes[0]['createdAt']) == parse('2014-01-03T20:30:00+00')
        assert notes[0]['updatedAt'] is None
        results = search_advising_notes(search_phrase='academic')
        notes = results['notes']
        assert len(notes) == 1
        assert notes[0]['noteSnippet'] == ''
        assert notes[0]['advisorName'] == 'Lemmy Kilmister'
        assert parse(notes[0]['createdAt']) == parse('2014-01-03T20:30:00+00')
        assert notes[0]['updatedAt'] is None

    def test_search_result_strip_tags(self, app):
        tag_embedded_note = """<p>01 Plain: Student discussed <b>transfer</b> credit with advisor.</p>
            <p>*02 Real script: before<script>alert('real')</script>after</p>
            <p>*03 Script with attrs and uppercase: A<SCRIPT type="text/javascript" src="https://example.com/x.js"></SCRIPT>B</p>
            <p>*04 Encoded script: &lt;script&gt;alert('encoded')&lt;/script&gt;</p>
            <p>*05 Double-encoded script: &amp;lt;script&amp;gt;alert('double')&amp;lt;/script&amp;gt;</p>
            <p>*06 Numeric refs: &#60;script&#62;alert('dec')&#60;/script&#62; and &#x3C;script&#x3E;alert('hex')&#x3C;/script&#x3E;</p>
            <p>*07 Real img onerror: <img src=x onerror="alert('img')">done</p>
            <p>*08 Encoded img onerror: &lt;img src=x onerror="alert('img2')"&gt;done</p>
            <p>*09 Encoded svg onload: &lt;svg onload=alert('svg')&gt;&lt;/svg&gt;done</p>
            <p>*10 Link: <a href="javascript:alert('href')">click me</a></p>
            <p>*11 Style: <style>body { display: none; }</style>visible text</p>
            <p>*12 Iframe: <iframe src="https://example.com">fallback</iframe>after iframe</p>
            <p>*13 Nested skip: <noscript><script>alert('nested')</script>hidden</noscript>shown</p>
            <p>*14 Comment: before<!-- <script>alert('comment')</script> -->after</p>
            <ul><li>*Testing!</li></ul>
            <p>*15 Comparisons: GPA < 3.0, units > 120, and 2 <3 should survive</p>
            <p>*16 Ampersands: R&amp;D, Q&A, and a bare & sign</p>
            <p>*17 Unicode: café, naïve, 学生, emoji 🎓, non-breaking&nbsp;space</p>
            <p>*18 Split word: trans<b>fer</b>red</p>
            <p>*19 Triple-encoded (beyond max_passes, must be escaped on output): &amp;amp;lt;img src=x onerror=alert('triple')&amp;amp;gt;</p>
            <p>*20 Unclosed script at end swallows the rest: <script>alert('unclosed')"""
        with (
            override_config(app, 'NOTES_SEARCH_RESULT_SNIPPET_PADDING', 60),
            _create_coe_advisor_note(app, body=tag_embedded_note),
        ):
            results = search_advising_notes(search_phrase='test')
            notes = results['notes']
            lines = notes[0]['noteSnippet'].split('*')
            assert lines[0].lstrip() == '...with advisor. '
            assert lines[1].lstrip() == '02 Real script: before after '
            assert lines[2].lstrip() == '03 Script with attrs and uppercase: A B '
            assert lines[3].lstrip() == '04 Encoded script: '
            assert lines[4].lstrip() == '05 Double-encoded script: '
            assert lines[5].lstrip() == '06 Numeric refs: and '
            assert lines[6].lstrip() == '07 Real img onerror: done '
            assert lines[7].lstrip() == '08 Encoded img onerror: done '
            assert lines[8].lstrip() == '09 Encoded svg onload: done '
            assert lines[9].lstrip() == '10 Link: click me '
            assert lines[10].lstrip() == '11 Style: visible text '
            assert lines[11].lstrip() == '12 Iframe: after iframe '
            assert lines[12].lstrip() == '13 Nested skip: shown '
            assert lines[13].lstrip() == '14 Comment: before after '
            assert lines[14].lstrip() == '<strong>Testing</strong>! '
            assert lines[15].lstrip() == '15 Comparisons: GPA &lt; 3.0, units &gt; 120, and 2 &lt; 3 should survive '
            assert lines[16].lstrip() == '16 Ampersands: R&amp;D, Q&amp;A, and a bare &amp; sign '
            assert lines[17].lstrip() == '17 Unicode: café, naïve, 学生, emoji 🎓, non-breaking space '
            assert lines[18].lstrip() == '18 Split word: trans fer red '
            assert lines[19].lstrip() == '19 Triple-encoded (beyond max_passes, must be escaped on output): &lt;img src=x onerror=alert(&#x27;&#x27;triple&#x27;&#x27;)&gt; '  # noqa: E501
            assert lines[20].lstrip() == '20 Unclosed script at end swallows the rest: '

    def test_search_advising_notes_stemming(self):
        results = search_advising_notes(search_phrase='spare')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1

        assert '<strong>spared</strong>' in notes[0]['noteSnippet']
        results = search_advising_notes(search_phrase='felicity')
        notes = results['notes']
        assert '<strong>felicities</strong>' in notes[0]['noteSnippet']

    def test_search_advising_notes_too_short_to_snippet(self):
        results = search_advising_notes(search_phrase='campus')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert notes[0]['noteSnippet'] == 'Is this student even on <strong>campus</strong>?'

    def test_search_advising_notes_ordered_by_relevance(self, app):
        """Ranks newer results higher but also prefers stronger text matches."""
        with (
            _create_coe_advisor_note(app, subject='Confound the confounders', created_at=datetime(2015, 11, 1, tzinfo=UTC)) as oldest_note,
            _create_coe_advisor_note(
                app,
                body='"Confound" appearing only once.',
                created_at=datetime.now() - timedelta(days=300),
                parent_note_id=oldest_note.id,
            ) as recent_comment,
        ):
            results = search_advising_notes(search_phrase='confound')
            notes = results['notes']
            total_note_count = results['totalNoteCount']
            assert len(notes) == 4
            assert total_note_count == 4
            # the most recent result is ranked first, though it contains only one instance of the search term.
            # the 2nd ranked result is slightly older than the 3rd, but ranked higher because it contains more instances of the search term.
            # the oldest result is ranked last, though it contains the most instances of the search term.
            assert notes[0]['id'] == recent_comment.id
            assert notes[0]['noteSnippet'] == '&quot;<strong>Confound</strong>&quot; appearing only once.'
            assert notes[1]['noteSnippet'] == 'I am <strong>confounded</strong> by this <strong>confounding</strong> student'
            assert '<strong>confounded</strong> that of himself' in notes[2]['noteSnippet']
            assert notes[3]['id'] == oldest_note.id
            assert notes[3]['noteSnippet'] == '<strong>Confound</strong> the <strong>confounders</strong>'

    def test_search_prefers_exact_text_matches(self, app, mock_advising_note_with_comments):  # noqa: ARG002
        """Ranks exact text matches highest, then adjacent words in order, then stemmed words in any order."""
        with (
            _create_coe_advisor_note(app, subject='Completed the online Orienteering. Has not selected any classes.') as single_exact_match,
            _create_coe_advisor_note(
                app,
                subject='Discussed selecting classes, then they selected 5 classes. Will follow up.',
            ) as double_phrase_match,
            _create_coe_advisor_note(app, subject='Classes classes classes have not been selected selected selected.') as triple_word_match,
        ):
            results = search_advising_notes(search_phrase='Has not selected any classes')
            notes = results['notes']
            total_note_count = results['totalNoteCount']
            assert len(notes) == 3
            assert total_note_count == 3
            assert notes[0]['id'] == single_exact_match.id
            assert notes[0]['noteSnippet'] == 'Completed the online Orienteering. <strong>Has</strong> <strong>not</strong> <strong>selected</strong> <strong>any</strong> <strong>classes</strong>.'  # noqa: E501
            assert notes[1]['id'] == double_phrase_match.id
            assert notes[1]['noteSnippet'] == 'Discussed <strong>selecting</strong> <strong>classes</strong>, then they <strong>selected</strong> 5 <strong>classes</strong>. Will follow up.'  # noqa: E501
            assert notes[2]['id'] == triple_word_match.id
            assert notes[2]['noteSnippet'] == '<strong>Classes</strong> <strong>classes</strong> <strong>classes</strong> have <strong>not</strong> been <strong>selected</strong> <strong>selected</strong> <strong>selected</strong>.'  # noqa: E501

    def test_search_advising_notes_multiple_terms(self):
        results = search_advising_notes(search_phrase='burnt diana temple')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert 'Herostratus lives that <strong>burnt</strong> the <strong>Temple</strong> of <strong>Diana</strong>' in notes[0]['noteSnippet']

    def test_search_advising_notes_no_match(self):
        results = search_advising_notes(search_phrase='pyramid octopus')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 0
        assert total_note_count == 0

    def test_search_advising_notes_funny_characters(self):
        results = search_advising_notes(search_phrase='horse & epitaph')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert 'Time hath spared the <strong>Epitaph</strong> of Adrians <strong>horse</strong>' in notes[0]['noteSnippet']

    def test_search_dates(self):
        results = search_advising_notes(search_phrase='2/1/2019 1:30')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert (
            'scheduled next appt. <strong>2/1/2019</strong> @ <strong>1</strong>:<strong>30</strong>. Student'
        ) in notes[0]['noteSnippet']
        results = search_advising_notes(search_phrase='1-24-19')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert 'drop Eng. 123 by <strong>1-24-19</strong>' in notes[0]['noteSnippet']

    def test_search_decimals(self):
        results = search_advising_notes(search_phrase='2.0')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert 'Student continued on <strong>2</strong>.<strong>0</strong> prob (COP) until Sp &#x27;19.' in notes[0]['noteSnippet']

    def test_search_email_address(self):
        results = search_advising_notes(search_phrase='E-mailed test@berkeley.edu')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert (
               'Student continued on 2.0 prob (COP) until Sp &#x27;19. <strong>E-mailed</strong> '
               '<strong>test</strong>@<strong>berkeley</strong>.<strong>edu</strong>:') in notes[0]['noteSnippet']

    def test_search_advising_notes_timestamp_format(self):
        results = search_advising_notes(search_phrase='confound')
        notes = results['notes']
        ucbconversion_note = notes[0]
        cs_note = notes[1]
        assert ucbconversion_note['createdAt']
        assert ucbconversion_note['updatedAt'] is None
        assert cs_note['createdAt']
        assert cs_note['updatedAt'] is None

    def test_search_advising_notes_includes_newly_created(self, app):
        with _create_coe_advisor_note(
            app,
            subject='Confound this note',
            body='and its successors and assigns',
        ):
            results = search_advising_notes(search_phrase='confound')
            notes = results['notes']
            total_note_count = results['totalNoteCount']
            assert len(notes) == 3
            assert total_note_count == 3
            assert notes[0]['noteSnippet'] == '<strong>Confound</strong> this note - and its successors and assigns'
            assert notes[1]['noteSnippet'] == 'I am <strong>confounded</strong> by this <strong>confounding</strong> student'
            assert notes[2]['noteSnippet'].startswith('...pity the founder')

    def test_search_advising_notes_paginates_new_and_old(self, app):
        """Correctly paginates the combined set of BOA notes and legacy notes."""
        def _create_note(i, parent_id=None):
            label = 'comment' if parent_id else 'note'
            return _create_coe_advisor_note(
                app,
                subject='Planned redundancy',
                body=f'Confounded {label} {i}',
                created_at=datetime.now() - timedelta(days=i),
                parent_note_id=parent_id,
            )

        with _create_note(1) as note, _create_note(2), _create_note(3), _create_note(4), _create_note(5), _create_note(6, note.id):
            results = search_advising_notes(search_phrase='confound', offset=0, limit=4)
            notes = results['notes']
            assert len(notes) == 4
            assert results['totalNoteCount'] == 8
            # results with similar text matches are ranked newest to oldest
            for index, note in enumerate(notes):
                assert note['noteSnippet'] == f'Planned redundancy - <strong>Confounded</strong> note {index + 1}'

            results = search_advising_notes(search_phrase='confound', offset=4, limit=4)
            notes = results['notes']
            assert len(notes) == 4
            assert results['totalNoteCount'] == 8
            assert notes[0]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 5'
            assert notes[1]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> comment 6'
            assert notes[2]['noteSnippet'] == 'I am <strong>confounded</strong> by this <strong>confounding</strong> student'
            assert notes[3]['noteSnippet'].startswith('...pity the founder')

    def test_search_advising_notes_narrowed_by_author(self, app):
        """Narrows results for both new and legacy advising notes by author SID."""
        def _create_note(author):
            return _create_coe_advisor_note(
                app,
                author_uid=author['uid'],
                author_name=author['name'],
                subject='Futher on France',
                body='Brigitte has been molded to middle class circumstance',
            )
        joni = {
            'name': 'Joni Mitchell',
            'uid': '1133399',
            'sid': '800700600',
        }
        not_joni = {
            'name': 'Oliver Heyer',
            'uid': '2040',
        }
        with _create_note(joni), _create_note(not_joni):
            wide_response = search_advising_notes(search_phrase='Brigitte')
            notes = wide_response['notes']
            total_note_count = wide_response['totalNoteCount']
            assert len(notes) == 4
            assert total_note_count == 4
            narrow_response = search_advising_notes(search_phrase='Brigitte', author_csid=joni['sid'])
            notes = narrow_response['notes']
            total_note_count = narrow_response['totalNoteCount']
            assert len(notes) == 2
            assert total_note_count == 2
            new_note, legacy_note = notes[0], notes[1]
            assert new_note['advisorUid'] == joni['uid']
            assert legacy_note['advisorSid'] == joni['sid']

    def test_search_advising_notes_narrowed_by_student(self, app):
        """Narrows results for both new and legacy advising notes by student SID."""
        def _create_note(sid):
            return _create_coe_advisor_note(
                app,
                sid=sid,
                subject='Case load',
                body='Another day, another student',
            )
        with _create_note('9000000000'), _create_note('9100000000'):
            wide_response = search_advising_notes(search_phrase='student')
            notes = wide_response['notes']
            total_note_count = wide_response['totalNoteCount']
            assert len(notes) == 5
            assert total_note_count == 5
            narrow_response = search_advising_notes(search_phrase='student', student_csid='9100000000')
            notes = narrow_response['notes']
            assert len(notes) == 2
            new_note, legacy_note = notes[0], notes[1]
            assert new_note['studentSid'] == '9100000000'
            assert legacy_note['studentSid'] == '9100000000'

    def test_search_advising_notes_restricted_to_students_in_loch(self, app):
        with _create_coe_advisor_note(
            app,
            sid='6767676767',
            subject='Who is this?',
            body="Not a student in the loch, that's for sure",
        ):
            assert len(search_advising_notes(search_phrase='loch')['notes']) == 0
            with _create_coe_advisor_note(
                app,
                sid='11667051',
                subject='A familiar face',
                body='Whereas this student is a most distinguished denizen of the loch',
            ):
                assert len(search_advising_notes(search_phrase='loch')['notes']) == 1

    def test_search_advising_notes_narrowed_by_topic(self, app):
        def _create_note(topic):
            return _create_coe_advisor_note(
                app,
                topics=[topic],
                subject='Brigitte',
            )
        with _create_note('Good Show'), _create_note('Bad Show'):
            wide_response = search_advising_notes(search_phrase='Brigitte')
            notes = wide_response['notes']
            total_note_count = wide_response['totalNoteCount']
            assert len(notes) == 4
            assert total_note_count == 4
            narrow_response = search_advising_notes(search_phrase='Brigitte', topic='Good Show')
            notes = narrow_response['notes']
            total_note_count = narrow_response['totalNoteCount']
            assert len(notes) == 2
            assert total_note_count == 2

    def test_search_legacy_advising_notes_narrowed_by_date(self, app):
        halloween_2017 = datetime(2017, 10, 31, tzinfo=pytz.timezone(app.config['TIMEZONE'])).astimezone(pytz.utc)
        days = [
            halloween_2017 - timedelta(days=1),
            halloween_2017,
            halloween_2017 + timedelta(days=1),
            halloween_2017 + timedelta(days=2),
            halloween_2017 + timedelta(days=3),
        ]
        unbounded = search_advising_notes(search_phrase='Brigitte')
        notes = unbounded['notes']
        total_note_count = unbounded['totalNoteCount']
        assert len(notes) == 2
        assert total_note_count == 2
        lower_bound = search_advising_notes(search_phrase='Brigitte', datetime_from=days[2])
        assert len(lower_bound['notes']) == 1
        upper_bound = search_advising_notes(search_phrase='Brigitte', datetime_to=days[2])
        assert len(upper_bound['notes']) == 1
        closed_1 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[0], datetime_to=days[2])
        assert len(closed_1['notes']) == 1
        closed_2 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[2], datetime_to=days[3])
        assert len(closed_2['notes']) == 1
        closed_3 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[0], datetime_to=days[3])
        assert len(closed_3['notes']) == 2
        closed_4 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[3], datetime_to=days[4])
        assert len(closed_4['notes']) == 0

    def test_search_new_advising_notes_narrowed_by_date(self, app):
        today = datetime.now().replace(hour=0, minute=0, second=0, tzinfo=pytz.timezone(app.config['TIMEZONE'])).astimezone(pytz.utc)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        with _create_coe_advisor_note(
            app,
            subject='Bryant Park',
            body='There were loads of them',
        ):
            assert len(search_advising_notes(search_phrase='Bryant')['notes']) == 1

            assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday)['notes']) == 1
            assert len(search_advising_notes(search_phrase='Bryant', datetime_to=yesterday)['notes']) == 0
            assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday, datetime_to=yesterday)['notes']) == 0

            assert len(search_advising_notes(search_phrase='Bryant', datetime_from=tomorrow)['notes']) == 0
            assert len(search_advising_notes(search_phrase='Bryant', datetime_to=tomorrow)['notes']) == 1
            assert len(search_advising_notes(search_phrase='Bryant', datetime_from=tomorrow, datetime_to=tomorrow)['notes']) == 0

            assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday, datetime_to=tomorrow)['notes']) == 1

    def test_every_filter_combination(self, mock_searchable_advising_notes, mock_legacy_ucbconversion_records):  # noqa: ARG002
        """Returns exactly the BOA notes and legacy notes matching all active filters, for all 256 combinations."""
        def _search_advising_notes(criteria):
            results = search_advising_notes(**criteria, offset=0, limit=SEARCH_RESULTS_LIMIT)
            return {
                'rows': results['notes'],
                'total': results['totalNoteCount'],
            }
        assert_every_search_filter_combination(
            filters=NOTE_SEARCH_FILTERS,
            search=_search_advising_notes,
            expected_keys=_expected_note_ids,
            limit=SEARCH_RESULTS_LIMIT,
        )

    def test_filters_are_not_vacuous(self, mock_searchable_advising_notes, mock_legacy_ucbconversion_records):  # noqa: ARG002
        """Each filter, applied alone, narrows the results and leaves at least one match."""
        assert_search_filters_not_vacuous(NOTE_SEARCH_FILTERS, _expected_note_ids)

    def test_private_notes_excluded(self, mock_searchable_advising_notes):
        """A private BOA note is never returned, even when it matches every filter."""
        public_note, private_note = mock_searchable_advising_notes[0], mock_searchable_advising_notes[-1]
        results = search_advising_notes(
            **active_search_criteria(NOTE_SEARCH_FILTERS, ('search_phrase', 'author_uid', 'student_csid', 'topic', 'datetime_from')),
            limit=SEARCH_RESULTS_LIMIT,
        )
        note_ids = [row['id'] for row in results['notes']]
        assert public_note.id in note_ids
        assert private_note.id not in note_ids

@contextmanager
def _create_coe_advisor_note(
    app,
    sid='11667051',
    subject='',
    body='',
    topics=(),
    author_uid=coe_advisor_uid,
    author_name='Balloon Man',
    author_role='Spherical',
    author_dept_codes='COENG',
    created_at=None,
    parent_note_id=None,
):
    note = Note.create(
        author_uid=author_uid,
        author_name=author_name,
        author_role=author_role,
        author_dept_codes=author_dept_codes,
        topics=topics,
        sid=sid,
        subject=subject,
        body=body,
        parent_note_id=parent_note_id,
    )
    if created_at:
        note.created_at = created_at
    std_commit(allow_test_environment=True)
    refresh_loch_note_search_index(app, notes=[note])
    yield note
    refresh_loch_note_search_index(app, deleted_notes=[note])
    Note.delete(note_id=note.id)
    std_commit(allow_test_environment=True)


def _advisor_uids(department_codes, advisor_uid, advisor_sid):
    """Department codes, when present, take precedence over an individual advisor UID."""
    if not department_codes:
        if advisor_uid:
            return {advisor_uid}
        if advisor_sid:
            return {row['ldap_uid'] for row in data_loch.safe_execute_rds(
                'SELECT ldap_uid FROM sis_data.basic_attributes WHERE sid = %(sid)s',
                sid=advisor_sid,
            )}
        return set()
    uids = set()
    for dept_code in department_codes:
        dept = UniversityDept.find_by_dept_code(dept_code)
        uids.update(membership.authorized_user.uid for membership in dept.authorized_users)
        for peer_dept in PeerAdvisingDepartment.find_by_university_dept_id(dept.id):
            for member in PeerAdvisingDepartmentMember.query.filter_by(peer_advising_department_id=peer_dept.id).all():
                uids.add(AuthorizedUser.find_by_id(member.authorized_user_id, include_deleted=True).uid)
    return uids


def _expected_note_ids(
        search_phrase=None,
        author_uid=None,
        author_csid=None,
        student_csid=None,
        department_codes=None,
        topic=None,
        datetime_from=None,
        datetime_to=None,
):
    boa_cdc = data_loch.boa_cdc_schema()
    legacy_notes = data_loch.advising_notes_schema()
    advisor_uids = _advisor_uids(department_codes, author_uid, author_csid)
    all_student_sids = {row['sid'] for row in data_loch.safe_execute_rds(f'SELECT sid FROM {data_loch.student_schema()}.student_profile_index')}
    note_ids = []

    boa_note_text_matches = expected_fts_results(f'{boa_cdc}.advising_notes_search_index', 'id', search_phrase, data_loch.safe_execute_rds)
    boa_topic_matches = get_topic_matches(f'{boa_cdc}.advising_note_topics', topic, data_loch.safe_execute_rds)
    boa_notes = data_loch.safe_execute_rds(f'SELECT id, boa_id, student_sid, advisor_uid, is_private, updated_at FROM {boa_cdc}.advising_notes')
    for row in boa_notes:
        if (
            not row['is_private']
            and (not boa_note_text_matches or row['id'] in boa_note_text_matches)
            and (not boa_topic_matches or row['id'] in boa_topic_matches)
            and (not advisor_uids or row['advisor_uid'] in advisor_uids)
            and (not student_csid or row['student_sid'] == student_csid)
            and (row['student_sid'] in all_student_sids)
            and in_date_range(row['updated_at'], datetime_from, datetime_to)
        ):
            note_ids.append(row['boa_id'])

    legacy_note_text_matches = expected_fts_results(f'{legacy_notes}.advising_notes_search_index', 'id', search_phrase, data_loch.safe_execute_rds)
    legacy_topic_matches = get_topic_matches(f'{legacy_notes}.advising_note_topics_curated', topic, data_loch.safe_execute_rds)
    legacy_notes = data_loch.safe_execute_rds(f"""
        SELECT id, student_sid, advisor_uid, advisor_sid, is_private, created_by, created_at, updated_at
          FROM {legacy_notes}.advising_notes""")
    for row in legacy_notes:
        if (
            not row['is_private']
            and (not legacy_note_text_matches or row['id'] in legacy_note_text_matches)
            and (not legacy_topic_matches or row['id'] in legacy_topic_matches)
            and legacy_advisor_match(row, advisor_uids, author_csid)
            and (not student_csid or row['student_sid'] == student_csid)
            and (row['student_sid'] in all_student_sids)
            and in_date_range(legacy_timestamp(row), datetime_from, datetime_to)
        ):
            note_ids.append(row['id'])
    return note_ids

