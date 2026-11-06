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


from boac.lib import util
from tests.util import override_config


class TestUtil:
    """Generic utilities."""

    def test_vacuum_whitespace(self):
        """Cleans up leading, trailing, and repeated whitespace."""
        assert util.vacuum_whitespace('  Firstname    Lastname   ') == 'Firstname Lastname'

    def test_titleize(self, app):
        """Converts a sentence to title case, excepting articles and abbreviations."""
        app.config['ABBREVIATED_WORDS'] = None
        assert util.titleize('head like a hole, black as your soul') == 'Head Like a Hole, Black as Your Soul'
        assert util.titleize('I\'D RATHER DIE THAN GIVE YOU CONTROL') == 'I\'d Rather Die Than Give You Control'
        app.config['ABBREVIATED_WORDS'] = ['BOW', 'YOU']
        assert util.titleize('bOw dOwn bEfOrE thE OnE yOu sErvE') == 'BOW Down Before the One YOU Serve'
        assert util.titleize('YOU\'RE GOING To GET WHAT (you) DESERVE') == 'You\'re Going to Get What (YOU) Deserve'

    def test_tolerant_remove(self):
        """Ignores error if item not found in list."""
        assert not util.tolerant_remove([], 'foo')
        a = ['foo', 'bar', 'baz']
        assert util.tolerant_remove(a, 'bar') is True
        assert a == ['foo', 'baz']

    def test_to_bool_or_none(self):
        """If None is not False in your use case then use this util."""
        assert util.to_bool_or_none(None) is None
        assert util.to_bool_or_none('true') is True
        assert util.to_bool_or_none('false') is False
        assert util.to_bool_or_none('FALSE') is False
        assert util.to_bool_or_none('blargh') is None

    def test_unix_timestamp_to_localtime(self):
        """Localizes timestamps."""
        assert util.unix_timestamp_to_localtime(1536300000).year == 2018
        assert util.unix_timestamp_to_localtime(1536300000).month == 9
        assert util.unix_timestamp_to_localtime(1536300000).day == 6
        assert util.unix_timestamp_to_localtime(1536300000).hour == 23
        assert util.unix_timestamp_to_localtime(1536305000).day == 7
        assert util.unix_timestamp_to_localtime(1536305000).hour == 0

    def test_clean_websearch_phrase(self):
        """Normalizes whitespace and removes word-exclusion hyphens, keeping hyphens inside words."""
        assert util.clean_websearch_phrase(None) == ''
        assert util.clean_websearch_phrase('   ') == ''
        assert util.clean_websearch_phrase('  late\t\n drop  ') == 'late drop'
        # A leading hyphen would exclude the word, so it is dropped wherever a word starts.
        assert util.clean_websearch_phrase('late -drop') == 'late drop'
        assert util.clean_websearch_phrase('-late --drop') == 'late drop'
        assert util.clean_websearch_phrase('late - drop') == 'late drop'
        # Input made only of exclusion hyphens leaves nothing to search for.
        assert util.clean_websearch_phrase(' - ') == ''
        # Hyphens inside a word are part of the token, so they stay.
        assert util.clean_websearch_phrase('1-14') == '1-14'
        assert util.clean_websearch_phrase('late-drop') == 'late-drop'
        # Full-width letters fold to their plain forms.
        assert util.clean_websearch_phrase('\uff4c\uff41\uff54\uff45 drop') == 'late drop'
        assert util.clean_websearch_phrase('abc def', max_length=5) == 'abc d'

    def test_clean_websearch_phrase_keeps_search_syntax(self):
        """Leaves quoted phrases and OR in place unless literal matching is requested."""
        assert util.clean_websearch_phrase('"late drop" or dogs') == '"late drop" or dogs'
        assert util.clean_websearch_phrase('"late drop" or -dogs', literal=True) == 'late drop dogs'
        assert util.clean_websearch_phrase('cats OR dogs', literal=True) == 'cats dogs'
        # Only the standalone word is an operator, not words that contain it.
        assert util.clean_websearch_phrase('orange order', literal=True) == 'orange order'
        assert util.clean_websearch_phrase('"', literal=True) == ''

    def test_escape_like(self):
        """Escapes LIKE wildcards and the escape character itself."""
        assert util.escape_like('plain') == 'plain'
        assert util.escape_like('100%') == '100\\%'
        assert util.escape_like('a_b') == 'a\\_b'
        assert util.escape_like('c:\\temp') == 'c:\\\\temp'


