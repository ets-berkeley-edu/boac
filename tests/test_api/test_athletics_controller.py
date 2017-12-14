import pytest

test_uid = '1133399'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


class TestTeams:
    """Athletics API"""

    def test_not_authenticated(self, client):
        """returns 401 if not authenticated"""
        response = client.get('/api/teams/all')
        assert response.status_code == 401

    def test_get_all_team_groups(self, authenticated_session, client):
        """returns all team-groups if authenticated"""
        response = client.get('/api/team_groups/all')
        assert response.status_code == 200
        team_groups = response.json
        group_codes = [team_group['teamGroupCode'] for team_group in team_groups]
        group_names = [team_group['teamGroupName'] for team_group in team_groups]
        total_member_counts = [team_group['totalMemberCount'] for team_group in team_groups]
        assert ['MFB-DB', 'MFB-DL', 'MTE-AA', 'WFH-AA', 'WTE-AA'] == group_codes
        assert ['Football, Defensive Backs', 'Football, Defensive Line', 'Men\'s Tennis', 'Women\'s Field Hockey',
                'Women\'s Tennis'] == group_names
        assert [2, 3, 1, 1, 1] == total_member_counts

    def test_get_all_teams(self, authenticated_session, client):
        """returns all teams if authenticated"""
        response = client.get('/api/teams/all')
        assert response.status_code == 200
        teams = response.json
        assert len(teams) == 4
        team_codes = [team['code'] for team in teams]
        team_names = [team['name'] for team in teams]
        total_member_counts = [team['totalMemberCount'] for team in teams]
        assert ['FBM', 'TNM', 'FHW', 'TNW'] == team_codes
        assert ['Football', 'Men\'s Tennis', 'Women\'s Field Hockey', 'Women\'s Tennis'] == team_names
        assert [3, 1, 1, 1] == total_member_counts
