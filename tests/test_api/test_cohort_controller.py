from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
import pytest
import simplejson as json

test_uid = '1133399'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


class TestCohortDetail:
    """Cohort API"""

    def test_my_cohorts(self, authenticated_session, client):
        response = client.get('/api/cohorts/my')
        assert response.status_code == 200

        my_cohorts = response.json
        assert len(my_cohorts) == 2
        assert len(my_cohorts[0]['teamGroups']) == 2
        assert len(my_cohorts[1]['teamGroups']) == 1

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
        response = client.get('/api/cohort/{}?orderBy=firstName'.format(cohort_id))
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
        assert cohort['code'] == 'intensive'
        assert cohort['label'] == 'Intensive'
        assert cohort['totalMemberCount'] == len(cohort['members']) == 2
        assert cohort['members'][0]['uid'] == '61889'
        assert cohort['members'][1]['uid'] == '242881'
        assert 'teamGroups' not in cohort

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
        group_codes = ['MTE-AA', 'WTE-AA']
        custom_cohort = {
            'label': label,
            'teamGroupCodes': group_codes,
        }
        response = client.post('/api/cohort/create', data=json.dumps(custom_cohort), content_type='application/json')
        assert response.status_code == 200

        cohort = json.loads(response.data)
        assert 'label' in cohort and cohort['label'] == label
        assert 'teamGroups' in cohort
        assert group_codes == [g['teamGroupCode'] for g in cohort['teamGroups']]

        same_cohort = CohortFilter.find_by_id(cohort['id'])
        assert same_cohort['label'] == label
        assert 'teamGroups' in cohort and len(cohort['teamGroups']) == 2
        assert group_codes == [g['teamGroupCode'] for g in cohort['teamGroups']]

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
