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
def asc_advisor_session(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor_session(fake_auth):
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

    def test_my_cohorts(self, asc_advisor_session, client):
        response = client.get('/api/filtered_cohorts/my')
        assert response.status_code == 200
        cohorts = response.json
        assert [cohort['label'] for cohort in cohorts] == [
            'All sports',
            'Defense Backs, Active',
            'Defense Backs, All',
            'Defense Backs, Inactive',
            'Undeclared students',
        ]
        for cohort in cohorts:
            assert cohort['isOwnedByCurrentUser'] is True
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
        assert defense_backs_all['totalStudentCount'] == 2
        assert defense_backs_inactive['totalStudentCount'] == 1

    def test_my_cohorts_includes_students_with_alert_counts(self, asc_advisor_session, client, create_alerts, db_session):
        # Pre-load students into cache for consistent alert data.
        client.get('/api/student/61889/analytics')
        client.get('/api/student/98765/analytics')
        from boac.models.alert import Alert
        Alert.update_all_for_term(2178)

        cohorts = client.get('/api/filtered_cohorts/my').json
        assert len(cohorts[0]['alerts']) == 3

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

        cohorts = client.get('/api/filtered_cohorts/my').json
        assert len(cohorts[0]['alerts']) == 2
        assert cohorts[0]['alerts'][0]['sid'] == '11667051'
        assert cohorts[0]['alerts'][0]['alertCount'] == 2
        assert len(cohorts[1]['alerts']) == 0

    def test_cohorts_all(self, asc_advisor_session, client):
        """Returns all cohorts per owner."""
        response = client.get('/api/filtered_cohorts/all')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        owner = data[0]
        assert owner['uid'] == '1081940'
        assert 'firstName' in owner and 'lastName' in owner
        cohorts = owner['cohorts']
        assert len(cohorts) == 5

    def test_get_cohort(self, coe_advisor_session, client, coe_owned_cohort, create_alerts):
        """Returns a well-formed response with filtered cohort and alert count per student."""
        response = client.get(f'/api/filtered_cohort/{coe_owned_cohort.id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['id'] == coe_owned_cohort.id
        assert cohort['label'] == coe_owned_cohort.label
        assert 'students' in cohort
        assert cohort['students'][0].get('alertCount') == 3

    def test_get_cohort_without_students(self, coe_advisor_session, client, coe_owned_cohort):
        """Returns a well-formed response with cohort and no students."""
        response = client.get(f'/api/filtered_cohort/{coe_owned_cohort.id}?includeStudents=false')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'students' not in cohort

    def test_unauthorized_get_cohort(self, asc_advisor_session, client, coe_owned_cohort):
        """Returns a well-formed response with custom cohort."""
        response = client.get(f'/api/filtered_cohort/{coe_owned_cohort.id}')
        assert response.status_code == 404
        assert 'No cohort found' in json.loads(response.data)['message']

    def test_undeclared_major(self, asc_advisor_session, client):
        """Returns a well-formed response with custom cohort."""
        name = 'Undeclared students'
        cohort = next(c for c in CohortFilter.all_owned_by(asc_advisor_uid) if c.label == name)
        response = client.get(f'/api/filtered_cohort/{cohort.id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['label'] == name
        students = cohort['students']
        assert cohort['totalStudentCount'] == len(students) == 1
        # We expect the student with 'Letters & Sci Undeclared UG' major
        assert students[0]['sid'] == '5678901234'

    def test_includes_cohort_member_sis_data(self, asc_advisor_session, asc_owned_cohort, client):
        """Includes SIS data for custom cohort students."""
        response = client.get(f'/api/filtered_cohort/{asc_owned_cohort.id}')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['English BA', 'Nuclear Engineering BS']

    def test_includes_cohort_member_current_enrollments(self, asc_advisor_session, asc_owned_cohort, client):
        """Includes current-term active enrollments and analytics for custom cohort students."""
        response = client.get(f'/api/filtered_cohort/{asc_owned_cohort.id}?orderBy=firstName')
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
            assert analytics[metric]['displayPercentile'].endswith(('nd', 'rd', 'st', 'th'))

    def test_includes_cohort_member_term_gpa(self, asc_advisor_session, asc_owned_cohort, client):
        response = client.get(f'/api/filtered_cohort/{asc_owned_cohort.id}?orderBy=firstName')
        deborah = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2016', 'gpa': 3.8}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2018', 'gpa': 2.9}

    def test_includes_cohort_member_athletics_asc(self, asc_advisor_session, asc_owned_cohort, client):
        """Includes athletic data custom cohort members for ASC advisors."""
        response = client.get(f'/api/filtered_cohort/{asc_owned_cohort.id}')
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athleticsProfile']['athletics']) == 2
        assert athlete['athleticsProfile']['inIntensiveCohort'] is not None
        assert athlete['athleticsProfile']['isActiveAsc'] is not None
        assert athlete['athleticsProfile']['statusAsc'] is not None
        tennis = next(membership for membership in athlete['athleticsProfile']['athletics'] if membership['groupCode'] == 'WTE')
        field_hockey = next(membership for membership in athlete['athleticsProfile']['athletics'] if membership['groupCode'] == 'WFH')
        assert tennis['groupName'] == 'Women\'s Tennis'
        assert tennis['teamCode'] == 'TNW'
        assert tennis['teamName'] == 'Women\'s Tennis'
        assert field_hockey['groupName'] == 'Women\'s Field Hockey'
        assert field_hockey['teamCode'] == 'FHW'
        assert field_hockey['teamName'] == 'Women\'s Field Hockey'

    def test_omits_cohort_member_athletics_non_asc(self, coe_advisor_session, client, coe_owned_cohort):
        """Omits athletic data for non-ASC advisors."""
        response = client.get(f'/api/filtered_cohort/{coe_owned_cohort.id}')
        secretly_an_athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert 'athletics' not in secretly_an_athlete
        assert 'inIntensiveCohort' not in secretly_an_athlete
        assert 'isActiveAsc' not in secretly_an_athlete
        assert 'statusAsc' not in secretly_an_athlete

    def test_includes_cohort_member_athletics_advisors(self, admin_session, client, coe_owned_cohort):
        """Includes athletic data for admins."""
        response = client.get(f'/api/filtered_cohort/{coe_owned_cohort.id}')
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athleticsProfile']['athletics']) == 2
        assert athlete['athleticsProfile']['inIntensiveCohort'] is not None
        assert athlete['athleticsProfile']['isActiveAsc'] is not None
        assert athlete['athleticsProfile']['statusAsc'] is not None

    def test_get_cohort_404(self, client, coe_advisor_session):
        """Returns a well-formed response when no cohort found."""
        response = client.get('/api/filtered_cohort/99999999')
        assert response.status_code == 404
        assert 'No cohort found' in str(response.data)

    def test_offset_and_limit(self, asc_advisor_session, asc_owned_cohort, client):
        """Returns a well-formed response with custom cohort."""
        api_path = f'/api/filtered_cohort/{asc_owned_cohort.id}'
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
        response = client.post('/api/filtered_cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 403

    def test_cohort_ordering(self, client, asc_advisor_session):
        """Orders custom cohorts alphabetically."""
        z_team_data = {
            'label': 'Zebra Zealots',
            'groupCodes': ['MTE', 'WWP'],
        }
        response = client.post('/api/filtered_cohort/create', data=json.dumps(z_team_data), content_type='application/json')
        assert response.status_code == 200
        a_team_data = {
            'label': 'Aardvark Admirers',
            'groupCodes': ['MWP', 'WTE'],
        }
        response = client.post('/api/filtered_cohort/create', data=json.dumps(a_team_data), content_type='application/json')
        assert response.status_code == 200
        response = client.get('/api/filtered_cohorts/my')
        assert response.status_code == 200
        cohorts = response.json
        assert cohorts[0]['label'] == 'Aardvark Admirers'
        assert cohorts[-1]['label'] == 'Zebra Zealots'


class TestCohortCreate:
    """Cohort Create API."""

    def test_create_cohort(self, client, asc_advisor_session):
        """Creates custom cohort, owned by current user."""
        data = {
            'label': 'Tennis',
            'groupCodes': ['MTE', 'WTE'],
            'majors': [
                'Anthropology BA',
                'Bioengineering BS',
            ],
        }
        response = client.post('/api/filtered_cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200

        cohort = json.loads(response.data)
        assert 'students' in cohort
        assert 'label' in cohort and cohort['label'] == data['label']
        assert 'teamGroups' in cohort
        assert data['groupCodes'] == [g['groupCode'] for g in cohort['teamGroups']]

        cohort_id = cohort['id']
        response = client.get(f'/api/filtered_cohort/{cohort_id}')
        same_cohort = json.loads(response.data)

        assert 'students' in cohort
        assert same_cohort['label'] == data['label']
        assert 'teamGroups' in cohort and len(cohort['teamGroups']) == 2
        assert data['groupCodes'] == [g['groupCode'] for g in cohort['teamGroups']]
        f = cohort['filterCriteria']
        assert 'majors' in f and len(f['majors']) == 2

    def test_forbidden_create_of_coe_uid_cohort(self, asc_advisor_session, client, fake_auth):
        data = {
            'label': 'ASC advisor wants to see students of COE advisor',
            'advisorLdapUids': '1133399',
        }
        response = client.post('/api/filtered_cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 403

    def test_admin_create_of_coe_uid_cohort(self, admin_session, client, fake_auth):
        data = {
            'label': 'Admin wants to see students of COE advisor',
            'advisorLdapUids': '1133399',
        }
        response = client.post('/api/filtered_cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200

    def test_create_cohort_with_complex_filters(self, client, coe_advisor_session):
        """Creates custom cohort, with many non-empty filter_criteria."""
        data = {
            'label': 'Complex',
            'gpaRanges': ['numrange(0, 2, \'[)\')', 'numrange(2, 2.5, \'[)\')'],
            'levels': ['Junior'],
            'majors': [
                'Environmental Economics & Policy',
                'Gender and Women\’s Studies',
            ],
        }
        response = client.post('/api/filtered_cohort/create', data=json.dumps(data), content_type='application/json')
        assert 200 == response.status_code
        response = client.get('/api/filtered_cohorts/my')
        assert 200 == response.status_code
        cohort = next((x for x in response.json if x['label'] == data['label']), None)
        assert cohort and 'filterCriteria' in cohort
        for key in cohort['filterCriteria']:
            assert data.get(key) == cohort['filterCriteria'][key]

    def test_admin_creation_of_asc_cohort(self, client, admin_session):
        """COE advisor cannot use ASC criteria."""
        data = {'label': 'Admin superpowers', 'groupCodes': ['MTE', 'WWP']}
        response = client.post('/api/filtered_cohort/create', data=json.dumps(data), content_type='application/json')
        assert 200 == response.status_code

    def test_forbidden_cohort_creation(self, client, coe_advisor_session):
        """COE advisor cannot use ASC criteria."""
        data = {'label': 'Sorry Charlie', 'groupCodes': ['MTE', 'WWP']}
        response = client.post('/api/filtered_cohort/create', data=json.dumps(data), content_type='application/json')
        assert 403 == response.status_code


class TestCohortUpdate:
    """Cohort Update API."""

    def test_unauthorized_cohort_update(self, client, coe_advisor_session):
        cohort = CohortFilter.create(uid=asc_advisor_uid, label='Swimming, Men\'s', group_codes=['MSW', 'MSW-DV', 'MSW-SW'])
        data = {
            'id': cohort.id,
            'label': 'Hack the label!',
        }
        response = client.post('/api/filtered_cohort/update', data=json.dumps(data), content_type='application/json')
        assert 403 == response.status_code

    def test_cohort_update_name(self, client, asc_advisor_session):
        cohort = CohortFilter.create(uid=asc_advisor_uid, label='Swimming, Men\'s', group_codes=['MSW', 'MSW-DV', 'MSW-SW'])
        updated_label = 'Splashing, Men\'s'
        # First, we POST an empty label
        response = client.post('/api/filtered_cohort/update', data=json.dumps({'id': cohort.id}), content_type='application/json')
        assert 400 == response.status_code
        # Now, we POST a valid label
        data = {
            'id': cohort.id,
            'label': updated_label,
        }
        response = client.post('/api/filtered_cohort/update', data=json.dumps(data), content_type='application/json')
        assert 200 == response.status_code
        update = response.json
        assert update['label'] == updated_label

        def remove_empties(filter_criteria):
            return {k: v for k, v in filter_criteria.items() if v is not None}
        expected = remove_empties(cohort.filter_criteria)
        actual = remove_empties(update['filterCriteria'])
        assert expected == actual

    def test_cohort_update_filter_criteria(self, client, asc_advisor_session):
        label = 'Swimming, Men\'s'
        original_student_count = 4
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            label=label,
            group_codes=['MSW', 'MSW-DV', 'MSW-SW'],
            student_count=original_student_count,
        )
        assert original_student_count > 0
        updated_filter_criteria = {
            'groupCodes': ['MSW-DV', 'MSW-SW'],
        }
        data = {
            'id': cohort.id,
            'filterCriteria': updated_filter_criteria,
            'studentCount': original_student_count - 1,
        }
        response = client.post('/api/filtered_cohort/update', data=json.dumps(data), content_type='application/json')
        assert 200 == response.status_code

        updated_cohort = CohortFilter.find_by_id(int(response.json['id']))
        assert updated_cohort.label == label
        assert updated_cohort.student_count == original_student_count - 1

        def remove_empties(filter_criteria):
            return {k: v for k, v in filter_criteria.items() if v is not None}

        expected = remove_empties(cohort.filter_criteria)
        actual = remove_empties(updated_cohort.filter_criteria)
        assert expected == actual


class TestCohortDelete:
    """Cohort Delete API."""

    def test_delete_cohort_not_authenticated(self, client):
        """Custom cohort deletion requires authentication."""
        response = client.delete('/api/filtered_cohort/delete/123')
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """Custom cohort deletion is only available to owners."""
        cohort = CohortFilter.create(uid=coe_advisor_uid, label='Badminton teams', group_codes=['WWP', 'MWP'])
        assert cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        response = client.get(f'/api/filtered_cohort/{cohort.id}')
        assert response.status_code == 200
        _cohort = json.loads(response.data)
        assert _cohort['isOwnedByCurrentUser'] is False

        response = client.delete(f'/api/filtered_cohort/delete/{cohort.id}')
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, client, coe_advisor_session):
        """Deletes existing custom cohort while enforcing rules of ownership."""
        label = 'Water polo teams'
        cohort = CohortFilter.create(uid=coe_advisor_uid, label=label, group_codes=['WWP', 'MWP'])
        # Verify deletion
        response = client.delete(f'/api/filtered_cohort/delete/{cohort.id}')
        assert response.status_code == 200
        cohorts = CohortFilter.all_owned_by(coe_advisor_uid)
        assert not next((c for c in cohorts if c.id == cohort.id), None)


class TestCohortFilterDefinitions:
    """Cohort Filter Definitions API."""

    def test_coe_filter_definitions(self, client, coe_advisor_session):
        """Gets filters available to COE users."""
        response = client.get('/api/filter_cohort/definitions')
        assert response.status_code == 200
        definitions = response.json
        assert len(definitions) == 4
        assert len(definitions[0]) == 1
        assert len(definitions[1]) == 3
        assert len(definitions[2]) == 3
        assert len(definitions[3]) == 3

    def test_asc_filter_definitions(self, client, asc_advisor_session):
        """Gets filters available to ASC users."""
        response = client.get('/api/filter_cohort/definitions')
        assert response.status_code == 200
        definitions = response.json
        assert len(definitions) == 4
        assert definitions[2][0]['key'] == 'isInactiveAsc'
        assert definitions[2][1]['key'] == 'inIntensiveCohort'
        assert definitions[2][2]['key'] == 'groupCodes'

    def test_admin_filter_definitions(self, client, admin_session):
        """Gets filters available to Admin users."""
        response = client.get('/api/filter_cohort/definitions')
        assert response.status_code == 200
        definitions = response.json
        assert len(definitions) == 5
        # General
        assert definitions[0][0]['key'] == 'gpaRanges'
        assert len(definitions[0][0]['options']) == 5

        # Levels
        assert definitions[1][0]['key'] == 'levels'
        assert len(definitions[1][0]['options']) == 4
        # Units
        assert definitions[1][1]['key'] == 'unitRanges'
        assert len(definitions[1][1]['options']) == 5
        # Majors
        assert definitions[1][2]['key'] == 'majors'
        assert len(definitions[1][2]['options']) == 8

        # Ethnicity
        assert definitions[2][0]['key'] == 'ethnicities'
        assert len(definitions[2][0]['options']) == 3
        # Gender
        assert definitions[2][1]['key'] == 'genders'
        assert len(definitions[2][1]['options']) == 2
        # Underrepresented Minority
        assert definitions[2][2]['key'] == 'underrepresented'
        assert len(definitions[2][2]['options']) == 2

        # ASC Inactive
        assert definitions[3][0]['key'] == 'isInactiveAsc'
        assert len(definitions[3][0]['options']) == 2
        assert definitions[3][0]['defaultValue'] is None
        # ASC Intensive
        assert definitions[3][1]['key'] == 'inIntensiveCohort'
        assert len(definitions[3][1]['options']) == 2
        # Teams
        assert definitions[3][2]['key'] == 'groupCodes'
        assert len(definitions[3][2]['options']) == 7

        # COE PREP
        assert definitions[4][0]['key'] == 'coePrepStatuses'
        assert len(definitions[4][0]['options']) == 4
        # Last Name
        assert definitions[4][1]['key'] == 'lastNameRange'
        # COE advisors
        assert definitions[4][2]['key'] == 'advisorLdapUids'
        assert len(definitions[4][2]['options']) == 3
