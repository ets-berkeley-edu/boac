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

        cohorts = response.json
        assert len(cohorts) == 2
        assert len(cohorts[0]['teamGroups']) == 2
        # Student profiles are not included in this feed.
        assert 'students' not in cohorts[0]
        assert 'totalMemberCount' in cohorts[0]
        assert len(cohorts[1]['teamGroups']) == 1

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
        assert team_groups[0]['groupCode']
        assert team_groups[0]['groupName']
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
        assert athlete['currentTerm']['enrolledUnits'] == 12.5
        assert len(athlete['currentTerm']['enrollments']) == 3
        assert athlete['currentTerm']['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(athlete['currentTerm']['enrollments'][0]['canvasSites']) == 1
        analytics = athlete['analytics']
        for metric in ['assignmentsOnTime', 'pageViews', 'participations', 'courseCurrentScore']:
            assert analytics[metric]['percentile'] > 0
            assert analytics[metric]['displayPercentile'].endswith(('rd', 'st', 'th'))

    def test_includes_cohort_member_athletics(self, authenticated_session, client):
        """includes team memberships for custom cohort members"""
        user = AuthorizedUser.find_by_uid(test_uid)
        cohort_id = user.cohort_filters[0].id
        response = client.get('/api/cohort/{}'.format(cohort_id))
        athlete = response.json['members'][0]
        assert len(athlete['athletics']) == 2
        tennis = next(membership for membership in athlete['athletics'] if membership['groupCode'] == 'WTE-AA')
        field_hockey = next(membership for membership in athlete['athletics'] if membership['groupCode'] == 'WFH-AA')
        assert tennis['groupName'] == 'Women\'s Tennis'
        assert tennis['teamCode'] == 'TNW'
        assert tennis['teamName'] == 'Women\'s Tennis'
        assert field_hockey['groupName'] == 'Women\'s Field Hockey'
        assert field_hockey['teamCode'] == 'FHW'
        assert field_hockey['teamName'] == 'Women\'s Field Hockey'

    def test_get_cohort_404(self, authenticated_session, client):
        """returns a well-formed response when no cohort found"""
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
        assert 'members' in cohort
        assert cohort['totalMemberCount'] == len(cohort['members']) == 4
        assert 'teamGroups' not in cohort

    def test_order_by_with_intensive_cohort(self, authenticated_session, client):
        """returns the canned 'intensive' cohort, available to all authenticated users"""
        all_expected_order = {
            'first_name': ['61889', '1022796', '1049291', '242881'],
            'gpa': ['1022796', '242881', '1049291', '61889'],
            'group_name': ['242881', '1049291', '61889', '1022796'],
            'last_name': ['1022796', '1049291', '242881', '61889'],
            'level': ['1022796', '242881', '1049291', '61889'],
            'major': ['1022796', '61889', '242881', '1049291'],
            'units': ['61889', '1022796', '242881', '1049291'],
        }
        for order_by, expected_uid_list in all_expected_order.items():
            response = client.get(f'/api/intensive_cohort?orderBy={order_by}')
            assert response.status_code == 200, f'Non-200 response where order_by={order_by}'
            cohort = json.loads(response.data)
            assert cohort['totalMemberCount'] == 4, f'Wrong count where order_by={order_by}'
            uid_list = [s['uid'] for s in cohort['members']]
            assert uid_list == expected_uid_list, f'Unmet expectation where order_by={order_by}'

    def test_offset_and_limit(self, authenticated_session, client):
        """returns a well-formed response with custom cohort"""
        user = AuthorizedUser.find_by_uid(test_uid)
        api_path = '/api/cohort/{}'.format(user.cohort_filters[0].id)
        # First, offset is zero
        response = client.get(api_path + '?offset={}&limit={}'.format(0, 1))
        data_0 = json.loads(response.data)
        assert data_0['totalMemberCount'] == 4
        assert len(data_0['members']) == 1
        # Now, offset is one
        response = client.get(api_path + '?offset={}&limit={}'.format(1, 1))
        data_1 = json.loads(response.data)
        assert len(data_1['members']) == 1
        # Verify that a different offset results in a different member
        assert data_0['members'][0]['uid'] != data_1['members'][0]['uid']

    def test_create_cohort(self, authenticated_session, client):
        """creates custom cohort, owned by current user"""
        label = 'Tennis'
        group_codes = ['MTE', 'WTE-AA']
        data = {
            'label': label,
            'groupCodes': group_codes,
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200

        cohort = json.loads(response.data)
        assert 'members' in cohort
        assert 'label' in cohort and cohort['label'] == label
        assert 'teamGroups' in cohort
        assert group_codes == [g['groupCode'] for g in cohort['teamGroups']]

        same_cohort = CohortFilter.find_by_id(cohort['id'])
        assert 'members' in cohort
        assert same_cohort['label'] == label
        assert 'teamGroups' in cohort and len(cohort['teamGroups']) == 2
        assert group_codes == [g['groupCode'] for g in cohort['teamGroups']]

    def test_invalid_create_cohort_params(self, authenticated_session, client):
        bad_range_syntax = 'numrange(2, BLARGH, \'[)\')'
        data = {
            'label': 'Problematic Cohort',
            'gpaRanges': [bad_range_syntax],
            'levels': ['Sophomore'],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 500 == response.status_code
        assert 'BLARGH' in str(response.data)
        assert 'does not match expected' in str(response.data)

    def test_invalid_group_code(self, authenticated_session, client):
        data = {
            'label': 'groupCodes must be uppercase',
            'groupCodes': ['mte'],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 500 == response.status_code and 'mte' in str(response.data)

    def test_invalid_level(self, authenticated_session, client):
        data = {
            'label': 'Levels must be capitalized',
            'levels': ['sophomore'],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 500 == response.status_code and 'sophomore' in str(response.data)

    def test_create_cohort_with_invalid_data_structure(self, authenticated_session, client):
        data = {
            'label': 'Majors must be a list of strings',
            'majors': [{
                'label': 'American Studies',
                'selected': True,
            }],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 500 == response.status_code

    def test_create_cohort_with_complex_filters(self, authenticated_session, client):
        """creates custom cohort, with many non-empty filter_criteria"""
        label = 'Complex'
        gpa_ranges = [
            'numrange(0, 2, \'[)\')',
            'numrange(2, 2.5, \'[)\')',
        ]
        group_codes = []
        levels = ['Junior']
        majors = ['Environmental Economics & Policy', 'Gender and Women\’s Studies']
        data = {
            'label': label,
            'gpaRanges': gpa_ranges,
            'groupCodes': group_codes,
            'levels': levels,
            'majors': majors,
            'unitRangesEligibility': [],
            'unitRangesPacing': [],
        }
        client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        response = client.get('/api/cohorts/my')
        cohort = next(x for x in response.json if x['label'] == 'Complex')
        assert cohort and 'filterCriteria' in cohort
        for key in cohort['filterCriteria']:
            assert key in data
            assert data[key] == cohort['filterCriteria'][key]

    def test_delete_cohort_not_authenticated(self, client):
        """custom cohort deletion requires authentication"""
        response = client.delete('/api/cohort/delete/{}'.format('123'))
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """custom cohort deletion is only available to owners"""
        cohort = CohortFilter.create(uid=test_uid, label='Badminton teams', group_codes=['WWP-AA', 'MWP-AA'])
        assert cohort and 'id' in cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        response = client.delete('/api/cohort/delete/{}'.format(cohort['id']))
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, authenticated_session, client):
        """deletes existing custom cohort while enforcing rules of ownership"""
        label = 'Water polo teams'
        cohort = CohortFilter.create(uid=test_uid, label=label, group_codes=['WWP-AA', 'MWP-AA'])

        assert cohort and 'id' in cohort
        id_of_created_cohort = cohort['id']

        # Verify deletion
        response = client.delete('/api/cohort/delete/{}'.format(id_of_created_cohort))
        assert response.status_code == 200
        cohorts = CohortFilter.all_owned_by(test_uid)
        assert not next((c for c in cohorts if c['id'] == id_of_created_cohort), None)
