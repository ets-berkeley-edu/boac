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


from boac.models.cohort_filter import CohortFilter
import pytest
import simplejson as json

admin_uid = '2040'
asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'


@pytest.fixture()
def admin_session(fake_auth):
    fake_auth.login(admin_uid)


@pytest.fixture()
def asc_advisor(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor(fake_auth):
    fake_auth.login(coe_advisor_uid)


@pytest.fixture()
def asc_owned_cohort():
    cohorts = CohortFilter.all_owned_by(asc_advisor_uid)
    return next(c for c in cohorts if c.label == 'All sports') if len(cohorts) else None


@pytest.fixture()
def coe_owned_cohort():
    cohorts = CohortFilter.all_owned_by(coe_advisor_uid)
    return next(c for c in cohorts if c.label == 'Radioactive Women and Men') if len(cohorts) else None


class TestCohortDetail:
    """Cohort API."""

    def test_my_cohorts(self, asc_advisor, client):
        response = client.get('/api/cohorts/my')
        assert response.status_code == 200
        cohorts = response.json
        assert [cohort['label'] for cohort in cohorts] == [
            'All sports',
            'Defense Backs, Active',
            'Defense Backs, All',
            'Defense Backs, Inactive',
            'Undeclared students',
        ]
        all_sports = cohorts[0]
        assert len(all_sports['teamGroups']) == 2
        # Student profiles are not included in this feed.
        assert 'students' not in all_sports
        assert all_sports['totalStudentCount'] == 4

        defense_backs_active = cohorts[1]
        defense_backs_all = cohorts[2]
        defense_backs_inactive = cohorts[3]
        assert len(defense_backs_active['teamGroups']) == len(defense_backs_all['teamGroups']) == len(defense_backs_inactive['teamGroups']) == 1
        assert defense_backs_active['totalStudentCount'] == 2
        assert defense_backs_all['totalStudentCount'] == 3
        assert defense_backs_inactive['totalStudentCount'] == 1

    def test_create_cohort_if_first_coe_login(self, client, fake_auth):
        # COE advisor logs in for the first time
        uid = '90412'
        fake_auth.login(uid)
        cohorts = client.get('/api/cohorts/my').json
        assert len(cohorts) == 1
        cohort = cohorts[0]
        assert cohort['name'] == 'My Engineering Students'
        assert cohort['filterCriteria']['coeAdvisorUid'] == uid
        assert cohort['totalStudentCount'] == 2
        response = client.get(f"/api/cohort/{cohort['id']}")
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == 2
        assert next(s for s in students if s['name'] == 'Nora Stanton Barney')
        assert next(s for s in students if s['name'] == 'Deborah Davies')

    def test_my_cohorts_includes_students_with_alert_counts(self, create_alerts, asc_advisor, client, db_session):
        # Pre-load students into cache for consistent alert data.
        client.get('/api/user/61889/analytics')
        client.get('/api/user/98765/analytics')
        from boac.api.cache_utils import load_alerts
        load_alerts(2178)

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

    def test_cohorts_all(self, asc_advisor, client):
        """Returns all cohorts per owner."""
        response = client.get('/api/cohorts/all')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        owner = data[0]
        assert owner['uid'] == '1081940'
        assert 'firstName' in owner and 'lastName' in owner
        cohorts = owner['cohorts']
        assert len(cohorts) == 5

    def test_get_cohort(self, coe_advisor, coe_owned_cohort, client):
        """Returns a well-formed response with custom cohort."""
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['id'] == coe_owned_cohort.id
        assert cohort['label'] == coe_owned_cohort.label

    def test_unauthorized_get_cohort(self, asc_advisor, coe_owned_cohort, client):
        """Returns a well-formed response with custom cohort."""
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}')
        assert response.status_code == 404
        assert 'No cohort found' in json.loads(response.data)['message']

    def test_undeclared_major(self, asc_advisor, client):
        """Returns a well-formed response with custom cohort."""
        name = 'Undeclared students'
        cohort = next(c for c in CohortFilter.all_owned_by(asc_advisor_uid) if c.label == name)
        response = client.get(f'/api/cohort/{cohort.id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['label'] == name
        students = cohort['students']
        assert cohort['totalStudentCount'] == len(students) == 1
        # We expect the student with 'Letters & Sci Undeclared UG' major
        assert students[0]['sid'] == '5678901234'

    def test_includes_cohort_member_sis_data(self, asc_advisor, asc_owned_cohort, client):
        """Includes SIS data for custom cohort students."""
        response = client.get(f'/api/cohort/{asc_owned_cohort.id}')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['English BA', 'Nuclear Engineering BS']

    def test_includes_cohort_member_current_enrollments(self, asc_advisor, asc_owned_cohort, client):
        """Includes current-term active enrollments and analytics for custom cohort students."""
        response = client.get(f'/api/cohort/{asc_owned_cohort.id}?orderBy=firstName')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')

        term = athlete['term']
        assert term['termName'] == 'Fall 2017'
        assert term['enrolledUnits'] == 12.5
        assert len(term['enrollments']) == 4
        assert term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(term['enrollments'][0]['canvasSites']) == 1
        analytics = athlete['analytics']
        for metric in ['assignmentsSubmitted', 'currentScore', 'lastActivity']:
            assert analytics[metric]['percentile'] > 0
            assert analytics[metric]['displayPercentile'].endswith(('rd', 'st', 'th'))

    def test_includes_cohort_member_athletics_asc(self, asc_advisor, asc_owned_cohort, client):
        """Includes athletic data custom cohort members for ASC advisors."""
        response = client.get(f'/api/cohort/{asc_owned_cohort.id}')
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athletics']) == 2
        assert athlete['inIntensiveCohort'] is not None
        assert athlete['isActiveAsc'] is not None
        assert athlete['statusAsc'] is not None
        tennis = next(membership for membership in athlete['athletics'] if membership['groupCode'] == 'WTE')
        field_hockey = next(membership for membership in athlete['athletics'] if membership['groupCode'] == 'WFH')
        assert tennis['groupName'] == 'Women\'s Tennis'
        assert tennis['teamCode'] == 'TNW'
        assert tennis['teamName'] == 'Women\'s Tennis'
        assert field_hockey['groupName'] == 'Women\'s Field Hockey'
        assert field_hockey['teamCode'] == 'FHW'
        assert field_hockey['teamName'] == 'Women\'s Field Hockey'

    def test_omits_cohort_member_athletics_non_asc(self, coe_advisor, coe_owned_cohort, client):
        """Omits athletic data for non-ASC advisors."""
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}')
        secretly_an_athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert 'athletics' not in secretly_an_athlete
        assert 'inIntensiveCohort' not in secretly_an_athlete
        assert 'isActiveAsc' not in secretly_an_athlete
        assert 'statusAsc' not in secretly_an_athlete

    def test_includes_cohort_member_athletics_advisors(self, admin_session, coe_owned_cohort, client):
        """Includes athletic data for admins."""
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}')
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athletics']) == 2
        assert athlete['inIntensiveCohort'] is not None
        assert athlete['isActiveAsc'] is not None
        assert athlete['statusAsc'] is not None

    def test_get_cohort_404(self, coe_advisor, client):
        """Returns a well-formed response when no cohort found."""
        response = client.get('/api/cohort/99999999')
        assert response.status_code == 404
        assert 'No cohort found' in str(response.data)

    def test_offset_and_limit(self, asc_advisor, asc_owned_cohort, client):
        """Returns a well-formed response with custom cohort."""
        api_path = f'/api/cohort/{asc_owned_cohort.id}'
        # First, offset is zero
        response = client.get(f'{api_path}?offset={0}&limit={1}')
        data_0 = json.loads(response.data)
        assert data_0['totalStudentCount'] == 4
        assert len(data_0['students']) == 1
        # Now, offset is one
        response = client.get(f'{api_path}?offset={1}&limit={1}')
        data_1 = json.loads(response.data)
        assert len(data_1['students']) == 1
        # Verify that a different offset results in a different member
        assert data_0['students'][0]['uid'] != data_1['students'][0]['uid']

    def test_unauthorized_request_for_athletic_study_center_data(self, client, fake_auth):
        """In order to access intensive_cohort, inactive status, etc. the user must be either ASC or Admin."""
        fake_auth.login('1022796')
        data = {
            'label': 'My filtered cohort just hacked the system!',
            'isInactiveAsc': True,
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 403

    def test_create_cohort(self, coe_advisor, client):
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
        assert 'students' in cohort
        assert 'label' in cohort and cohort['label'] == label
        assert 'teamGroups' in cohort
        assert group_codes == [g['groupCode'] for g in cohort['teamGroups']]

        cohort_id = cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        same_cohort = json.loads(response.data)

        assert 'students' in cohort
        assert same_cohort['label'] == label
        assert 'teamGroups' in cohort and len(cohort['teamGroups']) == 2
        assert group_codes == [g['groupCode'] for g in cohort['teamGroups']]
        f = cohort['filterCriteria']
        assert 'majors' in f and len(f['majors']) == 2

    def test_read_only_cohort(self, client, fake_auth):
        uid = '1022796'
        fake_auth.login(uid)
        data = {
            'label': 'Students of Jane the COE Advisor',
            'coeAdvisorUid': uid,
            'groupCodes': [],
            'majors': [],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['isCannedCoeCohort'] is True
        assert cohort['isReadOnly'] is True
        assert cohort['filterCriteria']['coeAdvisorUid'] == uid
        cohort_id = cohort['id']
        response = client.delete(f'/api/cohort/delete/{cohort_id}')
        assert response.status_code == 403

    def test_forbidden_cohort_creation(self, client, fake_auth):
        uid = '1081940'
        fake_auth.login(uid)
        data = {
            'label': 'John the ASC Advisor',
            'coeAdvisorUid': uid,
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 403

    def test_invalid_create_cohort_params(self, coe_advisor, client):
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

    def test_invalid_group_code(self, coe_advisor, client):
        data = {
            'label': 'groupCodes must be uppercase',
            'groupCodes': ['mte'],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 500 == response.status_code and 'mte' in str(response.data)

    def test_invalid_level(self, coe_advisor, client):
        data = {
            'label': 'Levels must be capitalized',
            'levels': ['sophomore'],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 500 == response.status_code and 'sophomore' in str(response.data)

    def test_create_cohort_with_invalid_data_structure(self, coe_advisor, client):
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

    def test_create_cohort_with_complex_filters(self, coe_advisor, client):
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
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 200 == response.status_code
        response = client.get('/api/cohorts/my')
        assert 200 == response.status_code
        cohort = next((x for x in response.json if x['label'] == 'Complex'), None)
        assert cohort and 'filterCriteria' in cohort
        for key in cohort['filterCriteria']:
            assert data.get(key) == cohort['filterCriteria'][key]

    def test_cohort_ordering(self, coe_advisor, client):
        """Orders custom cohorts alphabetically."""
        z_team_data = {
            'label': 'Zebra Zealots',
            'groupCodes': ['MTE', 'WWP'],
        }
        client.post('/api/cohort/create', data=json.dumps(z_team_data), content_type='application/json')
        a_team_data = {
            'label': 'Aardvark Admirers',
            'groupCodes': ['MWP', 'WTE'],
        }
        client.post('/api/cohort/create', data=json.dumps(a_team_data), content_type='application/json')

        cohorts = client.get('/api/cohorts/my').json
        assert cohorts[0]['label'] == 'Aardvark Admirers'
        assert cohorts[-1]['label'] == 'Zebra Zealots'

    def test_delete_cohort_not_authenticated(self, client):
        """Custom cohort deletion requires authentication."""
        response = client.delete('/api/cohort/delete/123')
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """Custom cohort deletion is only available to owners."""
        cohort = CohortFilter.create(uid=coe_advisor_uid, label='Badminton teams', group_codes=['WWP', 'MWP'])
        assert cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        response = client.delete(f'/api/cohort/delete/{cohort.id}')
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, coe_advisor, client):
        """Deletes existing custom cohort while enforcing rules of ownership."""
        label = 'Water polo teams'
        cohort = CohortFilter.create(uid=coe_advisor_uid, label=label, group_codes=['WWP', 'MWP'])
        # Verify deletion
        response = client.delete(f'/api/cohort/delete/{cohort.id}')
        assert response.status_code == 200
        cohorts = CohortFilter.all_owned_by(coe_advisor_uid)
        assert not next((c for c in cohorts if c.id == cohort.id), None)
