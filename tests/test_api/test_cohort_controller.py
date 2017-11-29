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

    api_path = '/api/teams'

    def test_not_authenticated(self, client):
        """returns 401 if not authenticated"""
        response = client.get(TestTeamsList.api_path)
        assert response.status_code == 401

    def test_authenticated(self, authenticated_session, client):
        """returns a well-formed response if authenticated"""
        response = client.get(TestTeamsList.api_path)
        assert response.status_code == 200
        assert len(response.json) == 24
        assert response.json[0]['code'] == 'FHW'
        assert response.json[0]['name'] == 'Field Hockey - Women'
        assert response.json[0]['totalMemberCount'] == 4


class TestCohortDetail:
    """TeamMember detail API"""

    valid_api_path = '/api/cohort/FHW'
    invalid_api_path = '/api/cohort/XYZ'

    def test_not_authenticated(self, client):
        """returns 401 if not authenticated"""
        response = client.post(TestCohortDetail.valid_api_path)
        assert response.status_code == 401

    def test_path_without_translation(self, authenticated_session, client):
        """returns code as name when no code-to-name translation exists"""
        response = client.post(TestCohortDetail.invalid_api_path)
        assert response.status_code == 200
        assert response.json['code'] == 'XYZ'
        assert response.json['name'] == 'XYZ'
        assert len(response.json['members']) == 0

    def test_valid_path(self, authenticated_session, client):
        """returns a well-formed response on a valid code if authenticated"""
        response = client.post(TestCohortDetail.valid_api_path)
        assert response.status_code == 200
        assert response.json['code'] == 'FHW'
        assert response.json['name'] == 'Field Hockey - Women'
        assert len(response.json['members']) == 4
        assert response.json['members'][0]['name'] == 'Brigitte Lin'
        assert response.json['members'][0]['uid'] == '61889'
        assert response.json['members'][0]['avatar_url'] == 'https://calspirit.berkeley.edu/oski/images/oskibio.jpg'
        assert response.json['totalMemberCount'] == len(response.json['members'])

    def test_my_cohorts(self, authenticated_session, client):
        response = client.get('/api/cohorts/my')
        assert response.status_code == 200

        my_cohorts = response.json
        assert len(my_cohorts) == 2
        assert len(my_cohorts[0]['teams']) == 2
        assert len(my_cohorts[1]['teams']) == 2

    def test_get_cohort(self, authenticated_session, client):
        """returns a well-formed response with custom cohort"""
        user = AuthorizedUser.find_by_uid(test_uid)
        cohort_id = user.cohort_filters[0].id
        response = client.post('/api/cohort/{}'.format(cohort_id))
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] > 0
        assert data['label']

        teams = data['teams']
        assert len(teams) == 2
        assert teams[0]['code']
        assert teams[0]['name']
        assert isinstance(data['members'], list)
        assert data['totalMemberCount'] == len(data['members'])

    def test_offset_and_limit(self, authenticated_session, client):
        """returns a well-formed response with custom cohort"""
        user = AuthorizedUser.find_by_uid(test_uid)
        api_path = '/api/cohort/{}'.format(user.cohort_filters[0].id)
        # First, offset is zero
        response = client.post(api_path, data=json.dumps({'offset': 0, 'limit': 1}), content_type='application/json')
        data_offset_zero = json.loads(response.data)
        assert data_offset_zero['totalMemberCount'] > 1
        assert len(data_offset_zero['members']) == 1
        # Now, offset is one
        response = client.post(api_path, data=json.dumps({'offset': 1, 'limit': 1}), content_type='application/json')
        data_offset_one = json.loads(response.data)
        assert len(data_offset_one['members']) == 1
        # Verify that a different offset results in a different member
        assert data_offset_zero['members'][0]['uid'] != data_offset_one['members'][0]['uid']

    def test_create_cohort(self, authenticated_session, client):
        """creates custom cohort, owned by current user"""
        label = 'All tennis, all the time'
        team_codes = ['TNW', 'TNM']
        custom_cohort = {
            'label': label,
            'teamCodes': team_codes,
        }
        response = client.post('/api/cohort/create', data=json.dumps(custom_cohort), content_type='application/json')
        assert response.status_code == 200

        cohort = json.loads(response.data)
        assert 'label' in cohort and cohort['label'] == label
        assert 'teams' in cohort and len(cohort['teams']) == 2
        assert cohort['teams'][0]['code'] == team_codes[0]
        assert cohort['teams'][1]['code'] == team_codes[1]

        same_cohort = CohortFilter.find_by_id(cohort['id'])
        assert same_cohort['label'] == label
        assert 'teams' in cohort and len(cohort['teams']) == 2
        assert cohort['teams'][0]['code'] == team_codes[0]
        assert cohort['teams'][1]['code'] == team_codes[1]

    def test_delete_cohort_not_authenticated(self, client):
        """custom cohort deletion requires authentication"""
        response = client.delete('/api/cohort/delete/{}'.format('123'))
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """custom cohort deletion is only available to owners"""
        cohort = CohortFilter.create(label='Badminton teams', team_codes=['MBK', 'WBK'], uid=test_uid)
        assert cohort and 'id' in cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        response = client.delete('/api/cohort/delete/{}'.format(cohort['id']))
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, authenticated_session, client):
        """deletes existing custom cohort while enforcing rules of ownership"""
        label = 'Water polo teams'
        cohort = CohortFilter.create(label=label, team_codes=['WPW', 'WPM'], uid=test_uid)

        assert cohort and 'id' in cohort
        id_of_created_cohort = cohort['id']

        # Verify deletion
        response = client.delete('/api/cohort/delete/{}'.format(id_of_created_cohort))
        assert response.status_code == 200
        cohorts = CohortFilter.all_owned_by(test_uid)
        assert not next((c for c in cohorts if c['id'] == id_of_created_cohort), None)
