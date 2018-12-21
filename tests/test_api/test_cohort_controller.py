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
    return next((c for c in cohorts if c.name == 'All sports'), None)


@pytest.fixture()
def coe_owned_cohort():
    cohorts = CohortFilter.all_owned_by(coe_advisor_uid)
    assert len(cohorts)
    return next((c for c in cohorts if c.name == 'Radioactive Women and Men'), None)


class TestCohortDetail:
    """Cohort API."""

    def test_my_cohorts_not_authenticated(self, client):
        """Rejects anonymous user."""
        response = client.get('/api/cohorts/my')
        assert response.status_code == 401

    def test_my_cohorts(self, coe_advisor_session, client):
        """Returns user's cohorts."""
        response = client.get('/api/cohorts/my')
        assert response.status_code == 200
        cohorts = response.json
        assert len(cohorts) == 2
        for key in 'name', 'alertCount', 'filterCriteria', 'totalStudentCount', 'isOwnedByCurrentUser':
            assert key in cohorts[0], f'Missing cohort element: {key}'

    def test_students_with_alert_counts(self, asc_advisor_session, client, create_alerts, db_session):
        # Pre-load students into cache for consistent alert data.
        client.get('/api/student/61889/analytics')
        client.get('/api/student/98765/analytics')
        from boac.models.alert import Alert
        Alert.update_all_for_term(2178)
        cohorts = CohortFilter.all_owned_by(asc_advisor_uid)
        assert len(cohorts)
        cohort_id = cohorts[0].id
        students_with_alerts = client.get(f'/api/cohort/{cohort_id}/students_with_alerts').json
        assert len(students_with_alerts) == 3

        deborah = students_with_alerts[0]
        assert deborah['sid'] == '11667051'
        assert deborah['alertCount'] == 3
        # Summary student data is included with alert counts, but full term and analytics feeds are not.
        assert deborah['cumulativeGPA'] == 3.8
        assert deborah['cumulativeUnits'] == 101.3
        assert deborah['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert deborah['level'] == 'Junior'
        assert len(deborah['majors']) == 2
        assert deborah['term']['enrolledUnits'] == 12.5
        assert deborah['termGpa'][0]['gpa'] == 2.9
        assert 'analytics' not in deborah
        assert 'enrollments' not in deborah['term']

        dave_doolittle = students_with_alerts[1]
        assert dave_doolittle['sid'] == '2345678901'
        assert dave_doolittle['uid']
        assert dave_doolittle['firstName']
        assert dave_doolittle['lastName']
        assert dave_doolittle['alertCount'] == 1

        alert_to_dismiss = client.get('/api/alerts/current/11667051').json['shown'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        alert_to_dismiss = client.get('/api/alerts/current/2345678901').json['shown'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')

        students_with_alerts = client.get(f'/api/cohort/{cohort_id}/students_with_alerts').json
        assert len(students_with_alerts) == 2
        assert students_with_alerts[0]['sid'] == '11667051'
        assert students_with_alerts[0]['alertCount'] == 2

    def test_cohorts_all(self, asc_advisor_session, client):
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

    def test_get_cohort(self, coe_advisor_session, client, coe_owned_cohort, create_alerts):
        """Returns a well-formed response with filtered cohort and alert count per student."""
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['id'] == coe_owned_cohort.id
        assert cohort['name'] == coe_owned_cohort.name
        assert 'students' in cohort
        assert cohort['students'][0].get('alertCount') == 3

    def test_get_cohort_without_students(self, coe_advisor_session, client, coe_owned_cohort):
        """Returns a well-formed response with cohort and no students."""
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}?includeStudents=false')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'students' not in cohort

    def test_unauthorized_get_cohort(self, asc_advisor_session, client, coe_owned_cohort):
        """Returns a well-formed response with custom cohort."""
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}')
        assert response.status_code == 404
        assert 'No cohort found' in json.loads(response.data)['message']

    def test_undeclared_major(self, asc_advisor_session, client):
        """Returns a well-formed response with custom cohort."""
        cohort = CohortFilter.all_owned_by(asc_advisor_uid)[-1]
        response = client.get(f'/api/cohort/{cohort.id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['name'] == 'Undeclared students'
        students = cohort['students']
        assert cohort['totalStudentCount'] == len(students) == 1
        # We expect the student with 'Letters & Sci Undeclared UG' major
        assert students[0]['sid'] == '5678901234'

    def test_includes_cohort_member_sis_data(self, asc_advisor_session, asc_owned_cohort, client):
        """Includes SIS data for custom cohort students."""
        response = client.get(f'/api/cohort/{asc_owned_cohort.id}')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['English BA', 'Nuclear Engineering BS']

    def test_includes_cohort_member_current_enrollments(self, asc_advisor_session, asc_owned_cohort, client):
        """Includes current-term active enrollments and analytics for custom cohort students."""
        response = client.get(f'/api/cohort/{asc_owned_cohort.id}?orderBy=firstName')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')

        term = athlete['term']
        assert term['termName'] == 'Fall 2017'
        assert term['enrolledUnits'] == 12.5
        assert len(term['enrollments']) == 5
        assert term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(term['enrollments'][0]['canvasSites']) == 1
        analytics = athlete['analytics']
        for metric in ['assignmentsSubmitted', 'currentScore', 'lastActivity']:
            assert analytics[metric]['percentile'] > 0
            assert analytics[metric]['displayPercentile'].endswith(('nd', 'rd', 'st', 'th'))

    def test_includes_cohort_member_term_gpa(self, asc_advisor_session, asc_owned_cohort, client):
        response = client.get(f'/api/cohort/{asc_owned_cohort.id}?orderBy=firstName')
        deborah = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}

    def test_includes_cohort_member_athletics_asc(self, asc_advisor_session, asc_owned_cohort, client):
        """Includes athletic data custom cohort members for ASC advisors."""
        response = client.get(f'/api/cohort/{asc_owned_cohort.id}')
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
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}')
        secretly_an_athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert 'athletics' not in secretly_an_athlete
        assert 'inIntensiveCohort' not in secretly_an_athlete
        assert 'isActiveAsc' not in secretly_an_athlete
        assert 'statusAsc' not in secretly_an_athlete

    def test_includes_cohort_member_athletics_advisors(self, admin_session, client, coe_owned_cohort):
        """Includes athletic data for admins."""
        response = client.get(f'/api/cohort/{coe_owned_cohort.id}')
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athleticsProfile']['athletics']) == 2
        assert athlete['athleticsProfile']['inIntensiveCohort'] is not None
        assert athlete['athleticsProfile']['isActiveAsc'] is not None
        assert athlete['athleticsProfile']['statusAsc'] is not None

    def test_get_cohort_404(self, client, coe_advisor_session):
        """Returns a well-formed response when no cohort found."""
        response = client.get('/api/cohort/99999999')
        assert response.status_code == 404
        assert 'No cohort found' in str(response.data)

    def test_offset_and_limit(self, asc_advisor_session, asc_owned_cohort, client):
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
            'name': 'My filtered cohort just hacked the system!',
            'isInactiveAsc': True,
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 403


