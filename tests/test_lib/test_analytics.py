from boac.lib import analytics


class TestAnalyticsFromSummaryFeed:
    """Canvas analytics for student in course site"""
    canvas_course = {
        'canvasCourseId': 7654321,
    }
    canvas_user_id = '9000001'

    def test_insufficient_data(self, app):
        """notes insufficient data status"""
        summary_feed = [
            {
                'id': '9000000',
                'max_page_views': 3, 'max_participations': 3,
                'page_views': 0, 'page_views_level': 2,
                'participations': 0, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 5, 'late': 0, 'missing': 0, 'on_time': 0, 'total': 5},
            },
            {
                'id': self.canvas_user_id,
                'max_page_views': 3, 'max_participations': 3,
                'page_views': 0, 'page_views_level': 3,
                'participations': 0, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 5, 'late': 0, 'missing': 0, 'on_time': 0, 'total': 5},
            },
            {
                'id': '9000002',
                'max_page_views': 3, 'max_participations': 3,
                'page_views': 2, 'page_views_level': 2,
                'participations': 2, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 3, 'late': 0, 'missing': 0, 'on_time': 2, 'total': 5},
            },
        ]
        digested = analytics.analytics_from_summary_feed(summary_feed, self.canvas_user_id, self.canvas_course)
        assert digested['assignmentsOnTime']['insufficientData'] is True
        assert digested['assignmentsOnTime']['student']['zscore'] is not None
        assert digested['assignmentsOnTime']['student']['percentile'] is not None
        assert digested['pageViews']['insufficientData'] is True
        assert digested['pageViews']['student']['zscore'] is not None
        assert digested['pageViews']['student']['percentile'] is not None
        assert digested['participations']['insufficientData'] is True
        assert digested['participations']['student']['zscore'] is not None
        assert digested['participations']['student']['percentile'] is not None

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
        digested = analytics.analytics_from_summary_feed(summary_feed, self.canvas_user_id, self.canvas_course)
        assert digested['assignmentsOnTime']['insufficientData'] is True
        assert digested['assignmentsOnTime']['student'] == {'raw': 0, 'zscore': None, 'percentile': None}
        assert digested['pageViews']['insufficientData'] is False
        assert digested['participations']['insufficientData'] is True
        assert digested['participations']['student'] == {'raw': 0, 'zscore': None, 'percentile': None}

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
                'page_views': 0, 'page_views_level': 3,
                'participations': 0, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 3, 'late': 6, 'missing': 7, 'on_time': 0, 'total': 16},
            },
        ]
        for i in range(101, 301):
            summary_feed.append({
                'id': str(i),
                'max_page_views': 1218, 'max_participations': 11,
                'page_views': 1218, 'page_views_level': 2,
                'participations': 11, 'participations_level': 2,
                'tardiness_breakdown': {'floating': 0, 'late': 0, 'missing': 0, 'on_time': 16, 'total': 16},
            })

        digested = analytics.analytics_from_summary_feed(summary_feed, self.canvas_user_id, self.canvas_course)
        assert digested['assignmentsOnTime']['student']['percentile'] == 0
        assert digested['assignmentsOnTime']['insufficientData'] is False
        assert digested['pageViews']['student']['percentile'] == 0
        assert digested['pageViews']['insufficientData'] is False
        assert digested['participations']['student']['percentile'] == 0
        assert digested['participations']['insufficientData'] is False
