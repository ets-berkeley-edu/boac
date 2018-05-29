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


import boac.externals.sis_enrollments_api as enrollments_api
from boac.lib.mockingbird import MockResponse, register_mock


class TestSisEnrollmentsApi:
    """SIS enrollments API query."""

    def test_get_drops_and_midterms(self, app):
        oski_response = enrollments_api.get_drops_and_midterms(11667051, 2172)
        drops = oski_response['droppedPrimarySections']
        assert len(drops) == 1
        assert drops[0]['displayName'] == 'MATH 136'
        assert drops[0]['component'] == 'LEC'
        assert drops[0]['sectionNumber'] == '001'
        assert drops[0]['dropDate'] == '2016-12-11'
        midterms = oski_response['midtermGrades']
        assert len(midterms) == 1
        assert midterms[80100] == 'F'

    def test_get_enrollments(self, app):
        """Returns unwrapped data."""
        oski_response = enrollments_api.get_enrollments(11667051, 2178)
        student = oski_response['student']

        # TODO These assertions are a subset of those in test_inner_get_enrollments below; we should see if pytest
        # parameterization will allow us to condense.
        assert student['names'][0]['formattedName'] == 'Oski Bear'
        assert student['emails'][0]['emailAddress'] == 'oski@berkeley.edu'

        enrollments = oski_response['studentEnrollments']
        assert len(enrollments) == 6

        assert enrollments[0]['classSection']['class']['course']['displayName'] == 'BURMESE 1A'
        assert enrollments[0]['classSection']['number'] == '001'
        assert enrollments[0]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[0]['enrolledUnits']['taken'] == 4
        assert enrollments[0]['gradingBasis']['code'] == 'GRD'
        assert enrollments[0]['grades'][0]['type']['code'] == 'MID'
        assert enrollments[0]['grades'][0]['mark'] == 'D+'

        assert enrollments[5]['classSection']['class']['course']['displayName'] == 'PHYSED 11'
        assert enrollments[5]['classSection']['number'] == '001'
        assert enrollments[5]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[5]['enrolledUnits']['taken'] == 0.5
        assert enrollments[5]['gradingBasis']['code'] == 'PNP'
        assert enrollments[5]['grades'][0]['mark'] == 'P'

    def test_inner_get_enrollments(self, app):
        """Returns fixture data."""
        oski_response = enrollments_api._get_enrollments(11667051, 2178)
        assert oski_response
        assert oski_response.status_code == 200

        student = oski_response.json()['apiResponse']['response']['student']
        assert student['names'][0]['formattedName'] == 'Oski Bear'
        assert student['emails'][0]['emailAddress'] == 'oski@berkeley.edu'

        enrollments = oski_response.json()['apiResponse']['response']['studentEnrollments']
        assert len(enrollments) == 6

        assert enrollments[0]['classSection']['class']['course']['displayName'] == 'BURMESE 1A'
        assert enrollments[0]['classSection']['number'] == '001'
        assert enrollments[0]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[0]['enrolledUnits']['taken'] == 4
        assert enrollments[0]['gradingBasis']['code'] == 'GRD'
        assert enrollments[0]['grades'][0]['type']['code'] == 'MID'
        assert enrollments[0]['grades'][0]['mark'] == 'D+'

        assert enrollments[1]['classSection']['class']['course']['displayName'] == 'MED ST 205'
        assert enrollments[1]['classSection']['number'] == '001'
        assert enrollments[1]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[1]['enrolledUnits']['taken'] == 5
        assert enrollments[1]['gradingBasis']['code'] == 'GRD'

        assert enrollments[2]['classSection']['class']['course']['displayName'] == 'MUSIC 41C'
        assert enrollments[2]['classSection']['number'] == '002'
        assert enrollments[2]['enrollmentStatus']['status']['code'] == 'D'
        assert enrollments[2]['enrolledUnits']['taken'] == 2
        assert enrollments[2]['gradingBasis']['code'] == 'PNP'
        assert 'grades' not in enrollments[2]

        assert enrollments[3]['classSection']['class']['course']['displayName'] == 'NUC ENG 124'
        assert enrollments[3]['classSection']['number'] == '201'
        assert enrollments[3]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[3]['enrolledUnits']['taken'] == 0
        assert enrollments[3]['gradingBasis']['code'] == 'NON'
        assert 'grades' not in enrollments[3]

        assert enrollments[4]['classSection']['class']['course']['displayName'] == 'NUC ENG 124'
        assert enrollments[4]['classSection']['number'] == '002'
        assert enrollments[4]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[4]['enrolledUnits']['taken'] == 3
        assert enrollments[4]['gradingBasis']['code'] == 'PNP'
        assert enrollments[4]['grades'][0]['mark'] == 'P'

        assert enrollments[5]['classSection']['class']['course']['displayName'] == 'PHYSED 11'
        assert enrollments[5]['classSection']['number'] == '001'
        assert enrollments[5]['enrollmentStatus']['status']['code'] == 'E'
        assert enrollments[5]['enrolledUnits']['taken'] == 0.5
        assert enrollments[5]['gradingBasis']['code'] == 'PNP'
        assert enrollments[5]['grades'][0]['mark'] == 'P'

    def test_user_not_found(self, app, caplog):
        """Logs 404 for unknown user and returns informative message."""
        response = enrollments_api._get_enrollments(9999999, 2178)
        assert 'HTTP/1.1" 404' in caplog.text
        assert not response
        assert response.raw_response.status_code == 404
        assert response.raw_response.json()['message']

    def test_server_error(self, app, caplog):
        """Logs unexpected server errors and returns informative message."""
        api_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(enrollments_api._get_enrollments, api_error):
            response = enrollments_api._get_enrollments(11667051, 2178)
            assert 'HTTP/1.1" 500' in caplog.text
            assert not response
            assert response.raw_response.status_code == 500
            assert response.raw_response.json()['message']
