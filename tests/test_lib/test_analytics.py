from boac.externals import canvas
from boac.lib import analytics


class TestAnalytics:
    """Analytics"""

    def test_ordinal(self):
        """Format a whole number as a position"""
        assert analytics.ordinal(1) == '1st'
        assert analytics.ordinal(2) == '2nd'
        assert analytics.ordinal(3) == '3rd'
        for i in range(4, 20):
            assert analytics.ordinal(i) == '{}th'.format(i)
        assert analytics.ordinal(21) == '21st'
        assert analytics.ordinal(22) == '22nd'
        assert analytics.ordinal(23) == '23rd'

    def test_canvas_course_scores(self, app):
        """Summarizes scored assignments in fixture"""
        canvas_user_id = 9000100
        canvas_course_id = 7654321
        feed = canvas.get_course_enrollments(canvas_course_id, '2178')
        digested = analytics.analytics_from_canvas_course_enrollments(feed, canvas_user_id)
        course_current_score = digested['courseCurrentScore']
        assert course_current_score['boxPlottable'] is True
        assert course_current_score['summary'] == '8th percentile'
        assert course_current_score['student']['percentile'] == 8
        assert course_current_score['student']['raw'] == 86.0
        assert course_current_score['student']['roundedUpPercentile'] == 11

    def test_no_canvas_course_scores(self, app):
        """Handles complete absence of scored assignments"""
        canvas_user_id = 9000100
        canvas_course_id = 7654321
        feed = canvas.get_course_enrollments(canvas_course_id, '2178')
        # Mimic an unscored site.
        for row in feed:
            row['grades']['current_grade'] = None
            row['grades']['current_score'] = None
            row['grades']['final_grade'] = None
            row['grades']['final_score'] = None
        digested = analytics.analytics_from_canvas_course_enrollments(feed, canvas_user_id)
        course_current_score = digested['courseCurrentScore']
        assert course_current_score['boxPlottable'] is False
        assert course_current_score['summary'] == 'No data'
        assert course_current_score['student']['percentile'] is None
        assert course_current_score['student']['raw'] is None
        assert course_current_score['student']['roundedUpPercentile'] is None


