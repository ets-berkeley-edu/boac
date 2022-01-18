"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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
