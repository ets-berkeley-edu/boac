"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

import simplejson as json

from boac import std_commit
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from tests.test_api.api_test_utils import (
    all_cohorts_owned_by,
    api_cohort_create,
    api_cohort_events,
    api_curated_group_add_students,
    api_curated_group_remove_student,
    api_get_cohort,
)

admin_uid = '177473'
asc_advisor_uid = '1081940'
asc_and_coe_advisor_uid = '90412'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'


class TestCohortById:
    """Cohort by ID API."""

    @classmethod
    def setup_class(cls):
        cls.coe_owned_cohort = next((c for c in all_cohorts_owned_by(coe_advisor_uid) if c['name'] == 'Radioactive Women and Men'), None)
        cls.asc_owned_cohort = next((c for c in all_cohorts_owned_by(asc_advisor_uid) if c['name'] == 'All sports'), None)

    def test_students_with_alert_counts(self, client, fake_auth, create_alerts):  # noqa: ARG002
        """Pre-load students into cache for consistent alert data."""
        fake_auth.login(asc_advisor_uid)
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

    def test_get_cohort(self, client, fake_auth, create_alerts):  # noqa: ARG002
        """Returns a well-formed response with filtered cohort and alert count per student."""
        fake_auth.login(coe_advisor_uid)
        cohort_id = self.coe_owned_cohort['id']
        api_json = api_get_cohort(client, cohort_id, include_students=True)
        assert api_json['id'] == cohort_id
        assert api_json['name'] == self.coe_owned_cohort['name']
        assert 'students' in api_json
        assert api_json['students'][0].get('alertCount') == 4

    def test_get_cohort_without_students(self, client, fake_auth):
        """Cohort with include_students set to False."""
        fake_auth.login(coe_advisor_uid)
        api_json = api_get_cohort(client, self.coe_owned_cohort['id'], include_students=False)
        assert 'students' not in api_json

    def test_advisor_cannot_see_admin_cohort(self, client, fake_auth):
        """Cohorts created by Admin users are not viewable by non-Admin users."""
        fake_auth.login(asc_advisor_uid)
        cohort_id = all_cohorts_owned_by(admin_uid)[0]['id']
        api_get_cohort(client, cohort_id, expected_status_code=404)

    def test_undeclared_major(self, client, fake_auth):
        """Get cohort: Undeclared Major."""
        fake_auth.login(asc_advisor_uid)
        cohort = all_cohorts_owned_by(asc_advisor_uid)[-1]
        api_json = api_get_cohort(client, cohort['id'], include_students=True)
        assert api_json['name'] == 'Undeclared students'
        students = api_json['students']
        assert api_json['totalStudentCount'] == len(students) == 1
        # We expect the student with 'Letters & Sci Undeclared UG' major
        assert students[0]['sid'] == '5678901234'

    def test_includes_cohort_member_sis_data(self, client, fake_auth):
        """Includes SIS data for custom cohort students."""
        fake_auth.login(asc_advisor_uid)
        api_json = api_get_cohort(client, cohort_id=self.asc_owned_cohort['id'], include_students=True)
        athlete = next(m for m in api_json['students'] if m['firstName'] == 'Deborah')
        assert athlete['cumulativeGPA'] == 3.8
        assert athlete['cumulativeUnits'] == 101.3
        assert athlete['level'] == 'Junior'
        assert athlete['majors'] == ['English BA', 'Nuclear Engineering BS']

    def test_includes_cohort_member_current_enrollments(self, client, fake_auth):
        """Includes current-term active enrollments for custom cohort students."""
        fake_auth.login(asc_advisor_uid)
        api_json = api_get_cohort(
            client,
            cohort_id=self.asc_owned_cohort['id'],
            include_students=True,
            order_by='firstName',
        )
        athlete = next(m for m in api_json['students'] if m['firstName'] == 'Deborah')
        term = athlete['term']
        assert term['termName'] == 'Fall 2017'
        assert term['enrolledUnits'] == 12.5
        assert len(term['enrollments']) == 5
        assert term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(term['enrollments'][0]['canvasSites']) == 1

    def test_includes_cohort_member_non_current_enrollments(self, client, fake_auth):
        """Includes active enrollments for a non-current term if requested."""
        fake_auth.login(asc_advisor_uid)
        api_json = api_get_cohort(
            client,
            cohort_id=self.asc_owned_cohort['id'],
            include_students=True,
            order_by='firstName',
            term_id=2172,
        )
        athlete = next(m for m in api_json['students'] if m['firstName'] == 'Deborah')
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

    def test_includes_cohort_member_term_gpa(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        api_json = api_get_cohort(
            client,
            cohort_id=self.asc_owned_cohort['id'],
            include_students=True,
            order_by='firstName',
        )
        deborah = next(m for m in api_json['students'] if m['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}

    def test_includes_cohort_member_academic_standing(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        api_json = api_get_cohort(
            client,
            cohort_id=self.asc_owned_cohort['id'],
            include_students=True,
            order_by='firstName',
        )
        deborah = next(m for m in api_json['students'] if m['firstName'] == 'Deborah')
        assert deborah['academicStanding'] == {
            'actionDate': '2018-05-31',
            'status': 'GST',
            'termName': 'Spring 2018',
        }

    def test_includes_cohort_member_athletics_asc(self, client, fake_auth):
        """Includes athletic data custom cohort members for ASC advisors."""
        fake_auth.login(asc_advisor_uid)
        api_json = api_get_cohort(
            client,
            cohort_id=self.asc_owned_cohort['id'],
            include_students=True,
        )
        athlete = next(m for m in api_json['students'] if m['firstName'] == 'Deborah')
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

    def test_omits_cohort_member_athletics_non_asc(self, client, fake_auth):
        """Omits athletic data for non-ASC advisors."""
        fake_auth.login(coe_advisor_uid)
        api_json = api_get_cohort(
            client,
            cohort_id=self.coe_owned_cohort['id'],
            include_students=True,
        )
        secretly_an_athlete = next(m for m in api_json['students'] if m['firstName'] == 'Deborah')
        assert 'athletics' not in secretly_an_athlete
        assert 'inIntensiveCohort' not in secretly_an_athlete
        assert 'isActiveAsc' not in secretly_an_athlete
        assert 'statusAsc' not in secretly_an_athlete

    def test_includes_cohort_member_athletics_advisors(self, client, fake_auth):
        """Includes athletic data for admins."""
        fake_auth.login(admin_uid)
        api_json = api_get_cohort(
            client,
            cohort_id=self.coe_owned_cohort['id'],
            include_students=True,
        )
        athlete = next(m for m in api_json['students'] if m['firstName'] == 'Deborah')
        assert len(athlete['athleticsProfile']['athletics']) == 2
        assert athlete['athleticsProfile']['inIntensiveCohort'] is not None
        assert athlete['athleticsProfile']['isActiveAsc'] is not None
        assert athlete['athleticsProfile']['statusAsc'] is not None

    def test_get_cohort_404(self, client, fake_auth):
        """Get cohort: Dummy cohort_id results in HTTP 404."""
        fake_auth.login(coe_advisor_uid)
        api_get_cohort(client, cohort_id=99999999, expected_status_code=404)

    def test_offset_and_limit(self, client, fake_auth):
        """Get cohort: Offset and limit."""
        fake_auth.login(asc_advisor_uid)
        cohort_id = self.asc_owned_cohort['id']
        api_json = api_get_cohort(
            client,
            cohort_id=cohort_id,
            include_students=True,
            limit=1,
            offset=0,
        )
        assert api_json['totalStudentCount'] == 4
        assert len(api_json['students']) == 1
        first_student_uid = api_json['students'][0]['uid']
        # Now, offset is one
        api_json = api_get_cohort(
            client,
            cohort_id=cohort_id,
            include_students=True,
            limit=1,
            offset=1,
        )
        assert len(api_json['students']) == 1
        # Verify that a different offset results in a different member
        assert api_json['students'][0]['uid'] != first_student_uid

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

    def test_my_students_filter_me(self, client, fake_auth):
        """My Students cohort filter."""
        fake_auth.login(asc_advisor_uid)
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='All my students',
            filter_criteria={
                'cohortOwnerAcademicPlans': ['*'],
            },
        )
        api_json = api_get_cohort(client, cohort_id=cohort['id'], include_students=True)
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']

    def test_my_students_filter_not_me(self, client, fake_auth):
        """The My Students cohort owned by some other advisor."""
        fake_auth.login(admin_uid)
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='All my students',
            filter_criteria={
                'cohortOwnerAcademicPlans': ['*'],
            },
        )
        api_json = api_get_cohort(client, cohort_id=cohort['id'], include_students=True)
        sids = sorted([student['sid'] for student in api_json['students']])
        assert sids == ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']

    def test_cohort_with_curated_group_ids(self, client, fake_auth):
        """Cohort criteria can include filter-by-curated_group."""
        fake_auth.login(asc_advisor_uid)
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
        cohort = api_cohort_create(client, data)
        cohort_id = cohort['id']
        api_json = api_get_cohort(client, cohort_id=cohort_id, include_students=True)
        students = api_json['students']
        actual_sids = sorted([s['sid'] for s in students])
        assert actual_sids == expected_sids
        # If we delete a curated group referenced by the cohort then the cohort is quietly deleted, too.
        CuratedGroup.delete(curated_group_1.id)
        std_commit(allow_test_environment=True)
        assert CohortFilter.find_by_id(cohort_id) is None

    def test_cohort_student_count_when_curated_group_modified(self, client, fake_auth):
        """Expect cohort SIDs and student-count to change if a referenced curated group is modified."""
        fake_auth.login(asc_advisor_uid)
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

        api_curated_group_add_students(client, [curated_group.id], sids=['11667051', '7890123456'])
        cohort = api_get_cohort(client, cohort['id'])
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
            api_curated_group_remove_student(client, curated_group_ids=[curated_group.id], sid=sid)
        cohort = api_get_cohort(client, cohort['id'])
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
    """Everyone's Cohorts API."""

    @classmethod
    def _api_cohorts_by_dept_code(cls, client, dept_code, expected_status_code=200):
        response = client.get(f'/api/cohorts/by_dept_code/{dept_code}')
        assert response.status_code == expected_status_code
        return response.json

    def test_cohorts_all(self, client, fake_auth):
        """Returns all cohorts of ASC advisor."""
        fake_auth.login(asc_advisor_uid)
        api_json = self._api_cohorts_by_dept_code(client, 'COENG')
        assert len(api_json) == 1
        for index, user in enumerate(api_json):
            cohorts = user['cohorts']
            assert len(cohorts)
            if 0 < index < len(cohorts):
                # Verify order
                assert user['name'] > cohorts[index - 1]['user']['name']
            assert 'uid' in user
            for c_index, cohort in enumerate(cohorts):
                if 0 < c_index < len(cohorts):
                    # Verify order
                    assert cohort['name'] > cohorts[c_index - 1]['name']
                assert 'id' in cohort

    def test_all_cohorts_of_default_domain(self, client, fake_auth):
        """Returns all cohorts, excluding admitted students."""
        fake_auth.login(ce3_advisor_uid)
        api_json = self._api_cohorts_by_dept_code(client, 'UWASC')
        assert len(api_json)
        cohorts = api_json[0]['cohorts']
        assert len(cohorts)
        assert cohorts[0]['domain'] == 'default'
        assert cohorts[0]['name'] == 'All sports'

    def test_all_admitted_students_cohorts(self, client, fake_auth):
        """Returns all cohorts, excluding admitted students."""
        fake_auth.login(ce3_advisor_uid)
        api_json = self._api_cohorts_by_dept_code(client, 'ZCEEE')
        all_cohorts = [cohort for row in api_json for cohort in row['cohorts']]
        iterator = (cohort for cohort in all_cohorts if cohort['domain'] == 'admitted_students')
        assert next(iterator, None) is not None

    def test_history_not_available_when_admitted_students_domain(self, client, fake_auth):
        """The cohort history feature is not available if domain is 'admitted_students'."""
        fake_auth.login(ce3_advisor_uid)
        api_json = self._api_cohorts_by_dept_code(client, 'ZCEEE')
        cohorts = next(row['cohorts'] for row in api_json if len(row['cohorts']))
        api_cohort_events(client, cohorts[0]['id'], expected_status_code=400)


class TestCohortCreate:
    """Create Cohort API."""

    def test_create_cohort(self, client, fake_auth):
        """Creates custom cohort, owned by current user."""
        fake_auth.login(asc_advisor_uid)
        data = {
            'name': 'Tennis',
            'filters': [
                {'key': 'majors', 'value': 'Letters & Sci Undeclared UG'},
                {'key': 'groupCodes', 'value': 'MTE'},
                {'key': 'majors', 'value': 'English BA'},
            ],
        }

        def _verify(cohort):
            assert 'id' in cohort
            assert cohort.get('name') == 'Tennis'
            assert cohort['alertCount'] is not None
            assert len(cohort.get('criteria', {}).get('majors')) == 2
            # Students
            students = cohort.get('students')
            assert len(students) == 1
            assert students[0]['underrepresented'] is False

        api_json = api_cohort_create(client, data)
        _verify(api_json)
        cohort_id = api_json.get('id')
        _verify(api_get_cohort(client, cohort_id=cohort_id, include_students=True))

    def test_asc_advisor_is_forbidden(self, client, fake_auth):
        """Denies ASC advisor access to COE data."""
        fake_auth.login(asc_advisor_uid)
        data = {
            'name': 'ASC advisor wants to see students of COE advisor',
            'filters': [
                {'key': 'coeEthnicities', 'value': 'Vietnamese'},
            ],
        }
        api_cohort_create(client, data, expected_status_code=403)

    def test_create_complex_cohort(self, client, fake_auth):
        """Creates custom cohort, with many non-empty filter_criteria."""
        fake_auth.login(coe_advisor_uid)
        gpa_range_1 = {'min': 2, 'max': 2.499}
        gpa_range_2 = {'min': 0, 'max': 1.999}
        data = {
            'name': 'Complex',
            'filters': [
                {'key': 'majors', 'value': 'Gender and Womens Studies'},
                {'key': 'gpaRanges', 'value': gpa_range_1},
                {'key': 'levels', 'value': 'Junior'},
                {'key': 'gpaRanges', 'value': gpa_range_2},
                {'key': 'majors', 'value': 'Environmental Economics & Policy'},
                {'key': 'intendedMajors', 'value': 'Public Health BA'},
                {'key': 'intendedMajors', 'value': 'Mathematics'},
                {'key': 'minors', 'value': 'Physics UG'},
                {'key': 'subplans', 'value': 'Creative Writing'},
            ],
        }
        cohort = api_cohort_create(client, data)
        cohort_id = cohort['id']
        api_json = api_get_cohort(client, cohort_id)
        assert api_json['alertCount'] is not None
        criteria = api_json.get('criteria')
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
        assert 'Gender and Womens Studies' in majors
        # Minors
        minors = criteria.get('minors')
        assert len(minors) == 1
        assert 'Physics UG' in minors
        # Subplans
        subplans = criteria.get('subplans')
        assert len(subplans) == 1
        assert 'Creative Writing' in subplans

    def test_admin_creation_of_asc_cohort(self, client, fake_auth):
        """Admin can use ASC criteria."""
        fake_auth.login(admin_uid)
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

    def test_forbidden_cohort_creation(self, client, fake_auth):
        """COE advisor cannot use ASC criteria."""
        fake_auth.login(coe_advisor_uid)
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
            {'key': 'levels', 'value': 'Senior'},
        ],
    }

    def test_admin_intersecting_filters(self, client, fake_auth):
        """An admin can create a cohort using both ASC and COE criteria."""
        fake_auth.login(admin_uid)
        cohort = api_cohort_create(client, self._intersecting_filter_criteria)
        assert len(cohort['students']) == 1

    def test_multi_dept_intersecting_filters(self, client, fake_auth):
        """An advisor belonging to multiple departments can create a cohort using intersecting criteria."""
        fake_auth.login(asc_and_coe_advisor_uid)
        cohort = api_cohort_create(client, self._intersecting_filter_criteria)
        assert len(cohort['students']) == 1

    def test_single_dept_intersecting_filters_fails(self, client, fake_auth):
        """An advisor belonging to a single department cannot create a cohort using intersecting criteria."""
        fake_auth.login(coe_advisor_uid)
        api_cohort_create(client, self._intersecting_filter_criteria, expected_status_code=403)

    def test_academic_standing_cohort(self, client, fake_auth):
        """Find students per academic standing."""
        fake_auth.login(admin_uid)
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

    def test_active_students_cohort(self, client, fake_auth):
        """Cohort with active English majors only."""
        fake_auth.login(admin_uid)
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

    def test_completed_students_cohort(self, client, fake_auth):
        """Can find completed English majors on request."""
        fake_auth.login(admin_uid)
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

    def test_active_and_completed_students_cohort(self, client, fake_auth):
        """Can find active and completed English majors on request."""
        fake_auth.login(admin_uid)
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

    def test_inactive_students_cohort(self, client, fake_auth):
        """Can find inactive students on request."""
        fake_auth.login(admin_uid)
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
    """Update Cohort API."""

    @classmethod
    def _post_cohort_update(cls, client, json_data=()):
        return client.post(
            '/api/cohort/update',
            data=json.dumps(json_data),
            content_type='application/json',
        )

    def test_unauthorized_cohort_update(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
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
        assert response.status_code == 403

    def test_update_filters(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
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
        assert response.status_code == 400
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
        assert response.status_code == 200
        updated_cohort = response.json
        assert updated_cohort['alertCount'] is not None
        assert updated_cohort['criteria']['majors'] == ['Engineering Undeclared UG']
        assert updated_cohort['criteria']['gpaRanges'] == [gpa_range]
        assert updated_cohort['criteria'].get('groupCodes') is None

        def remove_empties(criteria):
            return {k: v for k, v in criteria.items() if v is not None}
        cohort = CohortFilter.find_by_id(cohort_id).to_api_json()
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

    def test_cohort_update_filter_criteria(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
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
        updated_cohort = CohortFilter.find_by_id(cohort_id).to_api_json()
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
    """Delete Cohort API."""

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

    def test_delete_cohort(self, client, fake_auth):
        """Deletes existing custom cohort while enforcing rules of ownership."""
        fake_auth.login(coe_advisor_uid)
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
    """Cohort per Filters API."""

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

    def test_students_per_filters_with_empty(self, client, fake_auth):
        """API requires non-empty input."""
        fake_auth.login(coe_advisor_uid)
        self._api_get_students_per_filters(client, {'filters': []}, expected_status_code=400)

    def test_students_per_filters_unauthorized(self, client, fake_auth):
        """ASC advisor is not allowed to query with COE attributes."""
        fake_auth.login(asc_advisor_uid)
        self._api_get_students_per_filters(
            client,
            {'filters': [{'key': 'coeAcademicStandings', 'value': ['N']}]},
            expected_status_code=403,
        )

    def test_students_per_ranges(self, client, fake_auth):
        """API translates range filters to proper filter_criteria query."""
        fake_auth.login(coe_advisor_uid)
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
        assert [s['lastName'] for s in students] == ['Doolittle', 'Farestveit', 'Jayaprakash', 'Kerschen']
        assert [s['cumulativeGPA'] for s in students] == [3.495, 3.9, 3.501, 3.005]
        criteria = api_json['criteria']
        assert len(criteria['gpaRanges']) == 2
        assert len(criteria['lastNameRanges']) == 1

    def test_my_students_filter_all_plans(self, client, fake_auth):
        """Returns students mapped to advisor, across all academic plans."""
        fake_auth.login(coe_advisor_uid)
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

    def test_my_students_filter_selected_plans(self, client, fake_auth):
        """Returns students mapped to advisor, per specified academic plans."""
        fake_auth.login(coe_advisor_uid)
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

    def test_students_per_filters_order_by(self, client, fake_auth):
        """Returns properly ordered list of students."""
        fake_auth.login(asc_advisor_uid)

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

    def test_student_athletes_inactive_asc(self, client, fake_auth):
        """An ASC advisor query defaults to active athletes only."""
        fake_auth.login(asc_advisor_uid)
        students = self._get_defensive_line(client, False, 'gpa')
        assert len(students) == 3
        for student in students:
            assert student['athleticsProfile']['isActiveAsc'] is True

    def test_student_athletes_inactive_admin(self, client, fake_auth):
        """An admin query defaults to active and inactive athletes."""
        fake_auth.login(admin_uid)
        students = self._get_defensive_line(client, None, 'gpa')
        assert len(students) == 4

        def is_active_asc(student):
            return student['athleticsProfile']['isActiveAsc']
        assert is_active_asc(students[0]) is False
        assert is_active_asc(students[1]) is True
        assert is_active_asc(students[2]) is True
        assert is_active_asc(students[3]) is True

    def test_filter_careers_graduate(self, client, fake_auth):
        """Cohort filter: Graduate careers."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'academicCareers', 'value': 'graduate'},
                ],
            },
        )
        students = api_json['students']
        assert len(students)
        for s in students:
            assert s['majors'][0].endswith('PhD')

    def test_filter_careers_undergraduate(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'academicCareers', 'value': 'undergraduate'},
                ],
            },
        )
        students = api_json['students']
        assert len(students)
        for s in students:
            assert s['majors'][0][-2:] in ('BA', 'BS', 'UG')

    def test_filter_careers_all(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_get_students_per_filters(
            client,
            {
                'filters': [
                    {'key': 'academicCareers', 'value': 'graduate'},
                    {'key': 'academicCareers', 'value': 'undergraduate'},
                ],
            },
        )
        students = api_json['students']
        assert len(students)
        for s in students:
            assert next(s for s in students if s['majors'][0].endswith('BA'))
            assert next(s for s in students if s['majors'][0].endswith('PhD'))

    def test_filter_colleges(self, client, fake_auth):
        """Cohort filter: Colleges."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_degree(self, client, fake_auth):
        """Cohort filter: Degree."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_degree_term(self, client, fake_auth):
        """Cohort filter: Degree terms."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_division(self, client, fake_auth):
        """Cohort filter: Academic division."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_entering_term(self, client, fake_auth):
        """Cohort filter: Entering term."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_graduate_program(self, client, fake_auth):
        """Cohort filter: Graduate Program."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_multiple_entering_terms(self, client, fake_auth):
        """Cohort filter: Multiple entering terms."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_expected_grad_term(self, client, fake_auth):
        """Returns students per expected graduation."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_transfer(self, client, fake_auth):
        """Returns list of transfer students."""
        fake_auth.login(coe_advisor_uid)
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

    def test_ethnicities_filter(self, client, fake_auth):
        """Returns students of specified ethnicity."""
        fake_auth.login(coe_advisor_uid)
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

    def test_incomplete_date_filter(self, client, fake_auth):
        """Cohort filter: Incomplete by date."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_get_students_per_filters(
            client,
            json_data={
                'filters': [
                    {'key': 'incompleteDateRanges', 'value': {'min': '2022-01-01', 'max': '2022-12-31'}},
                    {'key': 'academicCareerStatus', 'value': 'inactive'},
                ],
            },
        )
        sids = sorted([s['sid'] for s in api_json['students']])
        assert sids == ['3141592653']

    def test_incomplete_status_filter(self, client, fake_auth):
        """Cohort filter: Incomplete by status."""
        fake_auth.login(coe_advisor_uid)
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

    def test_midpoint_deficient_grade_filter(self, client, fake_auth):
        """Cohort filter: Midpoint deficient grade."""
        fake_auth.login(coe_advisor_uid)
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

    def test_last_term_gpa_filter(self, client, fake_auth):
        """Cohort filter: Last term GPA."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_visa_types(self, client, fake_auth):
        """Returns students with verified visa status and the specified visa type(s)."""
        fake_auth.login(coe_advisor_uid)
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

    def test_filter_visa_types_all(self, client, fake_auth):
        """Returns all students with verified visa status."""
        fake_auth.login(coe_advisor_uid)
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


def _new_undeclared_cohort(client):
    data = {
        'name': 'Nothing to Declare',
        'filters': [{'key': 'majors', 'value': 'Letters & Sci Undeclared UG'}],
    }
    cohort = api_cohort_create(client, data)
    cohort_id = cohort['id']
    return api_get_cohort(client, cohort_id, include_students=True)
