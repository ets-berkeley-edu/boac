import pytest
import simplejson as json

test_uid = '1133399'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


class TestAthletics:
    """Athletics API"""

    def test_team_not_authenticated(self, client):
        """returns 401 if not authenticated"""
        response = client.get('/api/team/FHW')
        assert response.status_code == 401

    def test_teams_not_authenticated(self, client):
        """returns 401 if not authenticated"""
        response = client.get('/api/teams/all')
        assert response.status_code == 401

    def test_get_all_team_groups(self, authenticated_session, client):
        """returns all team-groups if authenticated"""
        response = client.get('/api/team_groups/all')
        assert response.status_code == 200
        team_groups = response.json
        group_codes = [team_group['groupCode'] for team_group in team_groups]
        group_names = [team_group['groupName'] for team_group in team_groups]
        total_member_counts = [team_group['totalMemberCount'] for team_group in team_groups]
        assert ['MFB-DB', 'MFB-DL', 'MBB-AA', 'MTE-AA', 'WFH-AA', 'WTE-AA'] == group_codes
        assert [
            'Football, Defensive Backs',
            'Football, Defensive Line',
            'Men\'s Baseball',
            'Men\'s Tennis',
            'Women\'s Field Hockey',
            'Women\'s Tennis',
        ] == group_names
        assert [2, 3, 1, 1, 1, 1] == total_member_counts

    def test_get_all_teams(self, authenticated_session, client):
        """returns all teams if authenticated"""
        response = client.get('/api/teams/all')
        assert response.status_code == 200
        teams = response.json
        assert len(teams) == 5
        team_codes = [team['code'] for team in teams]
        team_names = [team['name'] for team in teams]
        total_member_counts = [team['totalMemberCount'] for team in teams]
        assert ['FBM', 'MBB', 'TNM', 'FHW', 'TNW'] == team_codes
        assert ['Football', 'Men\'s Baseball', 'Men\'s Tennis', 'Women\'s Field Hockey', 'Women\'s Tennis'] == team_names
        assert [3, 1, 1, 1, 1] == total_member_counts
        football = teams[0]
        assert football['code'] == 'FBM'
        assert football['name'] == 'Football'
        assert football['totalMemberCount'] == 3

    def test_team_not_found(self, authenticated_session, client):
        """returns code as name when no code-to-name translation exists"""
        response = client.get('/api/team/XYZ')
        assert response.status_code == 404
        assert 'code' not in response.json
        assert 'No team found' in json.loads(response.data)['message']

    def test_team_with_athletes_in_multiple_groups(self, authenticated_session, client):
        """returns a well-formed response on a valid code if authenticated"""
        response = client.get('/api/team/FBM?orderBy=last_name')
        assert response.status_code == 200
        team = response.json
        assert team['code'] == 'FBM'
        assert team['name'] == 'Football'
        assert 'teamGroups' in team
        group_codes = [team_group['groupCode'] for team_group in team['teamGroups']]
        assert ['MFB-DB', 'MFB-DL'] == group_codes
        assert team['totalMemberCount'] == 3
        members = team['members']
        assert len(members) == 3
        sid_list = [member['sid'] for member in members]
        assert ['2345678901', '5678901234', '3456789012'] == sid_list
        athlete = members[0]
        assert athlete['firstName'] == 'Oliver'
        assert athlete['lastName'] == 'Heyer'
        assert athlete['uid'] == '2040'
        assert athlete['inIntensiveCohort'] is False

    def test_includes_student_sis_data(self, authenticated_session, client):
        """includes SIS data for team members"""
        response = client.get('/api/team/FHW')
        athlete = response.json['members'][0]
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['Astrophysics BS', 'English BA']

    def test_includes_student_current_enrollments(self, authenticated_session, client):
        """includes current-term active enrollments and analytics for team members"""
        response = client.get('/api/team/FHW')
        athlete = response.json['members'][0]
        assert athlete['currentTerm']['termName'] == 'Fall 2017'
        assert athlete['currentTerm']['enrolledUnits'] == 12.5
        assert len(athlete['currentTerm']['enrollments']) == 3
        assert athlete['currentTerm']['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(athlete['currentTerm']['enrollments'][0]['canvasSites']) == 1

    def test_get_team_order_by(self, authenticated_session, client):
        expected = {
            'first_name': ['2345678901', '3456789012', '5678901234'],
            'gpa': ['3456789012', '2345678901', '5678901234'],
            'group_name': ['2345678901', '5678901234', '3456789012'],
            'last_name': ['2345678901', '5678901234', '3456789012'],
            'level': ['2345678901', '3456789012', '5678901234'],
            'major': ['3456789012', '2345678901', '5678901234'],
            'units': ['2345678901', '3456789012', '5678901234'],
        }
        for order_by, first_uid in expected.items():
            response = client.get(f'/api/team/FBM?orderBy={order_by}')
            assert response.status_code == 200, f'Non-200 response where order_by={order_by}'
            cohort = json.loads(response.data)
            assert cohort['totalMemberCount'] == 3, f'Wrong count where order_by={order_by}'
            sid_list = [s['sid'] for s in cohort['members']]
            assert sid_list == expected[order_by], f'Unmet expectation where order_by={order_by}'
