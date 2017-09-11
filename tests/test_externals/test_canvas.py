import pytest

from boac.lib.mockingbird import MockResponse, register_mock
import boac.externals.canvas as canvas


@pytest.fixture
def ucb_canvas(app):
    return app.canvas_instance


class TestCanvasGetUserForSisId:
    """Canvas API query (user for SIS ID)"""

    def test_user_for_sis_id(self, ucb_canvas):
        """returns fixture data"""
        oliver_response = canvas.get_user_for_sis_id(ucb_canvas, 2040)
        assert oliver_response
        assert oliver_response.status_code == 200
        assert oliver_response.json()['sortable_name'] == 'Heyer, Oliver'
        assert oliver_response.json()['avatar_url'] == 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Donald_Duck.svg/618px-Donald_Duck.svg.png'

        paul_response = canvas.get_user_for_sis_id(ucb_canvas, 242881)
        assert paul_response
        assert paul_response.status_code == 200
        assert paul_response.json()['sortable_name'] == 'Kerschen, Paul'
        assert paul_response.json()['avatar_url'] == 'https://en.wikipedia.org/wiki/Daffy_Duck#/media/File:Daffy_Duck.svg'

    def test_user_not_found(self, ucb_canvas, caplog):
        """logs 404 for unknown user and returns informative message"""
        response = canvas.get_user_for_sis_id(ucb_canvas, 9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not response
        assert response.raw_response.status_code == 404
        assert response.raw_response.json()['message']

    def test_server_error(self, ucb_canvas, caplog):
        """logs unexpected server errors and returns informative message"""
        canvas_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(canvas.get_user_for_sis_id, canvas_error):
            response = canvas.get_user_for_sis_id(ucb_canvas, 2040)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response
            assert response.raw_response.status_code == 500
            assert response.raw_response.json()['message']


class TestCanvasGetStudentSummariesForCourse:
    """Canvas API query (student summaries for course)"""

    def test_student_summaries(self, ucb_canvas):
        """returns a large result set from paged Canvas API"""
        student_summaries = canvas.get_student_summaries(ucb_canvas, 7654321)
        assert student_summaries
        assert len(student_summaries) == 730
        assert student_summaries[0]['id'] == 9000000
        assert student_summaries[0]['page_views'] == 567
        assert student_summaries[729]['id'] == 9000729
        assert student_summaries[729]['page_views'] == 400

    def test_course_not_found(self, ucb_canvas, caplog):
        """logs 404 for unknown course and returns wrapped exception"""
        student_summaries = canvas.get_student_summaries(ucb_canvas, 9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not student_summaries
        assert student_summaries.raw_response.status_code == 404
        assert student_summaries.raw_response.json()['message']

    def test_server_error(self, ucb_canvas, caplog):
        """logs unexpected server errors and returns wrapped exception"""
        canvas_error = MockResponse(503, {}, '{"message": "Server at capacity, go away."}')
        with register_mock(canvas.get_student_summaries, canvas_error):
            student_summaries = canvas.get_student_summaries(ucb_canvas, 7654321)
            assert 'HTTP/1.1" 503' in caplog.text
            assert not student_summaries
            assert student_summaries.raw_response.status_code == 503
            assert student_summaries.raw_response.json()['message']
