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


from boac.externals import canvas
from boac.lib.mockingbird import MockResponse, register_mock


class TestCanvasGetCourseSections:
    """Canvas API query (get course sections)."""

    def test_get_course_sections(self, app):
        """Returns fixture data."""
        burmese_sections = canvas._get_course_sections(7654320)
        assert burmese_sections
        assert len(burmese_sections) == 3
        assert burmese_sections[0]['sis_section_id'] == 'SEC:2017-D-90100'
        assert burmese_sections[1]['sis_section_id'] == 'SEC:2017-D-90101'

        medieval_sections = canvas._get_course_sections(7654321)
        assert medieval_sections
        assert len(medieval_sections) == 1
        assert medieval_sections[0]['sis_section_id'] == 'SEC:2017-D-90200-88CA51BE'

        nuclear_sections = canvas._get_course_sections(7654323)
        assert nuclear_sections
        assert len(nuclear_sections) == 2
        assert nuclear_sections[0]['sis_section_id'] == 'SEC:2017-D-90299'
        assert nuclear_sections[1]['sis_section_id'] == 'SEC:2017-D-90300'

    def test_course_not_found(self, app, caplog):
        """Logs 404 for unknown course."""
        response = canvas._get_course_sections(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not response

    def test_server_error(self, app, caplog):
        """Logs unexpected server errors."""
        canvas_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(canvas._get_course_sections, canvas_error):
            response = canvas._get_course_sections(7654320)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response


class TestCanvasGetUserForUid:
    """Canvas API query (user for LDAP UID)."""

    def test_user_for_uid(self, app):
        """Returns fixture data."""
        oliver_response = canvas.get_user_for_uid(2040)
        assert oliver_response
        assert oliver_response['sortable_name'] == 'Heyer, Oliver'
        assert oliver_response['avatar_url'] == 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Donald_Duck.svg/618px-Donald_Duck.svg.png'

        paul_response = canvas.get_user_for_uid(242881)
        assert paul_response
        assert paul_response['sortable_name'] == 'Kerschen, Paul'
        assert paul_response['avatar_url'] == 'https://en.wikipedia.org/wiki/Daffy_Duck#/media/File:Daffy_Duck.svg'

    def test_user_not_found(self, app, caplog):
        """Logs 404 for unknown user and returns False rather than None."""
        response = canvas.get_user_for_uid(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert response is False

    def test_raw_user_not_found(self, app, caplog):
        """Logs 404 for unknown user and returns informative message."""
        response = canvas._get_user_for_uid(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not response
        assert response.raw_response.status_code == 404
        assert response.raw_response.json()['message']

    def test_raw_server_error(self, app, caplog):
        """Logs unexpected server errors and returns informative message."""
        canvas_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(canvas._get_user_for_uid, canvas_error):
            response = canvas._get_user_for_uid(2040)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response
            assert response.raw_response.status_code == 500
            assert response.raw_response.json()['message']


class TestCanvasGetUserCourses:
    """Canvas API query (get courses for user)."""

    def test_get_courses(self, app):
        """Returns a well-formed response from multiple terms."""
        courses = canvas.get_student_courses(61889)
        assert courses
        assert len(courses) == 5
        assert courses[0]['id'] == 7654320
        assert courses[0]['name'] == 'Introductory Burmese'
        assert courses[0]['course_code'] == 'BURMESE 1A'
        assert courses[0]['term']['name'] == 'Fall 2017'
        assert courses[1]['id'] == 7654321
        assert courses[1]['name'] == 'Medieval Manuscripts as Primary Sources'
        assert courses[1]['course_code'] == 'MED ST 205'
        assert courses[1]['term']['name'] == 'Fall 2017'
        assert courses[2]['id'] == 7654330
        assert courses[2]['name'] == 'Optional Friday Night Radioactivity Group'
        assert courses[2]['course_code'] == 'NUC ENG 124'
        assert courses[2]['term']['name'] == 'Fall 2017'
        assert courses[3]['id'] == 7654323
        assert courses[3]['name'] == 'Radioactive Waste Management'
        assert courses[3]['course_code'] == 'NUC ENG 124'
        assert courses[3]['term']['name'] == 'Fall 2017'
        assert courses[4]['id'] == 7654325
        assert courses[4]['name'] == 'Modern Statistical Prediction and Machine Learning'
        assert courses[4]['course_code'] == 'STAT 154'
        assert courses[4]['term']['name'] == 'Spring 2017'

    def test_student_enrollments(self, app):
        """Returns only enrollments of type 'student'."""
        courses = canvas.get_student_courses(61889)
        for course in courses:
            assert course['enrollments'][0]['type'] == 'student'
            assert course['enrollments'][0]['enrollment_state'] == 'active'

    def test_user_not_found(self, app, caplog):
        """Logs 404 for unknown user."""
        courses = canvas.get_student_courses(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not courses

    def test_server_error(self, app, caplog):
        """Logs unexpected server errors."""
        canvas_error = MockResponse(503, {}, '{"message": "Server at capacity, go away."}')
        with register_mock(canvas._get_all_user_courses, canvas_error):
            courses = canvas._get_all_user_courses(61889)
            assert 'HTTP/1.1" 503' in caplog.text
            assert not courses


class TestCanvasGetStudentSummariesForCourse:
    """Canvas API query (student summaries for course)."""

    def test_student_summaries(self, app):
        """Returns a large result set from paged Canvas API."""
        student_summaries = canvas._get_student_summaries(7654321)
        assert student_summaries
        assert len(student_summaries) == 730
        assert student_summaries[0]['id'] == 9000000
        assert student_summaries[0]['page_views'] == 567
        assert student_summaries[729]['id'] == 9000729
        assert student_summaries[729]['page_views'] == 400

    def test_course_not_found(self, app, caplog):
        """Logs 404 for unknown course."""
        student_summaries = canvas._get_student_summaries(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not student_summaries

    def test_server_error(self, app, caplog):
        """Logs unexpected server errors."""
        canvas_error = MockResponse(503, {}, '{"message": "Server at capacity, go away."}')
        with register_mock(canvas._get_student_summaries, canvas_error):
            student_summaries = canvas._get_student_summaries(7654321)
            assert 'HTTP/1.1" 503' in caplog.text
            assert not student_summaries


class TestCanvasGrades:
    """Canvas API queries for grade data."""

    def test_course_enrollments(self, app):
        """Returns course enrollments."""
        feed = canvas._get_course_enrollments(7654321)
        assert feed
        assert len(feed) == 43
        assert feed[0]['user_id'] == 9000100
        assert feed[0]['grades']['current_score'] == 86.125
        assert feed[42]['user_id'] == 5432100
        assert feed[42]['grades']['current_score'] == 91.0

    def test_assignments_analytics(self, app):
        """Returns course assignments analytics."""
        feed = canvas._get_assignments_analytics(7654321, 61889)
        assert feed
        assert len(feed) == 7
        assignment = feed[0]
        assert assignment['title'] == 'Essay #1'
        assert assignment['points_possible'] == 20.0
        assert assignment['max_score'] == 19.0
        assert assignment['min_score'] == 15.0
        assert assignment['first_quartile'] == 17.5
        assert assignment['median'] == 18.0
        assert assignment['third_quartile'] == 18.5
        assert assignment['submission']['score'] == 15.0