class TestAnalyticsFromSummaryFeed:
    """Canvas course summary analytics"""
    canvas_course_id = 7654321
    canvas_user_id = '9000001'

    def test_small_difference(self, app):
        """notices that small difference"""
        summary_feed = [
            {
                'id': '9000000',
                'max_page_views': 1218, 'max_participations': 4,
                'page_views': 800, 'page_views_level': 2,
                'participations': 3, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 0, 'late': 2, 'missing': 0, 'on_time': 1, 'total': 3},
            },
            {
                'id': self.canvas_user_id,
                'max_page_views': 1218, 'max_participations': 11,
                'page_views': 0, 'page_views_level': 3,
                'participations': 0, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 0, 'late': 0, 'missing': 0, 'on_time': 3, 'total': 3},
            },
        ]
        for i in range(101, 301):
            summary_feed.append({
                'id': str(i),
                'max_page_views': 1218, 'max_participations': 11,
                'page_views': 1218, 'page_views_level': 2,
                'participations': 11, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 0, 'late': 1, 'missing': 0, 'on_time': 2, 'total': 3},
            })

        worst = analytics.analytics_from_summary_feed(summary_feed, '9000000', self.canvas_course_id)
        best = analytics.analytics_from_summary_feed(summary_feed, self.canvas_user_id, self.canvas_course_id)
        median = analytics.analytics_from_summary_feed(summary_feed, '101', self.canvas_course_id)
        for digested in [worst, best, median]:
            for column in ['assignmentsOnTime', 'pageViews', 'participations']:
                assert digested[column]['boxPlottable'] is False
                assert digested[column]['student']['percentile'] is not None

        assert worst['assignmentsOnTime']['summary'] == '0th percentile : score 1, maximum 3'
        assert median['assignmentsOnTime']['summary'] == '99th percentile : score 2, maximum 3'
        assert median['assignmentsOnTime']['student']['roundedUpPercentile'] == 99
        assert median['assignmentsOnTime']['student']['percentile'] != 99
        assert best['assignmentsOnTime']['summary'] == '100th percentile : score 3, maximum 3'

    def test_insufficient_data(self, app):
        """notes insufficient data status"""
        summary_feed = [
            {
                'id': '9000000',
                'max_page_views': 11, 'max_participations': 1,
                'page_views': 11, 'page_views_level': 2,
                'participations': 1, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 5, 'late': 0, 'missing': 0, 'on_time': 1, 'total': 6},
            },
            {
                'id': self.canvas_user_id,
                'max_page_views': 11, 'max_participations': 1,
                'page_views': 11, 'page_views_level': 2,
                'participations': 1, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 5, 'late': 0, 'missing': 0, 'on_time': 1, 'total': 6},
            },
            {
                'id': '9000002',
                'max_page_views': 11, 'max_participations': 1,
                'page_views': 11, 'page_views_level': 2,
                'participations': 1, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 5, 'late': 0, 'missing': 0, 'on_time': 1, 'total': 6},
            },
        ]
        digested = analytics.analytics_from_summary_feed(summary_feed, self.canvas_user_id, self.canvas_course_id)
        for column in ['assignmentsOnTime', 'pageViews', 'participations']:
            assert digested[column]['boxPlottable'] is False
            assert digested[column]['summary'] == 'Insufficient data'
            assert digested[column]['student']['percentile'] is None

    def test_zero_counts(self, app):
        """does not calculate statistics on a void"""
        summary_feed = [
            {
                'id': '9000000',
                'max_page_views': 247, 'max_participations': 0,
                'page_views': 29, 'page_views_level': 2,
                'participations': 0, 'participations_level': 0,
                'tardiness_breakdown': {'floating': 0, 'late': 0, 'missing': 0, 'on_time': 0, 'total': 0},
            },
            {
                'id': self.canvas_user_id,
                'max_page_views': 247, 'max_participations': 0,
                'page_views': 6, 'page_views_level': 3,
                'participations': 0, 'participations_level': 0,
                'tardiness_breakdown': {'floating': 0, 'late': 0, 'missing': 0, 'on_time': 0, 'total': 0},
            },
            {
                'id': '9000002',
                'max_page_views': 3, 'max_participations': 0,
                'page_views': 247, 'page_views_level': 3,
                'participations': 0, 'participations_level': 0,
                'tardiness_breakdown': {'floating': 0, 'late': 0, 'missing': 0, 'on_time': 0, 'total': 0},
            },
        ]
        digested = analytics.analytics_from_summary_feed(summary_feed, self.canvas_user_id, self.canvas_course_id)
        for column in ['assignmentsOnTime', 'participations']:
            assert digested[column]['boxPlottable'] is False
            assert digested[column]['summary'] == 'No data'
            assert digested[column]['student']['percentile'] is None

    def test_zeroth_percentile(self, app):
        """returns statistics even if this student did sweet nothing"""
        summary_feed = [
            {
                'id': '9000000',
                'max_page_views': 1218, 'max_participations': 11,
                'page_views': 800, 'page_views_level': 2,
                'participations': 6, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 0, 'late': 1, 'missing': 0, 'on_time': 15, 'total': 16},
            },
            {
                'id': self.canvas_user_id,
                'max_page_views': 1218, 'max_participations': 11,
                'page_views': None, 'page_views_level': 3,
                'participations': 0, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 3, 'late': 6, 'missing': 7, 'on_time': 0, 'total': 16},
            },
        ]
        for i in range(1118, 1218):
            summary_feed.append({
                'id': str(i),
                'max_page_views': 1218, 'max_participations': 11,
                'page_views': i, 'page_views_level': 2,
                'participations': 11, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 0, 'late': 0, 'missing': 0, 'on_time': 16, 'total': 16},
            })

        digested = analytics.analytics_from_summary_feed(summary_feed, self.canvas_user_id, self.canvas_course_id)
        print('zeroth = {}'.format(repr(digested)))
        for column in ['assignmentsOnTime', 'participations']:
            assert digested[column]['boxPlottable'] is False
            assert digested[column]['student']['percentile'] is not None
        assert digested['assignmentsOnTime']['summary'] == '0th percentile : score 0, maximum 16'
        assert digested['participations']['summary'] == '0th percentile : score 0, maximum 11'
        assert digested['pageViews']['summary'] == '0th percentile'
        assert digested['pageViews']['boxPlottable'] is True
