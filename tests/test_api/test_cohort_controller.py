"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac import std_commit
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from flask import current_app as app
import pytest
import simplejson as json
from tests.test_api.api_test_utils import all_cohorts_owned_by, api_cohort_create, api_cohort_events, api_cohort_get, \
    api_curated_group_add_students, api_curated_group_remove_student
from tests.util import override_config

asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'
coe_scheduler_uid = '6972201'
asc_and_coe_advisor_uid = '90412'
ce3_advisor_uid = '2525'


@pytest.fixture()
def admin_login(admin_user_uid, fake_auth):
    fake_auth.login(admin_user_uid)


@pytest.fixture()
def asc_advisor_login(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor_login(fake_auth):
    fake_auth.login(coe_advisor_uid)


@pytest.fixture()
def admin_owned_cohort(admin_user_uid):
    cohorts = all_cohorts_owned_by(admin_user_uid)
    return cohorts[0]


@pytest.fixture()
def asc_owned_cohort():
    cohorts = all_cohorts_owned_by(asc_advisor_uid)
    return next((c for c in cohorts if c['name'] == 'All sports'), None)


@pytest.fixture()
def coe_owned_cohort():
    cohorts = all_cohorts_owned_by(coe_advisor_uid)
    return next((c for c in cohorts if c['name'] == 'Radioactive Women and Men'), None)


class TestCohortById:

    def test_students_with_alert_counts(self, asc_advisor_login, client, create_alerts, db_session):
        """Pre-load students into cache for consistent alert data."""
        from boac.models.alert import Alert

        assert client.get('/api/student/by_uid/61889').status_code == 200
        assert client.get('/api/student/by_uid/98765').status_code == 200

        Alert.update_all_for_term(2178)
        cohorts = all_cohorts_owned_by(asc_advisor_uid)
        assert len(cohorts)
        cohort_id = cohorts[0]['id']
        response = client.get(f'/api/cohort/{cohort_id}/students_with_alerts')
        assert response.status_code == 200
        students_with_alerts = response.json
        assert len(students_with_alerts) == 3

        deborah = students_with_alerts[0]
        assert deborah['sid'] == '11667051'
        assert deborah['alertCount'] == 4
        # Summary student data is included with alert counts, but full term feeds are not.
        assert deborah['academicStanding']['status'] == 'GST'
        assert deborah['cumulativeGPA'] == 3.8
        assert deborah['cumulativeUnits'] == 101.3
        assert deborah['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert deborah['level'] == 'Junior'
        assert len(deborah['majors']) == 2
        assert deborah['term']['enrolledUnits'] == 12.5
        assert deborah['termGpa'][0]['gpa'] == 2.9
        assert 'enrollments' not in deborah['term']

        dave_doolittle = students_with_alerts[1]
        assert dave_doolittle['sid'] == '2345678901'
        assert dave_doolittle['uid']
        assert dave_doolittle['firstName']
        assert dave_doolittle['lastName']
        assert dave_doolittle['alertCount'] == 1

        def _get_alerts(uid):
            _response = client.get(f'/api/student/by_uid/{uid}')
            assert _response.status_code == 200
            return _response.json['notifications']['alert']

        alert_to_dismiss = _get_alerts(61889)[0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        alert_to_dismiss = _get_alerts(98765)[0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')

        students_with_alerts = client.get(f'/api/cohort/{cohort_id}/students_with_alerts').json
        assert len(students_with_alerts) == 2
        assert students_with_alerts[0]['sid'] == '11667051'
        assert students_with_alerts[0]['alertCount'] == 3

    def test_get_cohort(self, coe_advisor_login, client, coe_owned_cohort, create_alerts):
        """Returns a well-formed response with filtered cohort and alert count per student."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['id'] == cohort_id
        assert cohort['name'] == coe_owned_cohort['name']
        assert 'students' in cohort
        assert cohort['students'][0].get('alertCount') == 4

    def test_get_cohort_without_students(self, coe_advisor_login, client, coe_owned_cohort):
        """Returns a well-formed response with cohort and no students."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}?includeStudents=false')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'students' not in cohort

    def test_unauthorized_get_cohort(self, asc_advisor_login, client, coe_owned_cohort):
        """Returns a well-formed response with custom cohort."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 404
        assert 'No cohort found' in json.loads(response.data)['message']

    def test_advisor_cannot_see_admin_cohort(self, asc_advisor_login, client, admin_owned_cohort):
        cohort_id = admin_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 404
        assert 'No cohort found' in json.loads(response.data)['message']

    def test_undeclared_major(self, asc_advisor_login, client, app):
        """Returns a well-formed response with custom cohort."""
        cohort = all_cohorts_owned_by(asc_advisor_uid)[-1]
        cohort_id = cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert cohort['name'] == 'Undeclared students'
        students = cohort['students']
        assert cohort['totalStudentCount'] == len(students) == 1
        # We expect the student with 'Letters & Sci Undeclared UG' major
        assert students[0]['sid'] == '5678901234'

    def test_includes_cohort_member_sis_data(self, asc_advisor_login, asc_owned_cohort, client):
        """Includes SIS data for custom cohort students."""
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['English BA', 'Nuclear Engineering BS']

    def test_includes_cohort_member_current_enrollments(self, asc_advisor_login, asc_owned_cohort, client):
        """Includes current-term active enrollments for custom cohort students."""
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}?orderBy=firstName')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        term = athlete['term']
        assert term['termName'] == 'Fall 2017'
        assert term['enrolledUnits'] == 12.5
        assert len(term['enrollments']) == 5
        assert term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(term['enrollments'][0]['canvasSites']) == 1

    def test_includes_cohort_member_non_current_enrollments(self, asc_advisor_login, asc_owned_cohort, client):
        """Includes active enrollments for a non-current term if requested."""
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}?orderBy=firstName&termId=2172')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        term = athlete['term']
        assert term['termName'] == 'Spring 2017'
        assert term['enrolledUnits'] == 10.0
        assert len(term['enrollments']) == 3
        assert term['enrollments'][0]['displayName'] == 'CLASSIC 130 LEC 001'
        assert term['enrollments'][0]['grade'] == 'P'

    def test_includes_canvas_data(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        student_feed = _new_undeclared_cohort(client)['students'][0]
        assert 'analytics' in student_feed['term']['enrollments'][0]['canvasSites'][0]

    def test_no_canvas_access_suppresses_canvas_data(self, user_factory, client, fake_auth):
        advisor = user_factory(can_access_canvas_data=False, dept_codes=['ZZZZZ'])
        fake_auth.login(advisor.uid)
        student_feed = _new_undeclared_cohort(client)['students'][0]
        assert student_feed['term']['enrollments'][0]['canvasSites'] == []

    def test_includes_cohort_member_term_gpa(self, asc_advisor_login, asc_owned_cohort, client):
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}?orderBy=firstName')
        assert response.status_code == 200
        deborah = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}

    def test_includes_cohort_member_academic_standing(self, asc_advisor_login, asc_owned_cohort, client):
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}?orderBy=firstName')
        assert response.status_code == 200
        deborah = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert deborah['academicStanding'] == {
            'actionDate': '2018-05-31',
            'status': 'GST',
            'termName': 'Spring 2018',
        }

    def test_includes_cohort_member_athletics_asc(self, asc_advisor_login, asc_owned_cohort, client):
        """Includes athletic data custom cohort members for ASC advisors."""
        cohort_id = asc_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
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

    def test_omits_cohort_member_athletics_non_asc(self, coe_advisor_login, client, coe_owned_cohort):
        """Omits athletic data for non-ASC advisors."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        secretly_an_athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert 'athletics' not in secretly_an_athlete
        assert 'inIntensiveCohort' not in secretly_an_athlete
        assert 'isActiveAsc' not in secretly_an_athlete
        assert 'statusAsc' not in secretly_an_athlete

    def test_includes_cohort_member_athletics_advisors(self, admin_login, client, coe_owned_cohort):
        """Includes athletic data for admins."""
        cohort_id = coe_owned_cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        athlete = next(m for m in response.json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athleticsProfile']['athletics']) == 2
        assert athlete['athleticsProfile']['inIntensiveCohort'] is not None
        assert athlete['athleticsProfile']['isActiveAsc'] is not None
        assert athlete['athleticsProfile']['statusAsc'] is not None

    def test_get_cohort_404(self, client, coe_advisor_login):
        """Returns a well-formed response when no cohort found."""
        response = client.get('/api/cohort/99999999')
        assert response.status_code == 404
        assert 'No cohort found' in str(response.data)

    def test_offset_and_limit(self, asc_advisor_login, asc_owned_cohort, client):
        """Returns a well-formed response with custom cohort."""
        cohort_id = asc_owned_cohort['id']
        api_path = f'/api/cohort/{cohort_id}'
        # First, offset is zero
        response = client.get(f'{api_path}?offset={0}&limit={1}')
        assert response.status_code == 200
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
        fake_auth.login('1133399')
        data = {
            'name': 'My filtered cohort just hacked the system!',
            'filters': [
                {'key': 'isInactiveAsc', 'value': True},
            ],
        }
        api_cohort_create(client, data, expected_status_code=403)

    def test_my_students_filter_me(self, client, asc_advisor_login):
        """My Students cohort filter."""
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='All my students',
            filter_criteria={
                'cohortOwnerAcademicPlans': ['*'],
            },
        )
        response = client.get(f"/api/cohort/{cohort['id']}")
        assert response.status_code == 200
        sids = sorted([s['sid'] for s in response.json['students']])
        assert sids == ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']

    def test_my_students_filter_not_me(self, client, admin_login):
        """The My Students cohort owned by some other advisor."""
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='All my students',
            filter_criteria={
                'cohortOwnerAcademicPlans': ['*'],
            },
        )
        response = client.get(f"/api/cohort/{cohort['id']}").json
        sids = sorted([s['sid'] for s in response['students']])
        assert sids == ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']

    def test_cohort_with_curated_group_ids(self, client, asc_advisor_login):
        """Cohort criteria can include filter-by-curated_group."""
        user_id = AuthorizedUser.get_id_per_uid(asc_advisor_uid)
        # We start with the SIDs expected from the 'My Students' filter and then reduce expectations based on
        # the curated group SIDs below.
        expected_sids = ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']

        curated_group_1 = CuratedGroup.create(user_id, 'Destined to be a cohort filter, #1')
        std_commit(allow_test_environment=True)
        sids_1 = ['2345678901', '5678901234', '9100000000']
        for sid in sids_1:
            CuratedGroup.add_student(curated_group_1.id, sid)
            std_commit(allow_test_environment=True)

        curated_group_2 = CuratedGroup.create(user_id, 'Destined to be a cohort filter, #2')
        std_commit(allow_test_environment=True)
        sids_2 = ['5678901234', '9000000000', '9100000000']
        for sid in sids_2:
            CuratedGroup.add_student(curated_group_2.id, sid)
            std_commit(allow_test_environment=True)

        # Filter out the SIDs that are NOT in the curated groups
        for sid in expected_sids:
            if sid not in sids_1 or sid not in sids_2:
                expected_sids.remove(sid)
        # Time to create cohort
        data = {
            'name': 'A cohort defined, in part, by curated_group_ids',
            'filters': [
                {'key': 'cohortOwnerAcademicPlans', 'value': '*'},
                {'key': 'curatedGroupIds', 'value': curated_group_1.id},
                {'key': 'curatedGroupIds', 'value': curated_group_2.id},
            ],
        }
        cohort_id = api_cohort_create(client, data)['id']

        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        api_json = json.loads(response.data)
        students = api_json['students']
        actual_sids = sorted([s['sid'] for s in students])
        assert actual_sids == expected_sids
        # If we delete a curated group referenced by the cohort then the cohort is quietly deleted, too.
        CuratedGroup.delete(curated_group_1.id)
        std_commit(allow_test_environment=True)
        assert CohortFilter.find_by_id(cohort_id) is None

    def test_cohort_student_count_when_curated_group_modified(self, client, asc_advisor_login):
        """Expect cohort SIDs and student-count to change if a referenced curated group is modified."""
        user_id = AuthorizedUser.get_id_per_uid(asc_advisor_uid)
        curated_group = CuratedGroup.create(user_id, 'Destined to be a cohort filter, #1')
        std_commit(allow_test_environment=True)
        original_sids = ['2345678901', '5678901234', '9100000000']
        for sid in original_sids:
            CuratedGroup.add_student(curated_group.id, sid)
            std_commit(allow_test_environment=True)
        # Create the cohort
        data = {
            'name': 'Hey! You got your chocolate in my peanut butter!',
            'filters': [
                {
                    'key': 'curatedGroupIds',
                    'value': curated_group.id,
                },
            ],
        }
        cohort = api_cohort_create(client, data)
        assert cohort['totalStudentCount'] == 3

        events = api_cohort_events(client, cohort['id'])['events']
        assert len(events) == 3
        assert sorted([e['sid'] for e in events]) == ['2345678901', '5678901234', '9100000000']
        assert sorted([e['firstName'] for e in events]) == ['Dave', 'Nora Stanton', 'Sandeep']
        for e in events:
            assert e['createdAt'] is not None
            assert e['eventType'] == 'added'

        api_curated_group_add_students(client, curated_group.id, sids=['11667051', '7890123456'])
        cohort = api_cohort_get(client, cohort['id'])
        assert cohort['totalStudentCount'] == 5

        events = api_cohort_events(client, cohort['id'])['events']
        assert len(events) == 5
        assert sorted([e['sid'] for e in events][0:2]) == ['11667051', '7890123456']
        assert sorted([e['firstName'] for e in events][0:2]) == ['Deborah', 'Paul']
        assert sorted([e['sid'] for e in events][2:5]) == ['2345678901', '5678901234', '9100000000']
        assert sorted([e['firstName'] for e in events][2:5]) == ['Dave', 'Nora Stanton', 'Sandeep']
        for e in events:
            assert e['createdAt'] is not None
            assert e['eventType'] == 'added'

        for sid in original_sids:
            api_curated_group_remove_student(client, curated_group_id=curated_group.id, sid=sid)
        cohort = api_cohort_get(client, cohort['id'])
        assert cohort['totalStudentCount'] == 2

        events = api_cohort_events(client, cohort['id'])['events']
        assert len(events) == 8
        assert sorted([e['sid'] for e in events][0:3]) == ['2345678901', '5678901234', '9100000000']
        assert sorted([e['firstName'] for e in events][0:3]) == ['Dave', 'Nora Stanton', 'Sandeep']
        assert sorted([e['sid'] for e in events][3:5]) == ['11667051', '7890123456']
        assert sorted([e['firstName'] for e in events][3:5]) == ['Deborah', 'Paul']
        assert sorted([e['sid'] for e in events][5:8]) == ['2345678901', '5678901234', '9100000000']
        assert sorted([e['firstName'] for e in events][5:8]) == ['Dave', 'Nora Stanton', 'Sandeep']
        for e in events[0:2]:
            assert e['createdAt'] is not None
            assert e['eventType'] == 'removed'
        for e in events[3:8]:
            assert e['createdAt'] is not None
            assert e['eventType'] == 'added'


class TestCohortsEveryone:

    @classmethod
    def _api_cohorts_all(cls, client, expected_status_code=200):
        response = client.get('/api/cohorts/all')
        assert response.status_code == expected_status_code
        return response.json

    def test_admitted_students_feature_flag(self, client, fake_auth):
        """Deny non-CE3 advisor access to non-default cohort domain."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', False):
            fake_auth.login(ce3_advisor_uid)
            api_json = self._api_cohorts_all(client)
            all_cohorts = [cohort for row in api_json for cohort in row['cohorts']]
            iterator = (cohort for cohort in all_cohorts if cohort['domain'] == 'admitted_students')
            assert next(iterator, None) is None

    def test_cohorts_all(self, asc_advisor_login, client):
        """Returns all cohorts per owner."""
        api_json = self._api_cohorts_all(client)
        count = len(api_json)
        assert count == 3
        for index, entry in enumerate(api_json):
            user = entry['user']
            if 0 < index < count:
                # Verify order
                assert user['name'] > api_json[index - 1]['user']['name']
            assert 'uid' in user
            cohorts = entry['cohorts']
            cohort_count = len(cohorts)
            for c_index, cohort in enumerate(cohorts):
                if 0 < c_index < cohort_count:
                    # Verify order
                    assert cohort['name'] > cohorts[c_index - 1]['name']
                assert 'id' in cohort

    def test_all_cohorts_of_default_domain(self, client, fake_auth):
        """Returns all cohorts, excluding admitted students."""
        fake_auth.login(ce3_advisor_uid)
        api_json = self._api_cohorts_all(client)
        for row in api_json:
            for cohort in row['cohorts']:
                assert cohort['domain'] == 'default'
                assert cohort['name'] != 'First Generation Students'

    def test_all_admitted_students_cohorts(self, client, fake_auth):
        """Returns all cohorts, excluding admitted students."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            fake_auth.login(ce3_advisor_uid)
            api_json = self._api_cohorts_all(client)
            all_cohorts = [cohort for row in api_json for cohort in row['cohorts']]
            iterator = (cohort for cohort in all_cohorts if cohort['domain'] == 'admitted_students')
            assert next(iterator, None) is not None

    def test_history_not_available_when_admitted_students_domain(self, client, fake_auth):
        """The cohort history feature is not available if domain is 'admitted_students'."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            fake_auth.login(ce3_advisor_uid)
            api_json = self._api_cohorts_all(client)
            cohorts = next(row['cohorts'] for row in api_json if len(row['cohorts']))
            api_cohort_events(client, cohorts[0]['id'], expected_status_code=400)


class TestCohortCreate:

    def test_create_cohort(self, client, asc_advisor_login, app):
        """Creates custom cohort, owned by current user."""
        data = {
            'name': 'Tennis',
            'filters': [
                {'key': 'majors', 'value': 'Letters & Sci Undeclared UG'},
                {'key': 'groupCodes', 'value': 'MTE'},
                {'key': 'majors', 'value': 'English BA'},
                {'key': 'genders', 'value': 'Male'},
            ],
        }

        def _verify(cohort):
            assert cohort.get('name') == 'Tennis'
            assert cohort['alertCount'] is not None
            assert len(cohort.get('criteria', {}).get('majors')) == 2
            # ASC specific
            team_groups = cohort.get('teamGroups')
            assert len(team_groups) == 1
            assert team_groups[0].get('groupCode') == 'MTE'
            # Students
            students = cohort.get('students')
            assert len(students) == 1
            assert students[0]['gender'] == 'Male'
            assert students[0]['underrepresented'] is False

        data = api_cohort_create(client, data)
        _verify(data)
        cohort_id = data.get('id')
        assert cohort_id
        _verify(api_cohort_get(client, cohort_id))

    def test_scheduler_role_is_forbidden(self, client, fake_auth):
        """Rejects COE scheduler user."""
        fake_auth.login(coe_scheduler_uid)
        data = {
            'name': 'COE scheduler cannot create cohorts',
            'filters': [
                {'key': 'coeEthnicities', 'value': 'Vietnamese'},
            ],
        }
        api_cohort_create(client, data, expected_status_code=401)

    def test_asc_advisor_is_forbidden(self, asc_advisor_login, client, fake_auth):
        """Denies ASC advisor access to COE data."""
        data = {
            'name': 'ASC advisor wants to see students of COE advisor',
            'filters': [
                {'key': 'coeEthnicities', 'value': 'Vietnamese'},
            ],
        }
        api_cohort_create(client, data, expected_status_code=403)

    def test_admin_create_of_coe_uid_cohort(self, admin_login, client, fake_auth):
        """Allows Admin to access COE data."""
        data = {
            'name': 'Admin wants to see students of COE advisor',
            'filters': [
                {'key': 'coeGenders', 'value': 'M'},
                {'key': 'genders', 'value': 'Different Identity'},
            ],
        }
        cohort = api_cohort_create(client, data)
        assert len(cohort['students']) == 2
        for student in cohort['students']:
            assert student['gender'] == 'Different Identity'
            assert student['coeProfile']['gender'] == 'M'

    def test_create_complex_cohort(self, client, coe_advisor_login):
        """Creates custom cohort, with many non-empty filter_criteria."""
        gpa_range_1 = {'min': 2, 'max': 2.499}
        gpa_range_2 = {'min': 0, 'max': 1.999}
        data = {
            'name': 'Complex',
            'filters': [
                {'key': 'majors', 'value': 'Gender and Women''s Studies'},
                {'key': 'gpaRanges', 'value': gpa_range_1},
                {'key': 'levels', 'value': 'Junior'},
                {'key': 'coeGenders', 'value': 'M'},
                {'key': 'genders', 'value': 'Genderqueer/Gender Non-Conform'},
                {'key': 'gpaRanges', 'value': gpa_range_2},
                {'key': 'majors', 'value': 'Environmental Economics & Policy'},
                {'key': 'intendedMajors', 'value': 'Public Health BA'},
                {'key': 'intendedMajors', 'value': 'Mathematics'},
                {'key': 'minors', 'value': 'Physics UG'},
            ],
        }
        cohort = api_cohort_create(client, data)
        cohort_id = cohort['id']
        api_json = api_cohort_get(client, cohort_id)
        assert api_json['alertCount'] is not None
        criteria = api_json.get('criteria')
        # Genders
        assert criteria.get('genders') == ['Genderqueer/Gender Non-Conform']
        # COE genders
        assert criteria.get('coeGenders') == ['M']
        # GPA
        gpa_ranges = criteria.get('gpaRanges')
        assert len(gpa_ranges) == 2
        assert gpa_range_1 in gpa_ranges
        assert gpa_range_2 in gpa_ranges
        # Intended majors
        intended_majors = criteria.get('intendedMajors')
        assert len(intended_majors) == 2
        assert 'Public Health BA' in intended_majors
        assert 'Mathematics' in intended_majors
        # Levels
        assert criteria.get('levels') == ['Junior']
        # Majors
        majors = criteria.get('majors')
        assert len(majors) == 2
        assert 'Gender and Women''s Studies' in majors
        # Minors
        minors = criteria.get('minors')
        assert len(minors) == 1
        assert 'Physics UG' in minors

    def test_admin_creation_of_asc_cohort(self, client, admin_login):
        """Admin can use ASC criteria."""
        api_cohort_create(
            client,
            {
                'name': 'Admin superpowers',
                'filters': [
                    {'key': 'groupCodes', 'value': 'MTE'},
                    {'key': 'groupCodes', 'value': 'WWP'},
                ],
            },
        )

    def test_forbidden_cohort_creation(self, client, coe_advisor_login):
        """COE advisor cannot use ASC criteria."""
        data = {
            'name': 'Sorry Charlie',
            'filters': [
                {'key': 'groupCodes', 'value': 'MTE'},
            ],
        }
        api_cohort_create(client, data, expected_status_code=403)

    _intersecting_filter_criteria = {
        'name': 'Mixmaster BOA',
        'filters': [
            {'key': 'groupCodes', 'value': 'MBB'},
            {'key': 'coeGenders', 'value': 'F'},
        ],
    }

    def test_admin_intersecting_filters(self, client, admin_login):
        """An admin can create a cohort using both ASC and COE criteria."""
        cohort = api_cohort_create(client, self._intersecting_filter_criteria)
        assert len(cohort['students']) == 1

    def test_multi_dept_intersecting_filters(self, client, fake_auth):
        """An advisor belonging to multiple departments can create a cohort using intersecting criteria."""
        fake_auth.login(asc_and_coe_advisor_uid)
        cohort = api_cohort_create(client, self._intersecting_filter_criteria)
        assert len(cohort['students']) == 1

    def test_single_dept_intersecting_filters_fails(self, client, coe_advisor_login):
        """An advisor belonging to a single department cannot create a cohort using intersecting criteria."""
        api_cohort_create(client, self._intersecting_filter_criteria, expected_status_code=403)

    def test_academic_standing_cohort(self, admin_login, client, fake_auth):
        """Find students per academic standing."""
        data = {
            'name': 'Probation and Subject to Dismissal',
            'filters': [
                {'key': 'academicStandings', 'value': '2182:PRO'},
                {'key': 'academicStandings', 'value': '2182:GST'},
                {'key': 'academicStandings', 'value': '2178:GST'},
            ],
        }
        cohort = api_cohort_create(client, data)
        assert len(cohort['students']) == 3
        sids = [s['sid'] for s in cohort['students']]
        assert set(sids) == {'11667051', '3456789012', '5678901234'}

    def test_active_students_cohort(self, admin_login, client, fake_auth):
        """By default finds active English majors only."""
        data = {
            'name': 'English Active',
            'filters': [
                {'key': 'majors', 'value': 'English BA'},
            ],
        }
        cohort = api_cohort_create(client, data)
        assert len(cohort['students']) == 2
        sids = [s['sid'] for s in cohort['students']]
        assert set(sids) == {'11667051', '3456789012'}

    def test_completed_students_cohort(self, admin_login, client, fake_auth):
        """Can find completed English majors on request."""
        data = {
            'name': 'English Completed',
            'filters': [
                {'key': 'majors', 'value': 'English BA'},
                {'key': 'academicCareerStatus', 'value': 'completed'},
            ],
        }
        cohort = api_cohort_create(client, data)
        assert len(cohort['students']) == 1
        sids = [s['sid'] for s in cohort['students']]
        assert set(sids) == {'2718281828'}

    def test_active_and_completed_students_cohort(self, admin_login, client, fake_auth):
        """Can find active and completed English majors on request."""
        data = {
            'name': 'English All',
            'filters': [
                {'key': 'majors', 'value': 'English BA'},
                {'key': 'academicCareerStatus', 'value': 'active'},
                {'key': 'academicCareerStatus', 'value': 'completed'},
            ],
        }
        cohort = api_cohort_create(client, data)
        assert len(cohort['students']) == 3
        sids = [s['sid'] for s in cohort['students']]
        assert set(sids) == {'11667051', '3456789012', '2718281828'}

    def test_inactive_students_cohort(self, admin_login, client, fake_auth):
        """Can find inactive students on request."""
        data = {
            'name': 'Inactive',
            'filters': [
                {'key': 'academicCareerStatus', 'value': 'inactive'},
            ],
        }
        cohort = api_cohort_create(client, data)
        assert len(cohort['students']) == 2
        sids = [s['sid'] for s in cohort['students']]
        assert set(sids) == {'3141592653', '9191919191'}


class TestCohortUpdate:

    @classmethod
    def _post_cohort_update(cls, client, json_data=()):
        return client.post(
            '/api/cohort/update',
            data=json.dumps(json_data),
            content_type='application/json',
        )

    def test_unauthorized_cohort_update(self, client, coe_advisor_login):
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='Swimming, Men\'s',
            filter_criteria={
                'groupCodes': ['MSW', 'MSW-DV', 'MSW-SW'],
            },
        )
        data = {
            'id': cohort['id'],
            'name': 'Hack the name!',
        }
        response = self._post_cohort_update(client, data)
        assert 403 == response.status_code

    def test_update_filters(self, client, asc_advisor_login):
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='Swimming, Men\'s',
            filter_criteria={
                'groupCodes': ['MBB', 'MBB-AA'],
            },
        )
        response = api_cohort_events(client, cohort['id'])
        assert response['count'] == 2
        assert len(response['events']) == 2
        assert next(e for e in response['events'] if e['sid'] == '3456789012' and e['eventType'] == 'added')
        assert next(e for e in response['events'] if e['sid'] == '7890123456' and e['eventType'] == 'added')

        # First, we POST an empty name
        cohort_id = cohort['id']
        response = self._post_cohort_update(client, {'id': cohort_id})
        assert 400 == response.status_code
        # Now, we POST a valid name
        gpa_range = {'min': 2, 'max': 2.499}
        data = {
            'id': cohort_id,
            'filters': [
                {'key': 'majors', 'value': 'Engineering Undeclared UG'},
                {'key': 'gpaRanges', 'value': gpa_range},
            ],
        }
        response = self._post_cohort_update(client, data)
        assert 200 == response.status_code
        updated_cohort = response.json
        assert updated_cohort['alertCount'] is not None
        assert updated_cohort['criteria']['majors'] == ['Engineering Undeclared UG']
        assert updated_cohort['criteria']['gpaRanges'] == [gpa_range]
        assert updated_cohort['criteria'].get('groupCodes') is None

        def remove_empties(criteria):
            return {k: v for k, v in criteria.items() if v is not None}
        cohort = CohortFilter.find_by_id(cohort_id)
        expected = remove_empties(cohort['criteria'])
        actual = remove_empties(updated_cohort['criteria'])
        assert expected == actual

        response = api_cohort_events(client, cohort['id'])
        assert response['count'] == 5
        assert len(response['events']) == 5
        assert response['events'][2]['sid'] == '9000000000'
        assert response['events'][2]['eventType'] == 'added'
        assert next(e for e in response['events'][0:2] if e['sid'] == '3456789012' and e['eventType'] == 'removed')
        assert next(e for e in response['events'][0:2] if e['sid'] == '7890123456' and e['eventType'] == 'removed')

    def test_cohort_update_filter_criteria(self, client, asc_advisor_login):
        name = 'Swimming, Men\'s'
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name=name,
            filter_criteria={
                'groupCodes': ['MBB'],
            },
        )
        cohort_id = cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        cohort = json.loads(response.data)
        assert cohort['totalStudentCount'] == 1

        events = api_cohort_events(client, cohort['id'])['events']
        assert len(events) == 1
        assert events[0]['eventType'] == 'added'
        assert events[0]['sid'] == '7890123456'
        assert events[0]['createdAt'] is not None

        # Update the db
        response = self._post_cohort_update(
            client,
            {
                'id': cohort_id,
                'filters': [
                    {'key': 'groupCodes', 'value': 'MBB'},
                    {'key': 'groupCodes', 'value': 'MBB-AA'},
                ],
            },
        )
        assert response.status_code == 200
        # Verify the value of 'student_count' in db
        updated_cohort = CohortFilter.find_by_id(cohort_id)
        assert updated_cohort['totalStudentCount'] == 2
        assert 'sids' not in updated_cohort
        group_codes = updated_cohort['criteria']['groupCodes']
        assert len(group_codes) == 2
        assert group_codes == ['MBB', 'MBB-AA']

        events = api_cohort_events(client, cohort['id'])['events']
        assert len(events) == 2
        assert events[0]['eventType'] == 'added'
        assert events[0]['sid'] == '3456789012'
        assert events[0]['createdAt'] is not None
        assert events[1]['eventType'] == 'added'
        assert events[1]['sid'] == '7890123456'
        assert events[0]['createdAt'] > events[1]['createdAt']


class TestCohortDelete:

    def test_delete_cohort_not_authenticated(self, client):
        """Custom cohort deletion requires authentication."""
        response = client.delete('/api/cohort/delete/123')
        assert response.status_code == 401

    def test_delete_cohort_wrong_user(self, client, fake_auth):
        """Custom cohort deletion is only available to the owner."""
        cohort = CohortFilter.create(
            uid=coe_advisor_uid,
            name='Badminton teams',
            filter_criteria={
                'groupCodes': ['WWP', 'MWP'],
            },
        )
        assert cohort

        # This user does not own the custom cohort above
        fake_auth.login('2040')
        cohort_id = cohort['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        _cohort = json.loads(response.data)
        assert _cohort['isOwnedByCurrentUser'] is False

        response = client.delete(f'/api/cohort/delete/{cohort_id}')
        assert response.status_code == 400
        assert '2040 does not own' in str(response.data)

    def test_delete_cohort(self, client, coe_advisor_login):
        """Deletes existing custom cohort while enforcing rules of ownership."""
        name = 'Water polo teams'
        cohort = CohortFilter.create(
            uid=coe_advisor_uid,
            name=name,
            filter_criteria={
                'groupCodes': ['WWP', 'MWP'],
            },
        )
        # Verify deletion
        cohort_id = cohort['id']
        response = client.delete(f'/api/cohort/delete/{cohort_id}')
        assert response.status_code == 200
        cohorts = all_cohorts_owned_by(asc_advisor_uid)
        assert not next((c for c in cohorts if c['id'] == cohort_id), None)


class TestCohortPerFilters:

    @classmethod
    def _api_get_students_per_filters(cls, client, json_data=(), expected_status_code=200):
        response = client.post(
            '/api/cohort/get_students_per_filters',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_students_per_filters_not_authenticated(self, client):
        """API requires authentication."""
        self._api_get_students_per_filters(client, expected_status_code=401)

    def test_students_per_filters_with_empty(self, client, coe_advisor_login):
        """API requires non-empty input."""
        self._api_get_students_per_filters(client, {'filters': []}, expected_status_code=400)

    def test_students_per_filters_unauthorized(self, client, asc_advisor_login):
        """ASC advisor is not allowed to query with COE attributes."""
        self._api_get_students_per_filters(
            client,
            {
                'filters':
                    [
                        {'key': 'coeProbation', 'value': 'true'},
                    ],
            },
            expected_status_code=403,
        )

    def test_students_per_ranges(self, client, coe_advisor_login):
        """API translates 'coeProbation' filter to proper filter_criteria query."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'gpaRanges', 'value': {'min': 0.000, 'max': 0.500}},
                    {'key': 'gpaRanges', 'value': {'min': 3, 'max': 4}},
                    {'key': 'lastNameRanges', 'value': {'min': 'Do', 'max': 'KE'}},
                ],
                'orderBy': 'last_name',
            },
        )
        students = api_json['students']
        assert len(students) == api_json.get('totalStudentCount')
        assert ['Doolittle', 'Farestveit', 'Jayaprakash', 'Kerschen'] == [s['lastName'] for s in students]
        assert [3.495, 3.9, 3.501, 3.005] == [s['cumulativeGPA'] for s in students]
        criteria = api_json['criteria']
        assert len(criteria['gpaRanges']) == 2
        assert len(criteria['lastNameRanges']) == 1

    def test_my_students_filter_all_plans(self, client, coe_advisor_login):
        """Returns students mapped to advisor, across all academic plans."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'cohortOwnerAcademicPlans', 'value': '*'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['11667051', '7890123456', '9000000000', '9100000000']

    def test_my_students_filter_selected_plans(self, client, coe_advisor_login):
        """Returns students mapped to advisor, per specified academic plans."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'cohortOwnerAcademicPlans', 'value': '162B0U'},
                    {'key': 'cohortOwnerAcademicPlans', 'value': '162B3U'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['7890123456', '9000000000']

    def _get_defensive_line(self, client, inactive_asc, order_by):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'groupCodes', 'value': 'MFB-DL'},
                    {'key': 'isInactiveAsc', 'value': inactive_asc},
                ],
                'orderBy': order_by,
            },
        )
        return api_json['students']

    def test_students_per_filters_order_by(self, client, asc_advisor_login):
        """Returns properly ordered list of students."""
        def _get_first_student(order_by):
            students = self._get_defensive_line(client, False, order_by)
            assert len(students) == 3
            return students[0]
        assert _get_first_student('first_name')['firstName'] == 'Dave'
        assert _get_first_student('last_name')['lastName'] == 'Doolittle'
        assert _get_first_student('gpa')['cumulativeGPA'] == 3.005
        assert _get_first_student('gpa desc')['cumulativeGPA'] == 3.501
        assert _get_first_student('level')['level'] == 'Junior'
        assert _get_first_student('major')['majors'][0] == 'Chemistry BS'
        assert _get_first_student('units')['cumulativeUnits'] == 34
        assert _get_first_student('units desc')['cumulativeUnits'] == 102
        assert _get_first_student('entering_term')['matriculation'] == 'Spring 2015'
        assert _get_first_student('terms_in_attendance')['termsInAttendance'] == 4
        assert _get_first_student('terms_in_attendance desc')['termsInAttendance'] == 5

        defensive_line_by_units = self._get_defensive_line(client, False, 'enrolled_units')
        assert 'term' not in defensive_line_by_units[-1]
        assert defensive_line_by_units[0]['term']['enrolledUnits'] == 5
        assert defensive_line_by_units[1]['term']['enrolledUnits'] == 7

        defensive_line_by_units_desc = self._get_defensive_line(client, False, 'enrolled_units desc')
        assert defensive_line_by_units_desc[0]['term']['enrolledUnits'] == 7
        assert defensive_line_by_units_desc[1]['term']['enrolledUnits'] == 5
        assert 'term' not in defensive_line_by_units_desc[2]

        def _fall_2017_gpa(student_feed):
            return next((t['gpa'] for t in student_feed['termGpa'] if t['termName'] == 'Fall 2017'), None)

        defensive_line_by_term_gpa = self._get_defensive_line(client, False, 'term_gpa_2178')
        assert _fall_2017_gpa(defensive_line_by_term_gpa[0]) == 2.1
        assert _fall_2017_gpa(defensive_line_by_term_gpa[1]) == 3.2
        assert _fall_2017_gpa(defensive_line_by_term_gpa[2]) is None

        defensive_line_by_term_gpa_desc = self._get_defensive_line(client, False, 'term_gpa_2178 desc')
        assert _fall_2017_gpa(defensive_line_by_term_gpa_desc[0]) == 3.2
        assert _fall_2017_gpa(defensive_line_by_term_gpa_desc[1]) == 2.1
        assert _fall_2017_gpa(defensive_line_by_term_gpa_desc[2]) is None

        student = _get_first_student('group_name')
        assert student['athleticsProfile']['athletics'][0]['groupName'] == 'Football, Defensive Backs'

    def test_student_athletes_inactive_asc(self, client, asc_advisor_login):
        """An ASC advisor query defaults to active athletes only."""
        students = self._get_defensive_line(client, False, 'gpa')
        assert len(students) == 3
        for student in students:
            assert student['athleticsProfile']['isActiveAsc'] is True

    def test_student_athletes_inactive_admin(self, client, admin_login):
        """An admin query defaults to active and inactive athletes."""
        students = self._get_defensive_line(client, None, 'gpa')
        assert len(students) == 4

        def is_active_asc(student):
            return student['athleticsProfile']['isActiveAsc']
        assert is_active_asc(students[0]) is False
        assert is_active_asc(students[1]) is True
        assert is_active_asc(students[2]) is True
        assert is_active_asc(students[3]) is True

    def test_filter_colleges(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'colleges', 'value': 'Undergrad Engineering'},
                    {'key': 'colleges', 'value': 'Undergrad Chemistry'},
                ],
            },
        )
        students = api_json['students']
        for student in students:
            assert ('Nuclear Engineering BS' in student['majors'] or 'Chemistry BS' in student['majors']
                    or 'Engineering Undeclared UG' in student['majors'])

    def test_filter_degree(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'degrees', 'value': 'Philosophy BA'},
                ],
            },
        )
        students = api_json['students']
        assert len(students) == 1
        assert students[0]['sid'] == '3141592653'

    def test_filter_degree_term(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'degreeTerms', 'value': '2202'},
                ],
            },
        )
        students = api_json['students']
        assert len(students) == 2
        assert students[0]['sid'] == '3141592653'
        assert students[1]['sid'] == '2718281828'

    def test_filter_division(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'academicDivisions', 'value': 'L&S Arts & Humanities Division'},
                ],
            },
        )

        students = api_json['students']
        assert len(students) == 2
        assert students[0]['sid'] == '11667051'
        assert students[1]['sid'] == '3456789012'

    def test_filter_entering_term(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'enteringTerms', 'value': '2155'},
                ],
            },
        )
        students = api_json['students']
        assert len(students) == 6
        for student in students:
            assert student['matriculation'] == 'Summer 2015'

    def test_filter_graduate_program(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'graduatePrograms', 'value': 'Mathematics PhD'},
                ],
            },
        )

        students = api_json['students']
        assert len(students) == 1
        assert students[0]['sid'] == '890127492'

    def test_filter_multiple_entering_terms(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'enteringTerms', 'value': '1938'},
                    {'key': 'enteringTerms', 'value': '2158'},
                ],
            },
        )
        students = api_json['students']
        assert len(students) == 2
        for student in students:
            assert student['matriculation'] in ['Fall 1993', 'Fall 2015']

    def test_filter_expected_grad_term(self, client, coe_advisor_login):
        """Returns students per expected graduation."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'expectedGradTerms', 'value': '2202'},
                ],
            },
        )
        students = api_json['students']
        assert len(students) == 2
        for student in students:
            assert student['expectedGraduationTerm']['name'] == 'Spring 2020'

    def test_filter_transfer(self, client, coe_advisor_login):
        """Returns list of transfer students."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'transfer', 'value': True},
                ],
            },
        )
        students = api_json['students']
        assert len(students) == 2
        for student in students:
            assert student['transfer'] is True

    def test_ethnicities_filter(self, client, coe_advisor_login):
        """Returns students of specified ethnicity."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'ethnicities', 'value': 'African-American / Black'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['2345678901', '3456789012', '890127492']

    def test_incomplete_date_filter(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'incompleteDateRanges', 'value': {'min': '2022-01-01', 'max': '2022-12-31'}},
                    {'key': 'academicCareerStatus', 'value': 'inactive'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['3141592653']

    def test_incomplete_status_filter(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'incomplete', 'value': 'scheduled'},
                    {'key': 'academicCareerStatus', 'value': 'inactive'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['3141592653']

    def test_midpoint_deficient_grade_filter(self, client, coe_advisor_login):
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'midpointDeficient', 'value': 'true'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['11667051']

    def test_last_term_gpa_filter(self, client, coe_advisor_login):
        summer_success = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'lastTermGpaRanges', 'value': {'min': 3, 'max': 4}},
                ],
            },
        )
        assert len(summer_success['students']) == 0
        summer_less_success = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'lastTermGpaRanges', 'value': {'min': 0, 'max': 0.5}},
                ],
            },
        )
        assert len(summer_less_success['students']) == 1
        assert {'termName': 'Summer 2017', 'gpa': 0.0} in summer_less_success['students'][0]['termGpa']

    def test_filter_visa_types(self, client, coe_advisor_login):
        """Returns students with verified visa status and the specified visa type(s)."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'visaTypes', 'value': 'F1'},
                    {'key': 'visaTypes', 'value': 'J1'},
                    {'key': 'visaTypes', 'value': 'PA,RF,L2,E2,H4,E1,U3,A1,E3,O1,OT,U1'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['2345678901', '5678901234']

    def test_filter_visa_types_all(self, client, coe_advisor_login):
        """Returns all students with verified visa status."""
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'visaTypes', 'value': '*'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['2345678901', '5678901234']


class TestDownloadCohortCsv:

    @classmethod
    def _api_download_cohort_csv(cls, client, cohort_id, csv_columns_selected, expected_status_code=200):
        response = client.post(
            '/api/cohort/download_csv',
            data=json.dumps({
                'cohortId': cohort_id,
                'csvColumnsSelected': csv_columns_selected,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.data

    def test_download_csv_not_authenticated(self, client, coe_owned_cohort):
        """API requires authentication."""
        self._api_download_cohort_csv(
            client,
            coe_owned_cohort['id'],
            csv_columns_selected=['sid'],
            expected_status_code=401,
        )

    def test_download_csv_unauthorized(self, client, asc_owned_cohort, coe_advisor_login):
        """ASC advisor cannot download cohort CSV containing COE attributes."""
        self._api_download_cohort_csv(
            client,
            cohort_id=asc_owned_cohort['id'],
            csv_columns_selected=['first_name', 'last_name', 'sid'],
            expected_status_code=404,
        )

    def test_download_csv(self, asc_advisor_login, client, fake_auth):
        """Advisor can download cohort CSV."""
        expected_sids = ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='Download Me',
            filter_criteria={
                'cohortOwnerAcademicPlans': ['*'],
            },
        )
        response = client.get(f"/api/cohort/{cohort['id']}")
        assert response.status_code == 200
        sids = sorted([s['sid'] for s in response.json['students']])
        assert sids == expected_sids
        data = self._api_download_cohort_csv(client, cohort['id'], csv_columns_selected=['sid'])
        sids_in_csv = [s for s in data.decode('utf-8').split() if s.isdigit()]
        assert sids_in_csv == expected_sids

        # Another ASC advisor downloads same CSV
        client.get('/api/auth/logout')
        fake_auth.login('6446')
        data = self._api_download_cohort_csv(client, cohort['id'], csv_columns_selected=['sid'])
        sids_in_csv = [s for s in data.decode('utf-8').split() if s.isdigit()]
        assert sids_in_csv == expected_sids


class TestDownloadCsvPerFilters:

    @classmethod
    def _api_download_csv_per_filters(cls, client, json_data=(), expected_status_code=200):
        response = client.post(
            '/api/cohort/download_csv_per_filters',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_download_csv_not_authenticated(self, client):
        """API requires authentication."""
        self._api_download_csv_per_filters(client, expected_status_code=401)

    def test_download_csv_with_empty(self, client, coe_advisor_login):
        """API requires non-empty input."""
        self._api_download_csv_per_filters(client, {'filters': ()}, expected_status_code=400)

    def test_download_csv_unauthorized(self, client, asc_advisor_login):
        """ASC advisor is not allowed to query with COE attributes."""
        self._api_download_csv_per_filters(
            client,
            {
                'filters': [
                    {'key': 'coeProbation', 'value': 'true'},
                ],
                'csvColumnsSelected': [
                    'first_name',
                    'last_name',
                    'sid',
                ],
            },
            expected_status_code=403,
        )

    def test_download_csv(self, client, coe_advisor_login):
        """Advisor can download CSV with ALL students of cohort."""
        data = {
            'filters': [
                {'key': 'coeEthnicities', 'value': ['H', 'B']},
            ],
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
                'email',
                'phone',
                'majors',
                'level_by_units',
                'terms_in_attendance',
                'expected_graduation_term',
                'units_completed',
                'term_gpa_2172',
                'term_gpa_2175',
                'cumulative_gpa',
                'program_status',
            ],
        }
        response = client.post(
            '/api/cohort/download_csv_per_filters',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = str(response.data)
        for snippet in [
            'first_name,last_name,sid,email,phone,majors,level_by_units,terms_in_attendance,expected_graduation_term,units_completed,term_gpa_2172,term_gpa_2175,cumulative_gpa,program_status',  # noqa: E501
            'Deborah,Davies,11667051,barnburner@berkeley.edu,415/123-4567,English BA;Nuclear Engineering BS,Junior,,Fall 2019,101.3,2.700,,3.8,Active',  # noqa: E501
            'Paul,Farestveit,7890123456,qadept@berkeley.edu,415/123-4567,Nuclear Engineering BS,Senior,2,Spring 2020,110,,,3.9,Active',
        ]:
            assert str(snippet) in csv

    def test_download_csv_custom_columns(self, client, coe_advisor_login):
        """Advisor can generate a CSV with the columns they want."""
        data = {
            'filters': [
                {'key': 'levels', 'value': 'Junior'},
            ],
            'csvColumnsSelected': [
                'majors',
                'level_by_units',
                'terms_in_attendance',
                'expected_graduation_term',
                'units_completed',
                'term_gpa_2172',
                'cumulative_gpa',
                'program_status',
                'intended_majors',
                'minors',
            ],
        }
        response = client.post(
            '/api/cohort/download_csv_per_filters',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = str(response.data)
        for snippet in [
            'majors,level_by_units,terms_in_attendance,expected_graduation_term,units_completed,term_gpa_2172,cumulative_gpa,program_status,intended_majors,minors',  # noqa: E501
            'Chemistry BS,Junior,4,Fall 2019,34,3.500,3.495,Active,',
            'English BA;Political Economy BA,Junior,5,Fall 2019,70,,3.005,Active,',
        ]:
            assert str(snippet) in csv

    admit_keys = [
        'applyuc_cpid',
        'cs_empl_id',
        'residency_category',
        'freshman_or_transfer',
        'admit_term',
        'admit_status',
        'current_sir',
        'college',
        'first_name',
        'middle_name',
        'last_name',
        'birthdate',
        'daytime_phone',
        'mobile',
        'permanent_street_1',
        'permanent_street_2',
        'permanent_city',
        'permanent_region',
        'permanent_postal',
        'permanent_country',
        'sex',
        'gender_identity',
        'xethnic',
        'hispanic',
        'urem',
        'first_generation_college',
        'parent_1_education_level',
        'parent_2_education_level',
        'highest_parent_education_level',
        'hs_unweighted_gpa',
        'hs_weighted_gpa',
        'transfer_gpa',
        'act_composite',
        'act_math',
        'act_english',
        'act_reading',
        'act_writing',
        'sat_total',
        'sat_r_evidence_based_rw_section',
        'sat_r_math_section',
        'sat_r_essay_reading',
        'sat_r_essay_analysis',
        'sat_r_essay_writing',
        'application_fee_waiver_flag',
        'foster_care_flag',
        'family_is_single_parent',
        'student_is_single_parent',
        'family_dependents_num',
        'student_dependents_num',
        'family_income',
        'student_income',
        'is_military_dependent',
        'military_status',
        'reentry_status',
        'athlete_status',
        'summer_bridge_status',
        'last_school_lcff_plus_flag',
        'special_program_cep',
        'us_citizenship_status',
        'us_non_citizen_status',
        'citizenship_country',
        'permanent_residence_country',
        'non_immigrant_visa_current',
        'non_immigrant_visa_planned',
        'uid',
    ]

    @classmethod
    def _api_download_admit_csv(cls, client, expected_status_code=200):
        data = {
            'filters': [
                {'key': 'isFirstGenerationCollege', 'value': True},
            ],
            'csvColumnsSelected': cls.admit_keys,
            'domain': 'admitted_students',
        }
        response = client.post(
            '/api/cohort/download_csv_per_filters',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response

    def test_download_csv_admit_domain(self, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            fake_auth.login(ce3_advisor_uid)
            response = self._api_download_admit_csv(client)
            assert 'csv' in response.content_type
            csv = str(response.data)
            assert ','.join(self.admit_keys) in csv
            assert (
                '19938035,00005852,RES,Transfer,Spring,No,No,College of Letters and Science,'
                'Ralph,,Burgess,1984-09-04,984.110.7693x347,681-857-8070,9590 Chang Extensions,'
                'Suite 478,East Jacobton,NY,55531,United States,F,Other,International,F,No,Yes,MasterDegree,'
                '3 - High School Graduate,,0.86,0.51,2.47,7,18,29,18,3,603,707,241,3,2,4,FeeWaiver,Y,,,05,02,41852,942,Y,'
                'ReserveOfficersTrainingProgram,No,,,,,Citizen,,United States,,,,123'
            ) in csv
            assert (
                '98002344,00029117,INT,Freshman,Spring,No,No,College of Engineering,Daniel,J,Mcknight,1993-07-06,859-319-8215x8689,'
                '231.865.8093,87758 Brown Throughway,Suite 657,West Andrea,M,25101,United States,,Other,White,T,,'
                'Yes,,5 - College Attended,,2.51,2.7,3.23,25,19,2,15,9,1445,639,724,7,5,5,,,,Y,0,02,23915,426,Y,,,Committed,,1,'
                'Destination College,Citizen,,United States,,,,'
            ) in csv

    def test_admit_domain_denies_non_ce3_advisor(self, user_factory, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            advisor = user_factory(dept_codes=['GUEST'])
            fake_auth.login(advisor.uid)
            self._api_download_admit_csv(client, 403)

    def test_admit_domain_respects_feature_flag(self, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', False):
            fake_auth.login(ce3_advisor_uid)
            self._api_download_admit_csv(client, 404)


class TestCohortFilterOptions:

    @classmethod
    def _api_cohort_filter_options(cls, client, json_data=(), owner='me', expected_status_code=200):
        response = client.post(
            f'/api/cohort/filter_options/{owner}',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_filter_options_api_not_authenticated(self, client):
        """Menu API cohort-filter-options requires authentication."""
        self._api_cohort_filter_options(client, expected_status_code=401)

    def test_filter_options_with_nothing_disabled(self, client, coe_advisor_login):
        """Menu API with all menu options available."""
        api_json = self._api_cohort_filter_options(client, {'existingFilters': []})
        for label, option_group in api_json.items():
            for entry in option_group:
                assert 'disabled' not in entry
                if entry['type']['ux'] == 'dropdown':
                    for option in entry['options']:
                        assert 'disabled' not in option

    def test_filter_options_for_guest_user(self, user_factory, client, fake_auth):
        """Filter options available to GUEST user."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, {'existingFilters': []})
        assert len(api_json)
        assert 'options' in list(api_json.values())[0][0]

    def test_filter_options_for_user_of_type_other(self, user_factory, client, fake_auth):
        """Filter options available to ZZZZZ user."""
        advisor = user_factory(dept_codes=['ZZZZZ'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, {'existingFilters': []})
        assert len(api_json)
        assert 'options' in list(api_json.values())[0][0]

    def test_filter_options_my_students_for_me(self, client, coe_advisor_login):
        """Returns user's own academic plans under 'My Students'."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters': [],
            },
        )
        my_students = next(opt for label, group in api_json.items() for opt in group if opt['label']['primary'] == 'My Students')
        assert len(my_students['options']) == 5
        assert {'name': 'All plans', 'value': '*'} in my_students['options']
        assert {'name': 'Bioengineering BS', 'value': '16288U'} in my_students['options']
        assert {'name': 'Engineering Undeclared UG', 'value': '162B0U'} in my_students['options']
        assert {'name': 'BioE/MSE Joint Major BS', 'value': '162B3U'} in my_students['options']
        assert {'name': 'Bioengineering UG', 'value': '16I010U'} in my_students['options']

    def test_filter_options_my_students_for_not_me(self, client, coe_advisor_login):
        """Returns another user's academic plans under 'My Students'."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters': [],
            },
            asc_advisor_uid,
        )
        my_students = next(opt for label, group in api_json.items() for opt in group if opt['label']['primary'] == 'My Students')
        assert len(my_students['options']) == 4
        assert {'name': 'All plans', 'value': '*'} in my_students['options']
        assert {'name': 'English BA', 'value': '25345U'} in my_students['options']
        assert {'name': 'English UG', 'value': '25I039U'} in my_students['options']
        assert {'name': 'Medieval Studies UG', 'value': '25I054U'} in my_students['options']

    def test_filter_options_with_category_disabled(self, client, coe_advisor_login):
        """The coe_probation option is disabled if it is in existing-filters."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters':
                    [
                        {'key': 'coeProbation', 'value': True},
                    ],
            },
        )
        assert len(api_json.keys())
        for label, option_group in api_json.items():
            for entry in option_group:
                if entry['key'] == 'coeProbation':
                    assert entry['disabled'] is True
                else:
                    assert 'disabled' not in entry

    def test_filter_options_with_one_disabled(self, client, coe_advisor_login):
        """The 'Freshman' sub-menu option is disabled if it is already in cohort filter set."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters':
                    [
                        {'key': 'levels', 'value': 'Freshman'},
                        {'key': 'levels', 'value': 'Sophomore'},
                        {'key': 'levels', 'value': 'Junior'},
                        {'key': 'coeAdvisorLdapUids', 'value': '1022796'},
                    ],
            },
        )
        assert len(api_json.keys())
        assertion_count = 0
        for label, opt_group in api_json.items():
            for entry in opt_group:
                # All top-level category menus are enabled
                assert 'disabled' not in entry
                if entry['key'] == 'levels':
                    for option in entry['options']:
                        disabled = option.get('disabled')
                        if option['value'] in ['Freshman', 'Sophomore', 'Junior']:
                            assert disabled is True
                            assertion_count += 1
                        else:
                            assert disabled is None
                else:
                    assert 'disabled' not in entry
        assert assertion_count == 3

    def test_all_options_in_category_disabled(self, client, coe_advisor_login):
        """Disable the category if all its options are in existing-filters."""
        api_json = self._api_cohort_filter_options(
            client,
            {
                'existingFilters':
                    [
                        {'key': 'cohortOwnerAcademicPlans', 'value': '*'},
                        {'key': 'levels', 'value': 'Doctoral Candidate > 6'},
                        {'key': 'levels', 'value': 'Doctoral Candidate <= 6'},
                        {'key': 'levels', 'value': 'Doctoral Pre-Candidacy'},
                        {'key': 'levels', 'value': 'Masters/Professional'},
                        {'key': 'levels', 'value': 'Senior'},
                        {'key': 'levels', 'value': 'Junior'},
                        {'key': 'levels', 'value': 'Sophomore'},
                        {'key': 'levels', 'value': 'Freshman'},
                        {'key': 'visaTypes', 'value': '*'},
                    ],
            },
        )
        for label, option_group in api_json.items():
            for entry in option_group:
                if entry['key'] == 'cohortOwnerAcademicPlans':
                    assert entry.get('disabled') is True
                elif entry['key'] == 'levels':
                    assert entry.get('disabled') is True
                    for option in entry['options']:
                        assert option.get('disabled') is True
                elif entry['key'] == 'visaTypes':
                    assert entry.get('disabled') is True
                else:
                    assert 'disabled' not in entry

    def test_range_of_entering_terms(self, user_factory, client, fake_auth):
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, {'existingFilters': []})
        entering_terms_filter = next((f for f in api_json['Academic'] if f['key'] == 'enteringTerms'), None)
        assert entering_terms_filter
        filter_options = entering_terms_filter.get('options')
        assert len(filter_options) == 4
        assert [o['name'] for o in filter_options] == ['2015 Fall', '2015 Summer', '2015 Spring', '1993 Fall']

    def test_range_of_expected_grad_terms(self, user_factory, client, fake_auth):
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, {'existingFilters': []})
        entering_terms_filter = next((f for f in api_json['Academic'] if f['key'] == 'expectedGradTerms'), None)
        assert entering_terms_filter
        filter_options = entering_terms_filter.get('options')
        assert len(filter_options['Past']) == 1
        assert filter_options['Past'][0]['name'] == '1997 Fall'

    def test_range_of_majors(self, user_factory, client, fake_auth):
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, {'existingFilters': []})
        majors_filter = next((f for f in api_json['Academic'] if f['key'] == 'majors'), None)
        assert {'name': 'Chemistry BS', 'value': 'Chemistry BS'} in majors_filter['options']
        assert {'name': 'Nuclear Engineering BS', 'value': 'Nuclear Engineering BS'} in majors_filter['options']
        assert {'name': 'Mathematics PhD', 'value': 'Mathematics PhD'} not in majors_filter['options']

    def test_range_of_graduate_programs(self, user_factory, client, fake_auth):
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, {'existingFilters': []})
        majors_filter = next((f for f in api_json['Academic'] if f['key'] == 'graduatePrograms'), None)
        assert len(majors_filter['options']) == 1
        assert majors_filter['options'][0] == {'name': 'Mathematics PhD', 'value': 'Mathematics PhD'}

    def test_no_curated_group_options(self, client, fake_auth):
        """User with no curated groups gets no cohort filter option where key='curatedGroupIds'."""
        fake_auth.login(asc_and_coe_advisor_uid)
        user_id = AuthorizedUser.get_id_per_uid(asc_and_coe_advisor_uid)
        assert not CuratedGroup.get_curated_groups(user_id)
        api_json = self._api_cohort_filter_options(client, {'existingFilters': []})
        verified = False
        for label, option_group in api_json.items():
            for filter_ in option_group:
                if filter_['key'] == 'curatedGroupIds':
                    assert filter_['disabled'] is True
                    verified = True
        assert verified

    def test_404_when_feature_flag_is_false(self, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', False):
            fake_auth.login(ce3_advisor_uid)
            self._api_cohort_filter_options(
                client,
                {
                    'domain': 'admitted_students',
                    'existingFilters': [],
                },
                expected_status_code=404,
            )

    def test_invalid_domain_value(self, user_factory, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            advisor = user_factory(dept_codes=['GUEST'])
            fake_auth.login(advisor.uid)
            self._api_cohort_filter_options(
                client,
                {
                    'domain': 'this_is_an_invalid_domain',
                    'existingFilters': [],
                },
                expected_status_code=400,
            )

    def test_admitted_students_domain_denied(self, user_factory, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            advisor = user_factory(dept_codes=['GUEST'])
            fake_auth.login(advisor.uid)
            self._api_cohort_filter_options(
                client,
                {
                    'domain': 'admitted_students',
                    'existingFilters': [],
                },
                expected_status_code=403,
            )

    def test_admitted_students_domain(self, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            fake_auth.login(ce3_advisor_uid)
            api_json = self._api_cohort_filter_options(
                client,
                {
                    'domain': 'admitted_students',
                    'existingFilters': [],
                },
            )
            assert len(api_json)
            for label, option_group in api_json.items():
                for entry in option_group:
                    # Verify the 'default' filters are not present.
                    assert 'unitRanges' != entry['key']
                    assert entry['domain'] == 'admitted_students'


class TestTranslateToFilterOptions:

    @classmethod
    def _api_translate_to_filter_options(cls, client, json_data=(), owner='me', expected_status_code=200):
        response = client.post(
            f'/api/cohort/translate_to_filter_options/{owner}',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_translate_criteria_when_empty(self, client, coe_advisor_login):
        """Empty criteria translates to zero rows."""
        assert [] == self._api_translate_to_filter_options(
            client,
            {
                'criteria': {},
            },
        )

    def test_translate_criteria_with_boolean(self, client, coe_advisor_login):
        """Filter-criteria with boolean is properly translated."""
        json_data = {
            'criteria': {
                'isInactiveCoe': False,
            },
        }
        api_json = self._api_translate_to_filter_options(client, json_data)
        assert len(api_json) == 1
        assert api_json[0]['label']['primary'] == 'Inactive (COE)'
        assert api_json[0]['key'] == 'isInactiveCoe'
        assert api_json[0]['value'] is False

    def test_translate_criteria_with_array(self, client, coe_advisor_login):
        """Filter-criteria with array is properly translated."""
        api_json = self._api_translate_to_filter_options(
            client,
            {
                'criteria': {
                    'genders': ['Female', 'Decline to State'],
                    'levels': ['Freshman', 'Sophomore'],
                },
            },
        )
        assert len(api_json) == 4
        # Levels
        assert api_json[0]['label']['primary'] == api_json[1]['label']['primary'] == 'Level'
        assert api_json[0]['key'] == api_json[1]['key'] == 'levels'
        assert api_json[0]['value'] == 'Freshman'
        assert api_json[1]['value'] == 'Sophomore'
        # Genders
        assert api_json[2]['label']['primary'] == api_json[3]['label']['primary'] == 'Gender'
        assert api_json[2]['key'] == api_json[3]['key'] == 'genders'
        assert api_json[2]['value'] == 'Female'
        assert api_json[3]['value'] == 'Decline to State'

    def test_handle_last_name_ranges(self, client, coe_advisor_login):
        """Filter-criteria with last_name range is properly translated."""
        last_name_ranges = [
            {'min': 'B', 'max': 'D'},
            {'min': 'M', 'max': 'Z'},
        ]
        api_json = self._api_translate_to_filter_options(
            client,
            {
                'criteria': {
                    'lastNameRanges': last_name_ranges,
                },
            },
        )
        assert len(api_json) == 2

        def _verify(index):
            assert api_json[index]['label']['primary'] == 'Last Name'
            assert api_json[index]['key'] == 'lastNameRanges'
            assert api_json[index]['value'] == last_name_ranges[index]
        _verify(0)
        _verify(1)

    def test_translate_criteria_my_students_for_me(self, client, coe_advisor_login):
        """User's own 'My Students' criteria are properly translated."""
        api_json = self._api_translate_to_filter_options(
            client,
            {
                'criteria': {
                    'cohortOwnerAcademicPlans': ['*'],
                },
            },
        )
        assert len(api_json) == 1
        assert api_json[0]['label']['primary'] == 'My Students'
        assert api_json[0]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[0]['value'] == '*'

    def test_translate_criteria_my_students_for_not_me(self, client, coe_advisor_login):
        """Another user's 'My Students' criteria are properly translated."""
        api_json = self._api_translate_to_filter_options(
            client,
            {
                'criteria': {
                    'cohortOwnerAcademicPlans': ['25I039U', '25I054U'],
                },
            },
            asc_advisor_uid,
        )
        assert len(api_json) == 2
        assert api_json[0]['label']['primary'] == 'My Students'
        assert api_json[0]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[0]['value'] == '25I039U'
        assert api_json[1]['label']['primary'] == 'My Students'
        assert api_json[1]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[1]['value'] == '25I054U'


def _new_undeclared_cohort(client):
    data = {
        'name': 'Nothing to Declare',
        'filters': [
            {'key': 'majors', 'value': 'Letters & Sci Undeclared UG'},
        ],
    }
    cohort = api_cohort_create(client, data)
    cohort_id = cohort['id']
    response = client.get(f'/api/cohort/{cohort_id}')
    assert response.status_code == 200
    return response.json