# Synthetic note text for the snippet tests. Filler words pad the note so that the phrase sits far from the start.
_FILLER = ' '.join(['filler'] * 20)


class TestSearchResultTextSnippet:
    """Search result snippets show the part of the text that best matches the whole query."""

    def test_prefers_contiguous_phrase_over_early_common_words(self, app):
        """A phrase late in the text wins over stop words that match near the start."""
        body = f'I wrote to ask for help with my schedule. {_FILLER} Although I finally submitted the missing lab report, the grade did not change.'
        with override_config(app, 'NOTES_SEARCH_RESULT_SNIPPET_PADDING', 5):
            snippet = util.search_result_text_snippet(body, 'Although I finally submitted the missing lab report')
        assert snippet.startswith('...')
        assert 'wrote' not in snippet
        assert (
            '<strong>Although</strong> <strong>I</strong> <strong>finally</strong> <strong>submitted</strong> '
            '<strong>the</strong> <strong>missing</strong> <strong>lab</strong> <strong>report</strong>'
        ) in snippet

    def test_shows_whole_phrase_longer_than_padding(self, app):
        """The window stretches to the end of a long phrase match instead of cutting it off."""
        body = f'{_FILLER} Although I finally submitted the missing lab report, the grade did not change. {_FILLER}'
        with override_config(app, 'NOTES_SEARCH_RESULT_SNIPPET_PADDING', 3):
            snippet = util.search_result_text_snippet(body, 'Although I finally submitted the missing lab report')
        assert '<strong>lab</strong> <strong>report</strong>' in snippet

    def test_stop_words_outside_phrase_are_not_bolded(self, app):
        """Common words are highlighted only as part of a matched phrase."""
        body = 'I asked for advice about calculus tutoring this term.'
        with override_config(app, 'NOTES_SEARCH_RESULT_SNIPPET_PADDING', 29):
            snippet = util.search_result_text_snippet(body, 'I need tutoring for calculus')
        assert snippet == 'I asked for advice about <strong>calculus</strong> <strong>tutoring</strong> this term.'

    def test_prefers_densest_cluster_of_terms(self, app):
        """Without a phrase match, the window goes where the most distinct query terms appear together."""
        body = f'Tutoring was mentioned once. {_FILLER} {_FILLER} We booked tutoring sessions before the calculus exam and the midterm.'
        with override_config(app, 'NOTES_SEARCH_RESULT_SNIPPET_PADDING', 5):
            snippet = util.search_result_text_snippet(body, 'midterm calculus tutoring')
        assert snippet.startswith('...')
        assert '<strong>calculus</strong>' in snippet
        assert '<strong>midterm</strong>' in snippet

    def test_single_term_uses_first_occurrence(self, app):
        """A one-word query still centers on its first match, using stemming."""
        body = f'{_FILLER} The student tested twice. {_FILLER} Tested again later.'
        with override_config(app, 'NOTES_SEARCH_RESULT_SNIPPET_PADDING', 2):
            snippet = util.search_result_text_snippet(body, 'test')
        assert snippet == '...The student <strong>tested</strong> twice. filler...'

    def test_stop_word_only_query_still_highlights(self, app):
        """If every query word is a stop word, those words are still treated as matches."""
        with override_config(app, 'NOTES_SEARCH_RESULT_SNIPPET_PADDING', 29):
            snippet = util.search_result_text_snippet('Where are the forms?', 'the')
        assert snippet == 'Where are <strong>the</strong> forms?'

    def test_no_match_is_escaped(self, app):
        """The fallback snippet is HTML-escaped like every other snippet, since the frontend renders it as HTML."""
        with override_config(app, 'NOTES_SEARCH_RESULT_SNIPPET_PADDING', 29):
            snippet = util.search_result_text_snippet('GPA &lt; 3.0 &amp; units &gt; 120', 'zebra')
        assert snippet == 'GPA &lt; 3.0 &amp; units &gt; 120'
