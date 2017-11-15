from boac.models import authorized_user
from boac.models.authorized_user import CohortFilter
from flask_login import current_user
import pytest
import simplejson as json

test_uid = '1133399'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


class TestTeamsList:
    """Cohorts list API"""

    api_path = '/api/teams'

    def test_not_authenticated(self, client, fixture_team_members):
        """returns 401 if not authenticated"""
        response = client.get(TestTeamsList.api_path)
        assert response.status_code == 401

    def test_authenticated(self, authenticated_session, client, fixture_team_members):
        """returns a well-formed response if authenticated"""
        response = client.get(TestTeamsList.api_path)
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['code'] == 'FHW'
        assert response.json[0]['name'] == 'Field Hockey - Women'
        assert response.json[0]['memberCount'] == 1


class TestCohortDetail:
    """TeamMember detail API"""

    valid_api_path = '/api/cohort/FHW'
    invalid_api_path = '/api/cohort/XYZ'

    def test_not_authenticated(self, client, fixture_team_members):
        """returns 401 if not authenticated"""
        response = client.get(TestCohortDetail.valid_api_path)
        assert response.status_code == 401

    def test_path_without_translation(self, authenticated_session, client, fixture_team_members):
        """returns code as name when no code-to-name translation exists"""
        response = client.get(TestCohortDetail.invalid_api_path)
        assert response.status_code == 200
        assert response.json['code'] == 'XYZ'
        assert response.json['name'] == 'XYZ'
        assert len(response.json['members']) == 0

    def test_valid_path(self, authenticated_session, client, fixture_team_members):
        """returns a well-formed response on a valid code if authenticated"""
        response = client.get(TestCohortDetail.valid_api_path)
        assert response.status_code == 200
        assert response.json['code'] == 'FHW'
        assert response.json['name'] == 'Field Hockey - Women'
        assert len(response.json['members']) == 1
        assert response.json['members'][0]['name'] == 'Brigitte Lin'
        assert response.json['members'][0]['uid'] == '61889'
        assert response.json['members'][0]['avatar_url'] == 'https://calspirit.berkeley.edu/oski/images/oskibio.jpg'

    def test_get_cohort(self, authenticated_session, client, fixture_team_members):
        """returns a well-formed response with custom cohort"""
        user = authorized_user.load_user(test_uid)
        cohort_filter_id = user.cohort_filters[0].id
        response = client.get('/api/cohort/{}'.format(cohort_filter_id))
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] > 0
        assert data['label'] == 'Men and women\'s soccer'

        teams = data['teams']
        assert len(teams) == 2
        assert teams[0]['code'] == 'SCW'
        assert teams[0]['name'] == 'Soccer - Women'
        assert isinstance(data['members'], list)

    def test_create_cohort_filter(self, authenticated_session, client, fixture_team_members):
        """creates custom cohort, owned by current user"""
        custom_cohort = {
            'label': 'All tennis, all the time',
            'team_codes': ['TNW', 'TNM'],
        }
        response = client.post('/api/cohort/create', data=json.dumps(custom_cohort), content_type='application/json')
        assert response.status_code == 200

    def test_delete_cohort_not_authenticated(self, client):
        """custom cohort deletion requires authentication"""
        response = client.delete('/api/cohort/delete/{}'.format('123'))
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """custom cohort deletion is only available to owners"""
        cohort_filter = CohortFilter.create(label='Badminton teams', team_codes=['MBK', 'WBK'])
        authorized_user.create_cohort_filter(cohort_filter, test_uid)
        # This user does not own the custom cohort above
        fake_auth.login('2040')
        response = client.delete('/api/cohort/delete/{}'.format(current_user.uid))
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, authenticated_session, client):
        """deletes existing custom cohort while enforcing rules of ownership"""
        label = 'Water polo teams'
        cohort_filter = CohortFilter.create(label=label, team_codes=['WPW', 'WPM'])
        authorized_user.create_cohort_filter(cohort_filter, test_uid)
        # Verify creation
        cohort_filter = find_cohort_filter_owned_by(test_uid, label)
        assert cohort_filter
        # Verify deletion
        response = client.delete('/api/cohort/delete/{}'.format(cohort_filter.id))
        assert response.status_code == 200
        assert not find_cohort_filter_owned_by(test_uid, label)


def find_cohort_filter_owned_by(uid, label):
    cohorts = authorized_user.load_cohorts_owned_by(uid)
    return next((cohort for cohort in cohorts if cohort.label == label), None)
