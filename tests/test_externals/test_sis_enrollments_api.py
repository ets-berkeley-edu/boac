import boac.externals.sis_enrollments_api as enrollments_api
from boac.lib.mockingbird import MockResponse, register_mock


class TestSisEnrollmentsApi:
    """SIS enrollments API query"""

    def test_get_enrollments(self, app):
        """returns unwrapped data"""
        oski_response = enrollments_api.get_enrollments(11667051, 2178)
        student = oski_response['student']
        assert student['names'][0]['formattedName'] == 'Oski Bear'
        assert student['emails'][0]['emailAddress'] == 'oski@berkeley.edu'

        enrollments = oski_response['studentEnrollments']
        assert len(enrollments) == 5

        assert enrollments[0]['classSection']['class']['course']['displayName'] == 'BURMESE 1A'
        assert enrollments[0]['classSection']['number'] == '001'
        assert enrollments[0]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[0]['enrolledUnits']['taken'] == 4
        assert enrollments[0]['gradingBasis']['code'] == 'GRD'
        assert enrollments[0]['grades'][0]['mark'] == 'B+'

        assert enrollments[1]['classSection']['class']['course']['displayName'] == 'MED ST 205'
        assert enrollments[1]['classSection']['number'] == '001'
        assert enrollments[1]['enrollmentStatus']['status']['code'] == 'D'
        assert enrollments[1]['enrolledUnits']['taken'] == 5
        assert enrollments[1]['gradingBasis']['code'] == 'GRD'

        assert enrollments[2]['classSection']['class']['course']['displayName'] == 'NUC ENG 124'
        assert enrollments[2]['classSection']['number'] == '002'
        assert enrollments[2]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[2]['enrolledUnits']['taken'] == 3
        assert enrollments[2]['gradingBasis']['code'] == 'PNP'
        assert enrollments[2]['grades'][0]['mark'] == 'P'

        assert enrollments[3]['classSection']['class']['course']['displayName'] == 'NUC ENG 124'
        assert enrollments[3]['classSection']['number'] == '201'
        assert enrollments[3]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[3]['enrolledUnits']['taken'] == 0
        assert enrollments[3]['gradingBasis']['code'] == 'NON'
        assert 'grades' not in enrollments[3]

        assert enrollments[4]['classSection']['class']['course']['displayName'] == 'PHYSED 11'
        assert enrollments[4]['classSection']['number'] == '001'
        assert enrollments[4]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[4]['enrolledUnits']['taken'] == 0.5
        assert enrollments[4]['gradingBasis']['code'] == 'PNP'
        assert enrollments[4]['grades'][0]['mark'] == 'P'

    def test_inner_get_enrollments(self, app):
        """returns fixture data"""
        oski_response = enrollments_api._get_enrollments(11667051, 2178)
        assert oski_response
        assert oski_response.status_code == 200

        student = oski_response.json()['apiResponse']['response']['student']
        assert student['names'][0]['formattedName'] == 'Oski Bear'
        assert student['emails'][0]['emailAddress'] == 'oski@berkeley.edu'

        enrollments = oski_response.json()['apiResponse']['response']['studentEnrollments']
        assert len(enrollments) == 5

        assert enrollments[0]['classSection']['class']['course']['displayName'] == 'BURMESE 1A'
        assert enrollments[0]['classSection']['number'] == '001'
        assert enrollments[0]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[0]['enrolledUnits']['taken'] == 4
        assert enrollments[0]['gradingBasis']['code'] == 'GRD'
        assert enrollments[0]['grades'][0]['mark'] == 'B+'

        assert enrollments[1]['classSection']['class']['course']['displayName'] == 'MED ST 205'
        assert enrollments[1]['classSection']['number'] == '001'
        assert enrollments[1]['enrollmentStatus']['status']['code'] == 'D'
        assert enrollments[1]['enrolledUnits']['taken'] == 5
        assert enrollments[1]['gradingBasis']['code'] == 'GRD'

        assert enrollments[2]['classSection']['class']['course']['displayName'] == 'NUC ENG 124'
        assert enrollments[2]['classSection']['number'] == '002'
        assert enrollments[2]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[2]['enrolledUnits']['taken'] == 3
        assert enrollments[2]['gradingBasis']['code'] == 'PNP'
        assert enrollments[2]['grades'][0]['mark'] == 'P'

        assert enrollments[3]['classSection']['class']['course']['displayName'] == 'NUC ENG 124'
        assert enrollments[3]['classSection']['number'] == '201'
        assert enrollments[3]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[3]['enrolledUnits']['taken'] == 0
        assert enrollments[3]['gradingBasis']['code'] == 'NON'
        assert 'grades' not in enrollments[3]

        assert enrollments[4]['classSection']['class']['course']['displayName'] == 'PHYSED 11'
        assert enrollments[4]['classSection']['number'] == '001'
        assert enrollments[4]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[4]['enrolledUnits']['taken'] == 0.5
        assert enrollments[4]['gradingBasis']['code'] == 'PNP'
        assert enrollments[4]['grades'][0]['mark'] == 'P'

    def test_user_not_found(self, app, caplog):
        """logs 404 for unknown user and returns informative message"""
        response = enrollments_api._get_enrollments(9999999, 2178)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not response
        assert response.raw_response.status_code == 404
        assert response.raw_response.json()['message']

    def test_server_error(self, app, caplog):
        """logs unexpected server errors and returns informative message"""
        api_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(enrollments_api._get_enrollments, api_error):
            response = enrollments_api._get_enrollments(11667051, 2178)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response
            assert response.raw_response.status_code == 500
            assert response.raw_response.json()['message']
