from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
import pytest
import simplejson as json

test_uid = '1133399'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


class TestTeamsList:
    """Cohorts list API"""

    api_path = '/api/teams/all'

    def test_not_authenticated(self, client):
        """returns 401 if not authenticated"""
        response = client.get(TestTeamsList.api_path)
        assert response.status_code == 401

    def test_authenticated(self, authenticated_session, client):
        """returns a well-formed response if authenticated"""
        response = client.get(TestTeamsList.api_path)
        assert response.status_code == 200
        teams = response.json
        assert len(teams) == 4
        assert teams[0]['code'] == 'FHW'
        assert teams[0]['name'] == 'Field Hockey - Women'
        assert teams[0]['totalMemberCount'] == 1
        assert teams[1]['totalMemberCount'] == 5


class TestCohortDetail:
    """TeamMember detail API"""

    valid_api_path = '/api/team/FHW'
    invalid_api_path = '/api/team/XYZ'

    def test_not_authenticated(self, client):
        """returns 401 if not authenticated"""
        response = client.get(TestCohortDetail.valid_api_path)
        assert response.status_code == 401

    def test_path_without_translation(self, authenticated_session, client):
        """returns code as name when no code-to-name translation exists"""
        response = client.get(TestCohortDetail.invalid_api_path)
        assert response.status_code == 404
        assert 'code' not in response.json
        assert 'No team found' in json.loads(response.data)['message']

    def test_valid_path(self, authenticated_session, client):
        """returns a well-formed response on a valid code if authenticated"""
        response = client.get(TestCohortDetail.valid_api_path)
        assert response.status_code == 200
        team = response.json
        assert team['code'] == 'FHW'
        assert team['name'] == 'Field Hockey - Women'
        members = team['members']
        assert team['totalMemberCount'] == len(members) == 1
        assert members[0]['name'] == 'Brigitte Lin'
        assert members[0]['uid'] == '61889'
        assert members[0]['avatar_url'] == 'https://calspirit.berkeley.edu/oski/images/oskibio.jpg'

    def test_includes_team_member_sis_data(self, authenticated_session, client):
        """includes SIS data for team members"""
        response = client.get(TestCohortDetail.valid_api_path)
        field_hockey_star = response.json['members'][0]
        assert field_hockey_star['cumulativeGPA'] == 3.8
        assert field_hockey_star['cumulativeUnits'] == 101.3
        assert field_hockey_star['level'] == 'Junior'
        assert field_hockey_star['majors'] == ['English BA', 'Astrophysics BS']

    def test_includes_team_member_current_enrollments(self, authenticated_session, client):
        """includes current-term active enrollments and analytics for team members"""
        response = client.get(TestCohortDetail.valid_api_path)
        field_hockey_star = response.json['members'][0]
        assert field_hockey_star['currentTerm']['termName'] == 'Fall 2017'
        assert field_hockey_star['currentTerm']['enrolledUnits'] == 7.5
        assert len(field_hockey_star['currentTerm']['enrollments']) == 2
        assert field_hockey_star['currentTerm']['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(field_hockey_star['currentTerm']['enrollments'][0]['canvasSites']) == 1

    def test_my_cohorts(self, authenticated_session, client):
        response = client.get('/api/cohorts/my')
        assert response.status_code == 200

        my_cohorts = response.json
        assert len(my_cohorts) == 2
        assert len(my_cohorts[0]['teamGroups']) == 2
        assert len(my_cohorts[1]['teamGroups']) == 1

    def test_get_all_team_groups(self, authenticated_session, client):
        response = client.get('/api/team_groups/all')
        assert response.status_code == 200
        team_groups = response.json
        assert 5 == len(team_groups)
        team_group_codes = [team_group['teamGroupCode'] for team_group in team_groups]
        assert ['MFB-DB', 'MFB-DL', 'MTE-AA', 'WFH-AA', 'WTE-AA'] == team_group_codes

    def test_team_groups_members(self, authenticated_session, client):
        response = client.get('/api/team_groups/members?teamGroupCodes=MFB-DB&teamGroupCodes=MFB-DL')
        assert response.status_code == 200
        assert 'members' in response.json
        member_uid_list = [member['uid'] for member in response.json['members']]
        assert ['2040', '242881', '1133399'] == member_uid_list

    def test_get_cohort(self, authenticated_session, client):
        """returns a well-formed response with custom cohort"""
        user = AuthorizedUser.find_by_uid(test_uid)
        cohort_id = user.cohort_filters[0].id
        response = client.get('/api/cohort/{}'.format(cohort_id))
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['id'] > 0
        assert cohort['label']

        team_groups = cohort['teamGroups']
        assert len(team_groups) == 2
        assert team_groups[0]['teamGroupCode']
        assert team_groups[0]['teamGroupName']
        assert isinstance(cohort['members'], list)
        assert cohort['totalMemberCount'] == len(cohort['members'])

    def test_includes_cohort_member_sis_data(self, authenticated_session, client):
        """includes SIS data for custom cohort members"""
        user = AuthorizedUser.find_by_uid(test_uid)
        cohort_id = user.cohort_filters[0].id
        response = client.get('/api/cohort/{}'.format(cohort_id))
        assert response.status_code == 200
        athlete = response.json['members'][0]
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['English BA', 'Astrophysics BS']

    def test_includes_cohort_member_current_enrollments(self, authenticated_session, client):
        """includes current-term active enrollments and analytics for custom cohort members"""
        user = AuthorizedUser.find_by_uid(test_uid)
        cohort_id = user.cohort_filters[0].id
        response = client.get('/api/cohort/{}'.format(cohort_id))
        assert response.status_code == 200
        athlete = response.json['members'][0]
        assert athlete['currentTerm']['termName'] == 'Fall 2017'
        assert athlete['currentTerm']['enrolledUnits'] == 7.5
        assert len(athlete['currentTerm']['enrollments']) == 2
        assert athlete['currentTerm']['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(athlete['currentTerm']['enrollments'][0]['canvasSites']) == 1

    def test_get_cohort_404(self, authenticated_session, client):
        """returns a canned cohort, available to all authenticated users"""
        response = client.get('/api/cohort/99999999')
        assert response.status_code == 404
        assert 'No cohort found' in str(response.data)

    def test_get_intensive_cohort(self, authenticated_session, client):
        """returns the canned 'intensive' cohort, available to all authenticated users"""
        response = client.get('/api/intensive_cohort')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['id'] == 'intensive'
        assert cohort['label'] == 'Intensive'
        assert cohort['totalMemberCount'] == len(cohort['members']) == 2
        assert cohort['members'][0]['uid'] == '61889'
        assert cohort['members'][1]['uid'] == '242881'
        assert cohort['teamGroups'][0]['teamGroupCode'] == 'MFB-DL'
        assert cohort['teamGroups'][1]['teamGroupCode'] == 'WFH-AA'
        assert cohort['teamGroups'][2]['teamGroupCode'] == 'WTE-AA'

    def test_offset_and_limit(self, authenticated_session, client):
        """returns a well-formed response with custom cohort"""
        user = AuthorizedUser.find_by_uid(test_uid)
        api_path = '/api/cohort/{}'.format(user.cohort_filters[0].id)
        # First, offset is zero
        response = client.get(api_path + '?offset={}&limit={}'.format(0, 1))
        data_offset_zero = json.loads(response.data)
        assert data_offset_zero['totalMemberCount'] == 4
        assert len(data_offset_zero['members']) == 1
        # Now, offset is one
        response = client.get(api_path + '?offset={}&limit={}'.format(1, 1))
        data_offset_one = json.loads(response.data)
        assert len(data_offset_one['members']) == 1
        # Verify that a different offset results in a different member
        assert data_offset_zero['members'][0]['uid'] != data_offset_one['members'][0]['uid']

    def test_create_cohort(self, authenticated_session, client):
        """creates custom cohort, owned by current user"""
        label = 'Tennis'
        team_group_codes = ['WTE-AA', 'MTE-AA']
        custom_cohort = {
            'label': label,
            'teamGroupCodes': team_group_codes,
        }
        response = client.post('/api/cohort/create', data=json.dumps(custom_cohort), content_type='application/json')
        assert response.status_code == 200

        cohort = json.loads(response.data)
        assert 'label' in cohort and cohort['label'] == label
        assert 'teamGroups' in cohort and len(cohort['teamGroups']) == 2
        assert cohort['teamGroups'][0]['teamGroupCode'] in team_group_codes
        assert cohort['teamGroups'][1]['teamGroupCode'] in team_group_codes

        same_cohort = CohortFilter.find_by_id(cohort['id'])
        assert same_cohort['label'] == label
        assert 'teamGroups' in cohort and len(cohort['teamGroups']) == 2
        assert cohort['teamGroups'][0]['teamGroupCode'] in team_group_codes
        assert cohort['teamGroups'][1]['teamGroupCode'] in team_group_codes

    def test_delete_cohort_not_authenticated(self, client):
        """custom cohort deletion requires authentication"""
        response = client.delete('/api/cohort/delete/{}'.format('123'))
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """custom cohort deletion is only available to owners"""
        cohort = CohortFilter.create(label='Badminton teams', team_group_codes=['MBK', 'WBK'], uid=test_uid)
        assert cohort and 'id' in cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        response = client.delete('/api/cohort/delete/{}'.format(cohort['id']))
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, authenticated_session, client):
        """deletes existing custom cohort while enforcing rules of ownership"""
        label = 'Water polo teams'
        cohort = CohortFilter.create(label=label, team_group_codes=['WPW', 'WPM'], uid=test_uid)

        assert cohort and 'id' in cohort
        id_of_created_cohort = cohort['id']

        # Verify deletion
        response = client.delete('/api/cohort/delete/{}'.format(id_of_created_cohort))
        assert response.status_code == 200
        cohorts = CohortFilter.all_owned_by(test_uid)
        assert not next((c for c in cohorts if c['id'] == id_of_created_cohort), None)