class TestCohortCreate:
    """Cohort Create API."""

    def test_create_cohort(self, client, asc_advisor_session):
        """Creates custom cohort, owned by current user."""
        data = {
            'name': 'Tennis',
            'groupCodes': ['MTE', 'WTE'],
            'majors': [
                'Anthropology BA',
                'Bioengineering BS',
            ],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200

        cohort = json.loads(response.data)
        assert 'students' in cohort
        assert 'name' in cohort and cohort['name'] == data['name']
        assert 'teamGroups' in cohort
        assert data['groupCodes'] == [g['groupCode'] for g in cohort['teamGroups']]

        cohort_id = cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        same_cohort = json.loads(response.data)

        assert 'students' in cohort
        assert same_cohort['name'] == data['name']
        assert 'teamGroups' in cohort and len(cohort['teamGroups']) == 2
        assert data['groupCodes'] == [g['groupCode'] for g in cohort['teamGroups']]
        f = cohort['filterCriteria']
        assert 'majors' in f and len(f['majors']) == 2

    def test_forbidden_create_of_coe_uid_cohort(self, asc_advisor_session, client, fake_auth):
        data = {
            'name': 'ASC advisor wants to see students of COE advisor',
            'advisorLdapUids': '1133399',
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 403

    def test_admin_create_of_coe_uid_cohort(self, admin_session, client, fake_auth):
        data = {
            'name': 'Admin wants to see students of COE advisor',
            'advisorLdapUids': '1133399',
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200

    def test_create_cohort_with_complex_filters(self, client, coe_advisor_session):
        """Creates custom cohort, with many non-empty filter_criteria."""
        data = {
            'name': 'Complex',
            'gpaRanges': ['numrange(0, 2, \'[)\')', 'numrange(2, 2.5, \'[)\')'],
            'levels': ['Junior'],
            'majors': [
                'Environmental Economics & Policy',
                'Gender and Women\’s Studies',
            ],
        }
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 200 == response.status_code
        cohort_id = response.json['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert 200 == response.status_code
        cohort = response.json
        assert cohort and 'filterCriteria' in cohort
        for key in cohort['filterCriteria']:
            assert data.get(key) == cohort['filterCriteria'][key]

    def test_admin_creation_of_asc_cohort(self, client, admin_session):
        """COE advisor cannot use ASC criteria."""
        data = {'name': 'Admin superpowers', 'groupCodes': ['MTE', 'WWP']}
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 200 == response.status_code

    def test_forbidden_cohort_creation(self, client, coe_advisor_session):
        """COE advisor cannot use ASC criteria."""
        data = {'name': 'Sorry Charlie', 'groupCodes': ['MTE', 'WWP']}
        response = client.post('/api/cohort/create', data=json.dumps(data), content_type='application/json')
        assert 403 == response.status_code


class TestCohortUpdate:
    """Cohort Update API."""

    def test_unauthorized_cohort_update(self, client, coe_advisor_session):
        cohort = CohortFilter.create(uid=asc_advisor_uid, name='Swimming, Men\'s', group_codes=['MSW', 'MSW-DV', 'MSW-SW'])
        data = {
            'id': cohort.id,
            'name': 'Hack the name!',
        }
        response = client.post('/api/cohort/update', data=json.dumps(data), content_type='application/json')
        assert 403 == response.status_code

    def test_cohort_update_name(self, client, asc_advisor_session):
        cohort = CohortFilter.create(uid=asc_advisor_uid, name='Swimming, Men\'s', group_codes=['MSW', 'MSW-DV', 'MSW-SW'])
        updated_name = 'Splashing, Men\'s'
        # First, we POST an empty name
        response = client.post('/api/cohort/update', data=json.dumps({'id': cohort.id}), content_type='application/json')
        assert 400 == response.status_code
        # Now, we POST a valid name
        data = {
            'id': cohort.id,
            'name': updated_name,
        }
        response = client.post('/api/cohort/update', data=json.dumps(data), content_type='application/json')
        assert 200 == response.status_code
        update = response.json
        assert update['name'] == updated_name

        def remove_empties(filter_criteria):
            return {k: v for k, v in filter_criteria.items() if v is not None}
        expected = remove_empties(cohort.filter_criteria)
        actual = remove_empties(update['filterCriteria'])
        assert expected == actual

    def test_cohort_update_filter_criteria(self, client, asc_advisor_session):
        name = 'Swimming, Men\'s'
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name=name,
            group_codes=['MBB'],
        )
        response = client.get(f'/api/cohort/{cohort.id}')
        cohort = json.loads(response.data)
        assert cohort['totalStudentCount'] == 1
        # Update the db
        cohort_id = cohort['id']
        updates = {
            'id': cohort_id,
            'filterCriteria': {
                'groupCodes': ['MBB', 'MBB-AA'],
            },
            'studentCount': 3,
        }
        response = client.post('/api/cohort/update', data=json.dumps(updates), content_type='application/json')
        assert response.status_code == 200
        # Verify the value of 'student_count' in db
        updated_cohort = CohortFilter.find_by_id(cohort_id)
        assert updated_cohort.student_count == updates['studentCount']
        assert updated_cohort.filter_criteria['groupCodes'] == updates['filterCriteria']['groupCodes']


class TestCohortDelete:
    """Cohort Delete API."""

    def test_delete_cohort_not_authenticated(self, client):
        """Custom cohort deletion requires authentication."""
        response = client.delete('/api/cohort/delete/123')
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """Custom cohort deletion is only available to owners."""
        cohort = CohortFilter.create(uid=coe_advisor_uid, name='Badminton teams', group_codes=['WWP', 'MWP'])
        assert cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        response = client.get(f'/api/cohort/{cohort.id}')
        assert response.status_code == 200
        _cohort = json.loads(response.data)
        assert _cohort['isOwnedByCurrentUser'] is False

        response = client.delete(f'/api/cohort/delete/{cohort.id}')
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, client, coe_advisor_session):
        """Deletes existing custom cohort while enforcing rules of ownership."""
        name = 'Water polo teams'
        cohort = CohortFilter.create(uid=coe_advisor_uid, name=name, group_codes=['WWP', 'MWP'])
        # Verify deletion
        response = client.delete(f'/api/cohort/delete/{cohort.id}')
        assert response.status_code == 200
        cohorts = CohortFilter.all_owned_by(asc_advisor_uid)
        assert not next((c for c in cohorts if c.id == cohort.id), None)


class TestCohortFilterDefinitions:
    """Cohort Filter Definitions API."""

    def test_coe_filter_definitions(self, client, coe_advisor_session):
        """Gets filters available to COE users."""
        response = client.get('/api/cohort/filter_definitions')
        assert response.status_code == 200
        definitions = response.json
        assert len(definitions) == 4
        assert len(definitions[0]) == 1
        assert len(definitions[1]) == 3
        assert len(definitions[2]) == 3
        assert len(definitions[3]) == 5

    def test_asc_filter_definitions(self, client, asc_advisor_session):
        """Gets filters available to ASC users."""
        response = client.get('/api/cohort/filter_definitions')
        assert response.status_code == 200
        definitions = response.json
        assert len(definitions) == 4
        assert definitions[2][0]['key'] == 'isInactiveAsc'
        assert definitions[2][1]['key'] == 'inIntensiveCohort'
        assert definitions[2][2]['key'] == 'groupCodes'

    def test_admin_filter_definitions(self, client, admin_session):
        """Gets filters available to Admin users."""
        response = client.get('/api/cohort/filter_definitions')
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

        # COE inactive
        assert definitions[4][0]['key'] == 'isInactiveCoe'
        # COE PREP
        assert definitions[4][1]['key'] == 'coePrepStatuses'
        assert len(definitions[4][1]['options']) == 4
        # COE-provided probation status
        assert definitions[4][2]['key'] == 'coeProbation'
        assert definitions[4][2]['defaultValue'] is None
        # Last Name
        assert definitions[4][3]['key'] == 'lastNameRange'
        # COE advisors
        assert definitions[4][4]['key'] == 'advisorLdapUids'
        assert len(definitions[4][4]['options']) == 3


class TestCohortTranslations:
    """Cohort Translation API."""

    def test_translate_criteria_when_empty(self, client, coe_advisor_session):
        """Empty filterCriteria translates to zero rows."""
        response = client.post(
            '/api/cohort/translate_filter_criteria',
            data=json.dumps({'filterCriteria': {}}),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.data) == []

    def test_translate_criteria_with_boolean(self, client, coe_advisor_session):
        """Filter-criteria with boolean is properly translated."""
        key = 'isInactiveCoe'
        response = client.post(
            '/api/cohort/translate_filter_criteria',
            data=json.dumps({'filterCriteria': {key: False}}),
            content_type='application/json',
        )
        assert response.status_code == 200
        rows = json.loads(response.data)
        assert len(rows) == 1
        row = rows[0]
        assert row['name'] == 'Inactive'
        assert row['key'] == key
        assert row['value'] is False
        assert 'subcategoryHeader' not in row

    def test_translate_criteria_with_array(self, client, coe_advisor_session):
        """Filter-criteria with array is properly translated."""
        key = 'levels'
        selected_options = ['Freshman', 'Sophomore']
        response = client.post(
            '/api/cohort/translate_filter_criteria',
            data=json.dumps({'filterCriteria': {key: selected_options}}),
            content_type='application/json',
        )
        assert response.status_code == 200
        rows = json.loads(response.data)
        assert len(rows) == 2
        assert rows[0]['name'] == rows[1]['name'] == 'Level'
        assert rows[0]['key'] == rows[1]['key'] == key
        assert rows[0]['subcategoryHeader'] == 'Freshman'
        assert rows[1]['subcategoryHeader'] == 'Sophomore'

        def selected_option_matches(row, value):
            option = next((o for o in row.get('options', []) if o.get('selected') is True), None)
            return option and option['value'] == value
        assert selected_option_matches(rows[0], 'Freshman') is True
        assert selected_option_matches(rows[1], 'Sophomore') is True

    def test_translate_criteria_with_range(self, client, coe_advisor_session):
        """Filter-criteria with range is properly translated."""
        key = 'lastNameRange'
        selected_options = ['M', 'Z']
        response = client.post(
            '/api/cohort/translate_filter_criteria',
            data=json.dumps({'filterCriteria': {key: selected_options}}),
            content_type='application/json',
        )
        assert response.status_code == 200
        rows = json.loads(response.data)
        assert len(rows) == 1
        row = rows[0]
        assert row['name'] == 'Last Name'
        assert row['key'] == key
        assert row['value'] == selected_options
        assert row['subcategoryHeader'] == 'Initials M through Z'
