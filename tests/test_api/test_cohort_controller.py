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


from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
import pytest
import simplejson as json

test_uid = '1133399'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


class TestCohortDetail:
    """Cohort API."""

    def test_my_cohorts(self, authenticated_session, client):
        response = client.get('/api/cohorts/my')
        assert response.status_code == 200
        cohorts = response.json
        assert len(cohorts) == 3
        assert len(cohorts[0]['teamGroups']) == 2
        # Student profiles are not included in this feed.
        assert 'students' not in cohorts[0]
        assert cohorts[0]['totalMemberCount'] == 4
        assert len(cohorts[1]['teamGroups']) == 1
        assert cohorts[1]['totalMemberCount'] == 2

    def test_my_cohorts_includes_students_with_alert_counts(self, create_alerts, authenticated_session, client):
        # Pre-load students into cache for consistent alert data.
        client.get('/api/user/61889/analytics')
        client.get('/api/user/98765/analytics')
        cohorts = client.get('/api/cohorts/my').json
        assert len(cohorts[0]['alerts']) == 2

        deborah = cohorts[0]['alerts'][0]
        assert deborah['sid'] == '11667051'
        assert deborah['alertCount'] == 3
        # Summary student data is included with alert counts, but full term and analytics feeds are not.
        assert deborah['cumulativeGPA'] == 3.8
        assert deborah['cumulativeUnits'] == 101.3
        assert deborah['level'] == 'Junior'
        assert len(deborah['majors']) == 2
        assert deborah['term']['enrolledUnits'] == 12.5
        assert 'analytics' not in deborah
        assert 'enrollments' not in deborah['term']

        dave_doolittle = cohorts[0]['alerts'][1]
        assert dave_doolittle['sid'] == '2345678901'
        assert dave_doolittle['uid']
        assert dave_doolittle['firstName']
        assert dave_doolittle['lastName']
        assert dave_doolittle['isActiveAsc']
        assert dave_doolittle['alertCount'] == 1

        other_alerts = cohorts[1]['alerts']
        assert len(other_alerts) == 1
        assert other_alerts[0]['sid'] == '2345678901'
        assert other_alerts[0]['alertCount'] == 1

        alert_to_dismiss = client.get('/api/alerts/current/11667051').json['shown'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        alert_to_dismiss = client.get('/api/alerts/current/2345678901').json['shown'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')

        cohorts = client.get('/api/cohorts/my').json
        assert len(cohorts[0]['alerts']) == 1
        assert cohorts[0]['alerts'][0]['sid'] == '11667051'
        assert cohorts[0]['alerts'][0]['alertCount'] == 2
        assert len(cohorts[1]['alerts']) == 0

    def test_cohorts_all(self, authenticated_session, client):
        """Returns all cohorts per owner."""
        response = client.get('/api/cohorts/all')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        oliver = data[0]
        assert oliver['uid'] == '2040'
        assert 'firstName' in oliver and 'lastName' in oliver
        cohorts = oliver['cohorts']
        assert len(cohorts) == 3
        assert [1, 3, 2] == [cohort['id'] for cohort in cohorts]

    def test_get_cohort(self, authenticated_session, client):
        """Returns a well-formed response with custom cohort."""
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
        assert cohort['totalMemberCount'] == 4
        assert cohort['totalMemberCount'] == len(cohort['members'])

    def test_undeclared_major(self, authenticated_session, client):
        """Returns a well-formed response with custom cohort."""
        user = AuthorizedUser.find_by_uid(test_uid)
        # This filter has majors='Undeclared'.
        cohort_id = user.cohort_filters[-1].id
        response = client.get('/api/cohort/{}'.format(cohort_id))
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['label'] == 'Undeclared students'
        students = cohort['members']
        assert cohort['totalMemberCount'] == len(students) == 1
        # We expect the student with 'Letters & Sci Undeclared UG' major
        assert students[0]['sid'] == '5678901234'

    def test_includes_cohort_member_sis_data(self, authenticated_session, client):
        """Includes SIS data for custom cohort members."""
        user = AuthorizedUser.find_by_uid(test_uid)
        cohort_id = user.cohort_filters[0].id
        response = client.get('/api/cohort/{}'.format(cohort_id))
        assert response.status_code == 200
        athlete = next(m for m in response.json['members'] if m['firstName'] == 'Deborah')
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['Astrophysics BS', 'English BA']

    def test_includes_cohort_member_current_enrollments(self, authenticated_session, client):
        """Includes current-term active enrollments and analytics for custom cohort members."""
        user = AuthorizedUser.find_by_uid(test_uid)
        cohort_id = user.cohort_filters[0].id
        response = client.get('/api/cohort/{}?orderBy=firstName'.format(cohort_id))
        assert response.status_code == 200
        athlete = next(m for m in response.json['members'] if m['firstName'] == 'Deborah')

        term = athlete['term']
        assert term['termName'] == 'Fall 2017'
        assert term['enrolledUnits'] == 12.5
        assert len(term['enrollments']) == 3
        assert term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(term['enrollments'][0]['canvasSites']) == 1
        analytics = athlete['analytics']
        for metric in ['assignmentsOnTime', 'pageViews', 'participations', 'courseCurrentScore']:
            assert analytics[metric]['percentile'] > 0
            assert analytics[metric]['displayPercentile'].endswith(('rd', 'st', 'th'))

    def test_includes_cohort_member_athletics(self, authenticated_session, client):
        """Includes team memberships for custom cohort members."""
        user = AuthorizedUser.find_by_uid(test_uid)
        cohort_id = user.cohort_filters[0].id
        response = client.get('/api/cohort/{}'.format(cohort_id))
        athlete = next(m for m in response.json['members'] if m['firstName'] == 'Deborah')
        assert len(athlete['athletics']) == 2
        tennis = next(membership for membership in athlete['athletics'] if membership['groupCode'] == 'WTE')
        field_hockey = next(membership for membership in athlete['athletics'] if membership['groupCode'] == 'WFH')
        assert tennis['groupName'] == 'Women\'s Tennis'
        assert tennis['teamCode'] == 'TNW'
        assert tennis['teamName'] == 'Women\'s Tennis'
        assert field_hockey['groupName'] == 'Women\'s Field Hockey'
        assert field_hockey['teamCode'] == 'FHW'
        assert field_hockey['teamName'] == 'Women\'s Field Hockey'

    def test_get_cohort_404(self, authenticated_session, client):
        """Returns a well-formed response when no cohort found."""
        response = client.get('/api/cohort/99999999')
        assert response.status_code == 404
        assert 'No cohort found' in str(response.data)

    def test_offset_and_limit(self, authenticated_session, client):
        """Returns a well-formed response with custom cohort."""
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
        """Creates custom cohort, owned by current user."""
        label = 'Tennis'
        group_codes = ['MTE', 'WTE']
        majors = ['Bioengineering BS', 'Undeclared']
        data = {
            'label': label,
            'groupCodes': group_codes,
            'majors': majors,
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
        f = cohort['filterCriteria']
        assert 'majors' in f and len(f['majors']) == 2

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
            'majors': [
                {
                    'label': 'American Studies',
                    'selected': True,
                },
            ],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 500 == response.status_code

    def test_create_cohort_with_complex_filters(self, authenticated_session, client):
        """Creates custom cohort, with many non-empty filter_criteria."""
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
            'unitRanges': [],
            'inIntensiveCohort': False,
        }
        client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        response = client.get('/api/cohorts/my')
        cohort = next(x for x in response.json if x['label'] == 'Complex')
        assert cohort and 'filterCriteria' in cohort
        for key in cohort['filterCriteria']:
            assert data.get(key) == cohort['filterCriteria'][key]

    def test_cohort_ordering(self, authenticated_session, client):
        """Orders custom cohorts alphabetically."""
        z_team_data = {
            'label': 'Zteam',
            'groupCodes': ['MTE', 'WWP'],
        }
        client.post('/api/cohort/create', data=json.dumps(z_team_data), content_type='application/json')
        a_team_data = {
            'label': 'Ateam',
            'groupCodes': ['MWP', 'WTE'],
        }
        client.post('/api/cohort/create', data=json.dumps(a_team_data), content_type='application/json')

        response = client.get('/api/cohorts/my')
        assert [cohort['label'] for cohort in response.json] == [
            'All sports',
            'Ateam',
            'Football, Defense Backs',
            'Undeclared students',
            'Zteam',
        ]

    def test_delete_cohort_not_authenticated(self, client):
        """Custom cohort deletion requires authentication."""
        response = client.delete('/api/cohort/delete/{}'.format('123'))
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """Custom cohort deletion is only available to owners."""
        cohort = CohortFilter.create(uid=test_uid, label='Badminton teams', group_codes=['WWP', 'MWP'])
        assert cohort and 'id' in cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        response = client.delete('/api/cohort/delete/{}'.format(cohort['id']))
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, authenticated_session, client):
        """Deletes existing custom cohort while enforcing rules of ownership."""
        label = 'Water polo teams'
        cohort = CohortFilter.create(uid=test_uid, label=label, group_codes=['WWP', 'MWP'])

        assert cohort and 'id' in cohort
        id_of_created_cohort = cohort['id']

        # Verify deletion
        response = client.delete('/api/cohort/delete/{}'.format(id_of_created_cohort))
        assert response.status_code == 200
        cohorts = CohortFilter.all_owned_by(test_uid)
        assert not next((c for c in cohorts if c['id'] == id_of_created_cohort), None)
