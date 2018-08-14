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


import pytest
import simplejson as json

asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'


@pytest.fixture()
def asc_advisor(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor(fake_auth):
    fake_auth.login(coe_advisor_uid)


class TestAthletics:
    """Athletics API."""

    def test_team_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        response = client.get('/api/team/FHW')
        assert response.status_code == 401

    def test_teams_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        response = client.get('/api/teams/all')
        assert response.status_code == 401

    def test_team_not_authorized(self, client, coe_advisor):
        """Returns 404 if not authorized."""
        response = client.get('/api/team/FHW')
        assert response.status_code == 404

    def test_teams_not_authorized(self, client, coe_advisor):
        """Returns 404 if not authorized."""
        response = client.get('/api/teams/all')
        assert response.status_code == 404

    def test_team_groups_not_authorized(self, client, coe_advisor):
        """Returns 404 if not authorized."""
        response = client.get('/api/team_groups/all')
        assert response.status_code == 200
        assert not response.json

    def test_get_all_team_groups(self, asc_advisor, client):
        """Returns all team-groups if authenticated."""
        response = client.get('/api/team_groups/all')
        assert response.status_code == 200
        team_groups = response.json
        group_codes = [team_group['groupCode'] for team_group in team_groups]
        group_names = [team_group['groupName'] for team_group in team_groups]
        assert ['MFB-DB', 'MFB-DL', 'MBB', 'MBB-AA', 'MTE', 'WFH', 'WTE'] == group_codes
        assert [
            'Football, Defensive Backs',
            'Football, Defensive Line',
            'Men\'s Baseball',
            'Men\'s Baseball (AA)',
            'Men\'s Tennis',
            'Women\'s Field Hockey',
            'Women\'s Tennis',
        ] == group_names
        total_student_counts = [team_group['totalStudentCount'] for team_group in team_groups]
        assert [3, 4, 1, 1, 2, 2, 2] == total_student_counts

    def test_get_all_teams(self, asc_advisor, client):
        """Returns all teams if authenticated."""
        response = client.get('/api/teams/all')
        assert response.status_code == 200
        teams = response.json
        assert len(teams) == 5
        team_codes = [team['code'] for team in teams]
        team_names = [team['name'] for team in teams]
        total_student_counts = [team['totalStudentCount'] for team in teams]
        assert ['FBM', 'BAM', 'TNM', 'FHW', 'TNW'] == team_codes
        assert ['Football', 'Men\'s Baseball', 'Men\'s Tennis', 'Women\'s Field Hockey', 'Women\'s Tennis'] == team_names
        assert [3, 2, 1, 1, 1] == total_student_counts
        football = teams[0]
        assert football['code'] == 'FBM'
        assert football['name'] == 'Football'
        assert football['totalStudentCount'] == 3

    def test_team_not_found(self, asc_advisor, client):
        """Returns code as name when no code-to-name translation exists."""
        response = client.get('/api/team/XYZ')
        assert response.status_code == 404
        assert 'code' not in response.json
        assert 'No team found' in json.loads(response.data)['message']

    def test_team_with_athletes_in_multiple_groups(self, asc_advisor, client):
        """Returns a well-formed response on a valid code if authenticated."""
        response = client.get('/api/team/FBM?orderBy=last_name')
        assert response.status_code == 200
        team = response.json
        assert team['code'] == 'FBM'
        assert team['name'] == 'Football'
        assert 'teamGroups' in team
        group_codes = [team_group['groupCode'] for team_group in team['teamGroups']]
        assert ['MFB-DB', 'MFB-DL'] == group_codes
        assert team['totalStudentCount'] == 3
        students = team['students']
        assert len(students) == 3
        sid_list = [student['sid'] for student in students]
        assert ['2345678901', '5678901234', '3456789012'] == sid_list
        athlete = students[0]
        assert athlete['name'] == 'Dave Doolittle'
        assert athlete['sid'] == '2345678901'
        assert athlete['athleticsProfile']['inIntensiveCohort'] is False

    def test_includes_student_sis_data(self, asc_advisor, client):
        """Includes SIS data for team members."""
        response = client.get('/api/team/FHW')
        athlete = response.json['students'][0]
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['English BA', 'Nuclear Engineering BS']

    def test_includes_student_current_enrollments(self, asc_advisor, client):
        """Includes current-term active enrollments and analytics for team members."""
        response = client.get('/api/team/FHW')
        athlete = response.json['students'][0]
        term = athlete['term']
        assert term['termName'] == 'Fall 2017'
        assert term['enrolledUnits'] == 12.5
        assert len(term['enrollments']) == 4
        assert term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(term['enrollments'][0]['canvasSites']) == 1

    def test_get_team_order_by(self, asc_advisor, client):
        expected = {
            'first_name': ['2345678901', '3456789012', '5678901234'],
            'gpa': ['3456789012', '2345678901', '5678901234'],
            'group_name': ['2345678901', '5678901234', '3456789012'],
            'last_name': ['2345678901', '5678901234', '3456789012'],
            'level': ['2345678901', '3456789012', '5678901234'],
            'major': ['2345678901', '3456789012', '5678901234'],
            'units': ['2345678901', '3456789012', '5678901234'],
        }
        for order_by, first_uid in expected.items():
            response = client.get(f'/api/team/FBM?orderBy={order_by}')
            assert response.status_code == 200, f'Non-200 response where order_by={order_by}'
            cohort = json.loads(response.data)
            assert cohort['totalStudentCount'] == 3, f'Wrong count where order_by={order_by}'
            sid_list = [s['sid'] for s in cohort['students']]
            assert sid_list == expected[order_by], f'Unmet expectation where order_by={order_by}'
