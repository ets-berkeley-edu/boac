import re
from boac.externals import sis_degree_progress_api
from boac.lib.mockingbird import MockResponse, register_mock


class TestSisDegreeProgressApi:
    """SIS Degree Progress API query"""

    def test_parsed(self, app):
        """returns the front-end-friendly data"""
        parsed = sis_degree_progress_api.parsed_degree_progress(11667051)
        assert parsed['reportDate'] == '2017-03-03'
        reqs = parsed['requirements']
        assert reqs['entryLevelWriting']['status'] == 'Satisfied'
        assert reqs['americanHistory']['status'] == 'Not Satisfied'
        assert reqs['americanCultures']['status'] == 'In Progress'
        assert reqs['americanInstitutions']['status'] == 'Not Satisfied'

    def test_get_degree_progress(self, app):
        """returns unwrapped data"""
        xml_dict = sis_degree_progress_api.get_degree_progress(11667051)
        degree_progress = xml_dict['UC_AA_PROGRESS']['PROGRESSES']['PROGRESS']
        assert degree_progress['RPT_DATE'] == '2017-03-03'
        assert degree_progress['REQUIREMENTS']['REQUIREMENT'][1]['NAME'] == 'American History (R-0002)'

    def test_inner_get_degree_progress(self, app):
        """returns fixture data"""
        oski_response = sis_degree_progress_api._get_degree_progress(11667051)
        assert oski_response
        assert oski_response.status_code == 200
        xml = oski_response.text
        assert re.search(r'<UC_AA_PROGRESS>', xml)

    def test_user_not_found(self, app, caplog):
        """returns False when CS delivers an error in the XML"""
        response = sis_degree_progress_api._get_degree_progress(9999999)
        assert response
        parsed = sis_degree_progress_api.get_degree_progress(9999999)
        assert not parsed

    def test_server_error(self, app, caplog):
        """logs unexpected server errors and returns informative message"""
        api_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(sis_degree_progress_api._get_degree_progress, api_error):
            response = sis_degree_progress_api._get_degree_progress(11667051)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response
            assert response.raw_response.status_code == 500
            assert response.raw_response.json()['message']
