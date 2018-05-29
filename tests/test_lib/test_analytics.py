"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


import io

from boac.externals import data_loch
from boac.lib import analytics
from boac.lib.mockingdata import MockRows, register_mock


class TestAnalytics:
    """Analytics."""

    def test_ordinal(self):
        """Format a whole number as a position."""
        assert analytics.ordinal(1) == '1st'
        assert analytics.ordinal(2) == '2nd'
        assert analytics.ordinal(3) == '3rd'
        for i in range(4, 20):
            assert analytics.ordinal(i) == f'{i}th'
        assert analytics.ordinal(21) == '21st'
        assert analytics.ordinal(22) == '22nd'
        assert analytics.ordinal(23) == '23rd'


class TestAnalyticsFromLochAssignmentsSubmitted:
    canvas_user_id = 9000100
    canvas_course_id = 7654321
    term_id = '2178'

    def test_from_fixture(self, app):
        digested = analytics.loch_assignments_submitted(self.canvas_user_id, self.canvas_course_id, self.term_id)
        assert digested['student']['raw'] == 8
        assert digested['student']['percentile'] == 64
        assert digested['student']['roundedUpPercentile'] == 81
        assert digested['courseDeciles'][0] == 0
        assert digested['courseDeciles'][9] == 10
        assert digested['courseDeciles'][10] == 17

    def test_small_difference(self, app):
        """Notices that small difference."""
        rows = [
            'canvas_user_id,submissions_turned_in',
            '9000000,1',
            str(self.canvas_user_id) + ',3',
        ]
        for i in range(101, 301):
            rows.append(str(i) + ',2')
        mr = MockRows(io.StringIO('\n'.join(rows)))
        with register_mock(data_loch._get_submissions_turned_in_relative_to_user, mr):
            worst = analytics.loch_assignments_submitted('9000000', self.canvas_course_id, self.term_id)
            best = analytics.loch_assignments_submitted(self.canvas_user_id, self.canvas_course_id, self.term_id)
            median = analytics.loch_assignments_submitted('101', self.canvas_course_id, self.term_id)

            for digested in [worst, best, median]:
                assert digested['boxPlottable'] is False
                assert digested['student']['percentile'] is not None
            assert worst['displayPercentile'] == '0th'
            assert worst['student']['raw'] == 1
            assert median['displayPercentile'] == '99th'
            assert median['student']['raw'] == 2
            assert median['student']['roundedUpPercentile'] == 99
            assert median['student']['percentile'] != 99
            assert best['displayPercentile'] == '100th'
            assert best['student']['raw'] == 3

    def test_with_loch_error(self, app):
        bad_course_id = 'NoSuchSite'
        digested = analytics.loch_assignments_submitted(self.canvas_user_id, bad_course_id, self.term_id)
        assert digested == {'error': 'Unable to retrieve from Data Loch'}

    def test_when_no_data(self, app):
        mr = MockRows(io.StringIO('canvas_user_id,assignments_submitted'))
        with register_mock(data_loch._get_submissions_turned_in_relative_to_user, mr):
            digested = analytics.loch_assignments_submitted(self.canvas_user_id, self.canvas_course_id, self.term_id)
        assert digested['student']['raw'] is None
        assert digested['student']['percentile'] is None
        assert digested['boxPlottable'] is False
        assert digested['courseDeciles'] is None


class TestAnalyticsFromLochAnalytics:
    canvas_user_id = 9000100
    canvas_course_id = 7654321
    term_id = '2178'

    def test_from_fixture(self, app):
        digested = analytics.loch_student_analytics(self.canvas_user_id, self.canvas_course_id, self.term_id)
        score = digested['currentScore']
        assert score['student']['raw'] == 84
        assert score['student']['percentile'] == 73
        assert score['student']['roundedUpPercentile'] == 76
        assert score['courseDeciles'][0] == 47
        assert score['courseDeciles'][9] == 94
        assert score['courseDeciles'][10] == 104
        last_activity = digested['lastActivity']
        assert last_activity['student']['raw'] == 1535275620
        assert 'daysSinceLastActivity' in last_activity['student']
        assert last_activity['student']['percentile'] == 93
        assert last_activity['student']['roundedUpPercentile'] == 90
        assert last_activity['courseDeciles'][0] == 1533021840
        assert last_activity['courseDeciles'][9] == 1535264940
        assert last_activity['courseDeciles'][10] == 1535533860

    def test_with_loch_error(self, app):
        bad_course_id = 'NoSuchSite'
        digested = analytics.loch_student_analytics(self.canvas_user_id, bad_course_id, self.term_id)
        _error = {'error': 'Unable to retrieve from Data Loch'}
        assert digested == {'currentScore': _error, 'lastActivity': _error}

    def test_when_no_data(self, app):
        mr = MockRows(io.StringIO('canvas_user_id,course_scores'))
        with register_mock(data_loch._get_canvas_course_scores, mr):
            digested = analytics.loch_student_analytics(self.canvas_user_id, self.canvas_course_id, self.term_id)
        score = digested['currentScore']
        assert score['student']['raw'] is None
        assert score['student']['percentile'] is None
        assert score['boxPlottable'] is False
        assert score['courseDeciles'] is None


class TestAnalyticsFromLochLastActivity:
    uid = '61889'
    canvas_course_id = 7654321
    term_id = '2178'

    def test_from_fixture(self, app):
        digested = analytics.loch_page_views(self.uid, self.canvas_course_id, self.term_id)
        assert digested['student']['raw'] == 766
        assert digested['student']['percentile'] == 54
        assert digested['courseDeciles'][0] == 9
        assert digested['courseDeciles'][9] == 917
        assert digested['courseDeciles'][10] == 31983

    def test_with_loch_error(self, app):
        bad_course_id = 'NoSuchSite'
        digested = analytics.loch_page_views(self.uid, bad_course_id, self.term_id)
        assert digested == {'error': 'Unable to retrieve from Data Loch'}

    def test_when_no_data(self, app):
        mr = MockRows(io.StringIO('uid,canvas_user_id,loch_page_views'))
        with register_mock(data_loch._get_course_page_views, mr):
            digested = analytics.loch_page_views(self.uid, self.canvas_course_id, self.term_id)
        assert digested['student']['raw'] is None
        assert digested['student']['percentile'] is None
        assert digested['boxPlottable'] is False
        assert digested['courseDeciles'] is None

    def test_when_no_records_for_this_student(self, app):
        lazy_uid = '211159'
        digested = analytics.loch_page_views(lazy_uid, self.canvas_course_id, self.term_id)
        assert digested['student']['raw'] == 0
        assert digested['student']['roundedUpPercentile'] == 0
        assert digested['courseDeciles'][0] == 0
        assert digested['courseDeciles'][10] == 31983
