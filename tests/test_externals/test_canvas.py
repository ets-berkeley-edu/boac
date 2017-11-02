import boac.externals.canvas as canvas
from boac.lib.mockingbird import MockResponse, register_mock


class TestCanvasGetCourseSections:
    """Canvas API query (get course sections)"""

    def test_get_course_sections(self, app):
        """returns fixture data"""
        burmese_sections = canvas.get_course_sections(7654320)
        assert burmese_sections
        assert len(burmese_sections) == 3
        assert burmese_sections[0]['sis_section_id'] == 'SEC:2017-D-90100'
        assert burmese_sections[1]['sis_section_id'] == 'SEC:2017-D-90101'

        medieval_sections = canvas.get_course_sections(7654321)
        assert medieval_sections
        assert len(medieval_sections) == 1
        assert medieval_sections[0]['sis_section_id'] == 'SEC:2017-D-90200-88CA51BE'

        nuclear_sections = canvas.get_course_sections(7654323)
        assert nuclear_sections
        assert len(nuclear_sections) == 2
        assert nuclear_sections[0]['sis_section_id'] == 'SEC:2017-D-90299'
        assert nuclear_sections[1]['sis_section_id'] == 'SEC:2017-D-90300'

    def test_course_not_found(self, app, caplog):
        """logs 404 for unknown course"""
        response = canvas.get_course_sections(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not response

    def test_server_error(self, app, caplog):
        """logs unexpected server errors"""
        canvas_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(canvas._get_course_sections, canvas_error):
            response = canvas._get_course_sections(7654320)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response


class TestCanvasGetUserForUid:
    """Canvas API query (user for LDAP UID)"""

    def test_user_for_uid(self, app):
        """returns fixture data"""
        oliver_response = canvas.get_user_for_uid(2040)
        assert oliver_response
        assert oliver_response['sortable_name'] == 'Heyer, Oliver'
        assert oliver_response['avatar_url'] == 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Donald_Duck.svg/618px-Donald_Duck.svg.png'

        paul_response = canvas.get_user_for_uid(242881)
        assert paul_response
        assert paul_response['sortable_name'] == 'Kerschen, Paul'
        assert paul_response['avatar_url'] == 'https://en.wikipedia.org/wiki/Daffy_Duck#/media/File:Daffy_Duck.svg'

    def test_user_not_found(self, app, caplog):
        """logs 404 for unknown user and returns False rather than None"""
        response = canvas.get_user_for_uid(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert response is False

    def test_raw_user_not_found(self, app, caplog):
        """logs 404 for unknown user and returns informative message"""
        response = canvas._get_user_for_uid(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not response
        assert response.raw_response.status_code == 404
        assert response.raw_response.json()['message']

    def test_raw_server_error(self, app, caplog):
        """logs unexpected server errors and returns informative message"""
        canvas_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(canvas._get_user_for_uid, canvas_error):
            response = canvas._get_user_for_uid(2040)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response
            assert response.raw_response.status_code == 500
            assert response.raw_response.json()['message']


class TestCanvasGetUserCourses:
    """Canvas API query (get courses for user)"""

    def test_get_courses(self, app):
        """returns a well-formed response"""
        courses = canvas.get_student_courses_in_term(61889)
        assert courses
        assert len(courses) == 3
        assert courses[0]['id'] == 7654320
        assert courses[0]['name'] == 'Introductory Burmese'
        assert courses[0]['course_code'] == 'BURMESE 1A'
        assert courses[1]['id'] == 7654321
        assert courses[1]['name'] == 'Medieval Manuscripts as Primary Sources'
        assert courses[1]['course_code'] == 'MED ST 205'
        assert courses[2]['id'] == 7654323
        assert courses[2]['name'] == 'Radioactive Waste Management'
        assert courses[2]['course_code'] == 'NUC ENG 124'

    def test_student_enrollments(self, app):
        """returns only enrollments of type 'student'"""
        courses = canvas.get_student_courses_in_term(61889)
        for course in courses:
            assert course['enrollments'][0]['type'] == 'student'

    def test_current_term(self, app):
        """returns only enrollments in current term"""
        courses = canvas.get_student_courses_in_term(61889)
        for course in courses:
            assert course['term']['name'] == app.config.get('CANVAS_CURRENT_ENROLLMENT_TERM')

    def test_user_not_found(self, app, caplog):
        """logs 404 for unknown user"""
        courses = canvas.get_student_courses_in_term(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not courses

    def test_server_error(self, app, caplog):
        """logs unexpected server errors"""
        canvas_error = MockResponse(503, {}, '{"message": "Server at capacity, go away."}')
        with register_mock(canvas._get_all_user_courses, canvas_error):
            courses = canvas._get_all_user_courses(61889)
            assert 'HTTP/1.1" 503' in caplog.text
            assert not courses


class TestCanvasGetStudentSummariesForCourse:
    """Canvas API query (student summaries for course)"""

    def test_student_summaries(self, app):
        """returns a large result set from paged Canvas API"""
        student_summaries = canvas.get_student_summaries(7654321)
        assert student_summaries
        assert len(student_summaries) == 730
        assert student_summaries[0]['id'] == 9000000
        assert student_summaries[0]['page_views'] == 567
        assert student_summaries[729]['id'] == 9000729
        assert student_summaries[729]['page_views'] == 400

    def test_course_not_found(self, app, caplog):
        """logs 404 for unknown course"""
        student_summaries = canvas.get_student_summaries(9999999)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not student_summaries

    def test_server_error(self, app, caplog):
        """logs unexpected server errors"""
        canvas_error = MockResponse(503, {}, '{"message": "Server at capacity, go away."}')
        with register_mock(canvas._get_student_summaries, canvas_error):
            student_summaries = canvas._get_student_summaries(7654321)
            assert 'HTTP/1.1" 503' in caplog.text
            assert not student_summaries
