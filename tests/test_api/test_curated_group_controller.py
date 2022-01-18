"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.curated_group import CuratedGroup
import pytest
import simplejson as json
from tests.test_api.api_test_utils import api_curated_group_add_students, api_curated_group_remove_student
from tests.util import override_config

admin_uid = '2040'
asc_advisor_uid = '6446'
authorized_advisor_uid = '90412'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'
coe_scheduler_uid = '6972201'


@pytest.fixture()
def asc_advisor(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def authorized_advisor(fake_auth):
    fake_auth.login(authorized_advisor_uid)


@pytest.fixture()
def coe_advisor(fake_auth):
    fake_auth.login(coe_advisor_uid)


@pytest.fixture()
def coe_scheduler(fake_auth):
    fake_auth.login(coe_scheduler_uid)


@pytest.fixture()
def no_canvas_data_access_advisor(fake_auth):
    fake_auth.login('1')


@pytest.fixture()
def admin_user_session(fake_auth):
    fake_auth.login(admin_uid)


@pytest.fixture()
def admin_curated_groups():
    user = AuthorizedUser.find_by_uid(admin_uid)
    return CuratedGroup.get_curated_groups(user.id)


@pytest.fixture()
def asc_curated_groups():
    advisor = AuthorizedUser.find_by_uid(asc_advisor_uid)
    return CuratedGroup.get_curated_groups(advisor.id)


@pytest.fixture()
def coe_advisor_groups():
    advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
    return CuratedGroup.get_curated_groups(advisor.id)


class TestCreateCuratedGroup:

    def test_not_authenticated(self, client):
        """Reject anonymous user."""
        _api_curated_group_create(client, expected_status_code=401, name='The Awkward Age', sids=['5678901234'])

    def test_authorized(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        group = _api_curated_group_create(client, name='The Awkward Age', sids=['5678901234'])
        student_feed = _api_get_curated_group(client, group['id'])['students'][0]
        assert 'analytics' in student_feed['term']['enrollments'][0]['canvasSites'][0]

    def test_unauthorized(self, app, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            fake_auth.login(coe_advisor_uid)
            _api_curated_group_create(
                client=client,
                domain='admitted_students',
                expected_status_code=403,
                name="Ain't gonna happen",
                sids=['5678901234'],
            )

    def test_authorized_ce3(self, app, client, fake_auth):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            fake_auth.login(ce3_advisor_uid)
            sid = '11667051'
            group = _api_curated_group_create(
                client=client,
                domain='admitted_students',
                name='The domain of admitted_students',
                sids=[sid],
            )
            students = _api_get_curated_group(client, group['id'])['students']
            assert len(students) == 1
            assert 'applyucCpid' in students[0]
            assert students[0]['sid'] == sid
            assert students[0]['admitStatus'] == 'Yes'


class TestGetCuratedGroup:

    @staticmethod
    def _api_students_with_alerts(client, curated_group_id, expected_status_code=200):
        response = client.get(f'/api/curated_group/{curated_group_id}/students_with_alerts')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, asc_curated_groups, client):
        """Anonymous user is rejected."""
        _api_get_curated_group(client, asc_curated_groups[0].id, expected_status_code=401)

    def test_unauthorized(self, asc_curated_groups, coe_advisor, client):
        """403 if user does not share a department membership with group owner."""
        _api_get_curated_group(client, asc_curated_groups[0].id, expected_status_code=403)

    def test_advisor_cannot_see_admin_curated_group(self, admin_curated_groups, coe_advisor, client):
        """403 if user does not share a department membership with group owner."""
        _api_get_curated_group(client, admin_curated_groups[0].id, expected_status_code=403)

    def test_curated_group_includes_alert_count(self, asc_advisor, asc_curated_groups, client, create_alerts):
        """Includes alert count per student."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id)
        students = api_json.get('students')
        assert students
        for student in students:
            assert isinstance(student.get('alertCount'), int)
        student_with_alerts = next((s for s in students if s['sid'] == '11667051'), None)
        assert student_with_alerts
        assert student_with_alerts['alertCount'] == 4

    def test_curated_group_includes_term_gpa(self, asc_advisor, asc_curated_groups, client):
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id)
        students = api_json['students']
        deborah = next(s for s in students if s['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}

    def test_curated_group_includes_academic_standing(self, asc_advisor, asc_curated_groups, client):
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id)
        students = api_json['students']
        deborah = next(s for s in students if s['firstName'] == 'Deborah')
        assert deborah['academicStanding'] == {
            'actionDate': '2018-05-31',
            'status': 'GST',
            'termName': 'Spring 2018',
        }

    def test_view_permitted_shared_dept(self, asc_curated_groups, authorized_advisor, client):
        """Advisor can view group if they share the group owner's department memberships."""
        group = _api_get_curated_group(client, asc_curated_groups[0].id)
        assert group['students']
        response = client.get(f'/api/curated_group/{asc_curated_groups[0].id}/students_with_alerts')
        assert response.status_code == 200

    def test_curated_group_includes_students_without_alerts(
            self,
            asc_advisor,
            asc_curated_groups,
            client,
            create_alerts,
    ):
        """Includes students in response."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='first_name')
        last_names = [s.get('lastName') for s in api_json['students']]
        assert last_names == ['Davies', 'Farestveit', 'Kerschen', 'Jayaprakash']
        alert_counts = [s.get('alertCount') for s in api_json['students']]
        assert alert_counts == [4, 0, 1, 0]

    def test_order_by_level(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response, ordered by level."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='level', offset=1, limit=2)
        names = [f"{s.get('level')} ({s.get('lastName')})" for s in api_json['students']]
        assert names == ['Junior (Kerschen)', 'Senior (Farestveit)']

    def test_order_by_major(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response, ordered by major."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='major', offset=1)
        majors = [f"{s.get('majors')[0] if len(s.get('majors')) else None} ({s.get('lastName')})" for s in api_json['students']]
        assert majors == [
            'English BA (Kerschen)',
            'Letters & Sci Undeclared UG (Jayaprakash)',
            'Nuclear Engineering BS (Farestveit)',
        ]

    def test_order_by_gpa_desc(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response, ordered by cumulative GPA descending."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='gpa desc')
        gpas = [f"{s.get('cumulativeGPA')} ({s.get('lastName')})" for s in api_json['students']]
        assert gpas == [
            '3.9 (Farestveit)',
            '3.8 (Davies)',
            '3.501 (Jayaprakash)',
            '3.005 (Kerschen)',
        ]

    def test_order_by_term_gpa(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response, ordered by term GPA, nulls last."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='term_gpa_2178')

        def _fall_2017_gpa(student):
            return next((t['gpa'] for t in student['termGpa'] if t['termName'] == 'Fall 2017'), None) if student['termGpa'] else None
        gpas = [f"{_fall_2017_gpa(s)} ({s.get('lastName')})" for s in api_json['students']]
        assert gpas == [
            '1.8 (Davies)',
            '2.1 (Jayaprakash)',
            '3.2 (Kerschen)',
            'None (Farestveit)',
        ]

    def test_order_by_term_gpa_desc(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response, ordered by term GPA descending, nulls last."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='term_gpa_2178 desc')

        def _fall_2017_gpa(student):
            return next((t['gpa'] for t in student['termGpa'] if t['termName'] == 'Fall 2017'), None) if student['termGpa'] else None
        gpas = [f"{_fall_2017_gpa(s)} ({s.get('lastName')})" for s in api_json['students']]
        assert gpas == [
            '3.2 (Kerschen)',
            '2.1 (Jayaprakash)',
            '1.8 (Davies)',
            'None (Farestveit)',
        ]

    def test_order_by_units_enrolled(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response, ordered by units in progress, nulls first."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='enrolled_units')
        units = [f"{s['term'].get('enrolledUnits') if s.get('term') else None} ({s.get('lastName')})" for s in api_json['students']]
        assert units == [
            '5 (Kerschen)',
            '7 (Jayaprakash)',
            '12.5 (Davies)',
            'None (Farestveit)',
        ]

    def test_order_by_units_enrolled_desc(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response, ordered by units in progress descending, nulls last."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='enrolled_units desc')
        units = [f"{s['term'].get('enrolledUnits') if s.get('term') else None} ({s.get('lastName')})" for s in api_json['students']]
        assert units == [
            '12.5 (Davies)',
            '7 (Jayaprakash)',
            '5 (Kerschen)',
            'None (Farestveit)',
        ]

    def test_order_by_terms_in_attendance(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response, ordered by terms completed, nulls last."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='terms_in_attendance')
        units = [f"{s['termsInAttendance']} ({s.get('lastName')})" for s in api_json['students']]
        assert units == [
            '2 (Farestveit)',
            '5 (Kerschen)',
            'None (Davies)',
            'None (Jayaprakash)',
        ]

    def test_curated_group_detail_includes_profiles(self, asc_advisor, asc_curated_groups, client, create_alerts):
        """Returns all students with profile data."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id)
        student = api_json['students'][0]
        assert student['cumulativeGPA'] == 3.8
        assert student['cumulativeUnits'] == 101.3
        assert student['level'] == 'Junior'
        assert len(student['majors']) == 2

    def test_curated_group_detail_includes_athletics(self, asc_advisor, asc_curated_groups, client):
        """Returns athletics data, including intensive and inactive, for ASC advisors."""
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id)
        students = api_json['students']
        teams = students[0]['athleticsProfile']['athletics']
        assert len(teams) == 2
        assert teams[0]['name'] == 'Women\'s Field Hockey'
        assert teams[0]['groupCode'] == 'WFH'
        assert teams[1]['name'] == 'Women\'s Tennis'
        assert teams[1]['groupCode'] == 'WTE'
        assert students[0]['athleticsProfile']['inIntensiveCohort'] is True
        assert students[0]['athleticsProfile']['isActiveAsc'] is True
        assert students[0]['athleticsProfile']['statusAsc'] == 'Compete'

    def test_curated_group_detail_omits_athletics_non_asc(self, client, coe_advisor, coe_advisor_groups):
        """Returns team memberships only for non-ASC advisors."""
        api_json = _api_get_curated_group(client, coe_advisor_groups[0].id)
        student = api_json['students'][0]
        assert len(student['athleticsProfile']['athletics']) == 1
        assert 'inIntensiveCohort' not in student['athleticsProfile']
        assert 'isActiveAsc' not in student['athleticsProfile']
        assert 'statusAsc' not in student['athleticsProfile']

    def test_curated_group_detail_includes_current_enrollments(self, asc_advisor, asc_curated_groups, client):
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='first_name')
        student_term = api_json['students'][0]['term']
        assert student_term['termName'] == 'Fall 2017'
        assert student_term['enrolledUnits'] == 12.5
        assert len(student_term['enrollments']) == 5
        assert student_term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(student_term['enrollments'][0]['canvasSites']) == 1

    def test_curated_group_detail_includes_past_enrollments(self, asc_advisor, asc_curated_groups, client):
        api_json = _api_get_curated_group(client, asc_curated_groups[0].id, order_by='first_name', term_id='2172')
        student_term = api_json['students'][0]['term']
        assert student_term['termName'] == 'Spring 2017'
        assert student_term['enrolledUnits'] == 10.0
        assert len(student_term['enrollments']) == 3
        assert student_term['enrollments'][0]['displayName'] == 'CLASSIC 130 LEC 001'
        assert student_term['enrollments'][0]['grade'] == 'P'

    def test_curated_group_detail_suppresses_canvas_data_when_unauthorized(self, client, no_canvas_data_access_advisor):
        group = _api_curated_group_create(client, name='The Awkward Age', sids=['5678901234'])
        student_feed = _api_get_curated_group(client, group['id'])['students'][0]
        assert student_feed['term']['enrollments'][0]['canvasSites'] == []

    def test_students_with_alerts(self, asc_advisor, asc_curated_groups, client, create_alerts, db_session):
        """Students with alerts per group id."""
        api_json = self._api_students_with_alerts(client, asc_curated_groups[0].id)
        assert len(api_json) == 2
        assert api_json[0]['alertCount'] == 4
        assert api_json[1]['alertCount'] == 1

        student = client.get('/api/student/by_uid/61889').json
        alert_to_dismiss = student['notifications']['alert'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        students_with_alerts = client.get(f'/api/curated_group/{asc_curated_groups[0].id}/students_with_alerts').json
        assert students_with_alerts[0]['alertCount'] == 3

    def test_group_includes_student_summary(self, asc_advisor, asc_curated_groups, client, create_alerts):
        """Returns summary details but not full term and analytics data."""
        api_json = self._api_students_with_alerts(client, asc_curated_groups[0].id)
        assert api_json[0]['academicStanding']['status'] == 'GST'
        assert api_json[0]['cumulativeGPA'] == 3.8
        assert api_json[0]['cumulativeUnits'] == 101.3
        assert api_json[0]['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert api_json[0]['level'] == 'Junior'
        assert api_json[0]['termGpa'][0]['gpa'] == 2.9
        assert len(api_json[0]['majors']) == 2

    def test_curated_groups_all(self, authorized_advisor, client):
        """Returns all groups to which user has viewing access, per owner."""
        response = client.get('/api/curated_groups/all')
        assert response.status_code == 200
        api_json = response.json
        count = len(api_json)
        for index, entry in enumerate(api_json):
            user = entry['user']
            if 0 < index < count and user['name'] and api_json[index - 1]['user']['name']:
                # Verify order
                assert user['name'] > api_json[index - 1]['user']['name']
            if user['uid'] == asc_advisor_uid or user['uid'] == coe_advisor_uid:
                assert len(entry['groups'])
                assert entry['groups'][0]['domain'] == 'default'
                assert entry['groups'][0]['name']
                assert entry['groups'][0]['totalStudentCount']


class TestAddStudents:

    def test_not_authenticated(self, asc_curated_groups, client):
        """Anonymous user is rejected."""
        assert api_curated_group_add_students(client, asc_curated_groups[0].id, expected_status_code=401, sids=['2345678901'])

    def test_unauthorized(self, asc_curated_groups, admin_user_session, client):
        """403 if user does not own the group."""
        assert api_curated_group_add_students(client, asc_curated_groups[0].id, expected_status_code=403, sids=['2345678901'])

    def test_add_student(self, asc_advisor, client):
        """Create a group and add a student."""
        group_name = 'Trams of Old London'
        group = _api_curated_group_create(client, name=group_name)
        assert group['totalStudentCount'] == 0
        sid = '2345678901'
        updated_group = api_curated_group_add_students(client, group['id'], sids=[sid])
        assert updated_group['name'] == group_name
        assert updated_group['totalStudentCount'] == 1
        assert updated_group['sids'] == [sid]

    def test_add_students(self, asc_advisor, client):
        """Create group and add students."""
        name = 'Cheap Tricks'
        group = _api_curated_group_create(client, name=name, sids=['2345678901', '11667051'])
        assert group['name'] == name
        assert group['totalStudentCount'] == 2
        # Add students
        updated_group = api_curated_group_add_students(
            client,
            group['id'],
            return_student_profiles=True,
            sids=['7890123456'],
        )
        assert updated_group['totalStudentCount'] == 3
        students = updated_group['students']
        sids = [s['sid'] for s in students]
        assert sids == ['11667051', '2345678901', '7890123456']
        # Add more and ask for FULL student profiles in payload
        updated_group = api_curated_group_add_students(
            client,
            group['id'],
            return_student_profiles=True,
            sids=['890127492', '8901234567'],
        )
        assert updated_group['totalStudentCount'] == 5
        students = updated_group['students']
        students.sort(key=lambda s: s['sid'])
        student = students[0]
        assert student['sid'] == '11667051'
        assert student['canvasUserId'] == '9000100'
        for expected_key in ('academicStanding', 'cumulativeGPA', 'cumulativeGPA', 'cumulativeUnits', 'majors', 'termGpa'):
            assert expected_key in student, f'Failed to find {expected_key} in student'


class TestRemoveStudent:
    """Curated Group API."""

    def test_not_authenticated(self, asc_curated_groups, client):
        """Anonymous user is rejected."""
        api_curated_group_remove_student(client, asc_curated_groups[0].id, '2345678901', expected_status_code=401)

    def test_unauthorized(self, asc_curated_groups, admin_user_session, client):
        """403 if user does not own the group."""
        api_curated_group_remove_student(client, asc_curated_groups[0].id, '2345678901', expected_status_code=403)

    def test_remove_student(self, asc_advisor, client):
        """Remove student from a curated group."""
        name = 'Furry Green Atom Bowl'
        sid = '2345678901'
        curated_group = _api_curated_group_create(client, name=name)
        curated_group_id = curated_group['id']
        curated_group = api_curated_group_add_students(client, curated_group_id, sids=[sid])
        assert curated_group['sids'] == [sid]
        assert curated_group['totalStudentCount'] == 1
        # Remove the SID
        curated_group = api_curated_group_remove_student(client, curated_group_id, sid)
        assert curated_group['totalStudentCount'] == 0


class TestUpdateCuratedGroup:
    """Curated Group API."""

    def test_rename_group(self, asc_advisor, client):
        """Rename curated group."""
        group = _api_curated_group_create(client, name='The Bones In The Ground')
        new_name = 'My Favourite Buildings'
        group_id = group['id']
        response = client.post(
            '/api/curated_group/rename',
            data=json.dumps({
                'id': group_id,
                'name': new_name,
            }),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert client.get(f'/api/curated_group/{group_id}').json['name'] == new_name


class TestDeleteCuratedGroup:
    """Curated Group API."""

    def test_not_authenticated(self, asc_curated_groups, client):
        """Anonymous user is rejected."""
        response = client.delete(f'/api/curated_group/delete/{asc_curated_groups[0].id}')
        assert response.status_code == 401

    def test_unauthorized(self, asc_curated_groups, admin_user_session, client):
        """403 if user does not own the group."""
        response = client.delete(f'/api/curated_group/delete/{asc_curated_groups[0].id}')
        assert response.status_code == 403

    def test_delete_group(self, asc_advisor, client):
        """Delete curated group."""
        group = _api_curated_group_create(client, name='Mellow Together')
        group_id = group['id']
        assert client.delete(f'/api/curated_group/delete/{group_id}').status_code == 200
        assert client.get(f'/api/curated_group/{group_id}').status_code == 404


class TestCuratedGroupWithInactives:

    active_sid = '2345678901'
    inactive_sid = '3141592653'
    completed_sid = '2718281828'

    def test_create_group_with_inactives(self, asc_advisor, client):
        group = _api_curated_group_create(
            client=client,
            name="Brenda's Iron Sledge",
            sids=[self.active_sid, self.inactive_sid, self.completed_sid],
        )
        group_id = group['id']
        assert group['totalStudentCount'] == 3
        assert len(group['students']) == 3
        sids = [r['sid'] for r in group['students']]
        assert self.active_sid in sids
        assert self.inactive_sid in sids
        assert self.completed_sid in sids

        group_feed = client.get(f'/api/curated_group/{group_id}').json
        assert group_feed['totalStudentCount'] == 3
        assert len(group_feed['students']) == 3
        assert group_feed['students'][0]['sid'] == self.inactive_sid
        assert group_feed['students'][0]['academicCareerStatus'] == 'Inactive'
        assert group_feed['students'][2]['sid'] == self.completed_sid
        assert group_feed['students'][2]['academicCareerStatus'] == 'Completed'
        assert group_feed['students'][2]['degrees'][0]['dateAwarded'] == '2010-05-14'
        assert group_feed['students'][2]['degrees'][0]['description'] == 'Doctor of Philosophy'

    def test_add_inactive_to_group(self, asc_advisor, client):
        group = _api_curated_group_create(
            client=client,
            name='Listening to the Higsons',
            sids=[self.active_sid],
        )
        assert group['totalStudentCount'] == 1
        updated_group = api_curated_group_add_students(
            client,
            group['id'],
            return_student_profiles=True,
            sids=[self.inactive_sid],
        )
        assert updated_group['totalStudentCount'] == 2
        assert updated_group['students'][1]['sid'] == self.active_sid
        assert updated_group['students'][0]['sid'] == self.inactive_sid


class TestDownloadCuratedGroupCSV:
    """Download Curated Group CSV API."""

    def test_download_csv_not_authenticated(self, asc_curated_groups, client):
        """Anonymous user is rejected."""
        data = {
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
            ],
        }
        response = client.post(
            f'/api/curated_group/{asc_curated_groups[0].id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 401

    def test_download_csv_unauthorized(self, asc_curated_groups, coe_advisor, client):
        """403 if user does not share a department membership with group owner."""
        data = {
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
            ],
        }
        response = client.post(
            f'/api/curated_group/{asc_curated_groups[0].id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 403

    def test_download_admits_csv(self, app, client, fake_auth):
        """Advisor can download CSV of 'admits' group."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            fake_auth.login(ce3_advisor_uid)
            curated_group = _api_curated_group_create(
                client=client,
                domain='admitted_students',
                name='Admits, curated',
                sids=['11667051'],
            )
            curated_group_id = curated_group['id']
            students = _api_get_curated_group(client, curated_group_id)['students']
            assert len(students) == 1
            data = {
                'csvColumnsSelected': [
                    'act_composite',
                    'birthdate',
                    'citizenship_country',
                    'family_dependents_num',
                    'gender_identity',
                    'highest_parent_education_level',
                    'non_immigrant_visa_current',
                    'xethnic',
                ],
            }
            response = client.post(
                f'/api/curated_group/{curated_group_id}/download_csv',
                data=json.dumps(data),
                content_type='application/json',
            )
            assert response.status_code == 200
            assert 'csv' in response.content_type
            csv = str(response.data)
            for snippet in [
                'act_composite,birthdate,citizenship_country,family_dependents_num,gender_identity,highest_parent_education_level,non_immigrant_visa_current,xethnic',  # noqa: E501
                '5,1985-06-02,Greece,05,Male,5 - College Attended,,NotSpecified',
            ]:
                assert str(snippet) in csv

    def test_download_csv(self, asc_advisor, asc_curated_groups, client):
        """Advisor can download CSV with ALL students of group."""
        data = {
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
                'cumulative_gpa',
                'program_status',
            ],
        }
        curated_group = next((g for g in asc_curated_groups if g.name == 'Four students'), None)
        assert curated_group
        response = client.post(
            f'/api/curated_group/{curated_group.id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = str(response.data)
        for snippet in [
            'first_name,last_name,sid,email,phone,majors,level_by_units,terms_in_attendance,expected_graduation_term,units_completed,term_gpa_2172,cumulative_gpa,program_status',  # noqa: E501
            'Deborah,Davies,11667051,barnburner@berkeley.edu,415/123-4567,English BA;Nuclear Engineering BS,Junior,,Fall 2019,101.3,2.700,3.8,Active',
            'Pauline,Kerschen,3456789012,doctork@berkeley.edu,415/123-4567,English BA;Political Economy BA,Junior,5,Fall 2019,70,,3.005,Active',
            'Sandeep,Jayaprakash,5678901234,ilovela@berkeley.edu,415/123-4567,Letters & Sci Undeclared UG,Senior,,Fall 2019,102,,3.501,Active',
            'Paul,Farestveit,7890123456,qadept@berkeley.edu,415/123-4567,Nuclear Engineering BS,Senior,2,Spring 2020,110,,3.9,Active',
        ]:
            assert str(snippet) in csv

    def test_download_csv_shared_dept(self, asc_curated_groups, authorized_advisor, client):
        """Advisor can download CSV if they share the group owner's department memberships."""
        data = {
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
            ],
        }
        curated_group = next((g for g in asc_curated_groups if g.name == 'Four students'), None)
        assert curated_group
        response = client.post(
            f'/api/curated_group/{curated_group.id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type

    def test_download_csv_custom_columns(self, asc_advisor, asc_curated_groups, client):
        """Advisor can generate a CSV with the columns they want."""
        data = {
            'csvColumnsSelected': [
                'majors',
                'level_by_units',
                'terms_in_attendance',
                'expected_graduation_term',
                'units_completed',
                'term_gpa_2175',
                'cumulative_gpa',
                'program_status',
            ],
        }
        curated_group = next((g for g in asc_curated_groups if g.name == 'Four students'), None)
        assert curated_group
        response = client.post(
            f'/api/curated_group/{curated_group.id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = str(response.data)
        for snippet in [
            'majors,level_by_units,terms_in_attendance,expected_graduation_term,units_completed,term_gpa_2175,cumulative_gpa,program_status',  # noqa: E501
            'English BA;Nuclear Engineering BS,Junior,,Fall 2019,101.3,,3.8,Active',
            'English BA;Political Economy BA,Junior,5,Fall 2019,70,,3.005,Active',
            'Letters & Sci Undeclared UG,Senior,,Fall 2019,102,,3.501,Active',
            'Nuclear Engineering BS,Senior,2,Spring 2020,110,,3.9,Active',
        ]:
            assert str(snippet) in csv


def _api_curated_group_create(client, expected_status_code=200, domain='default', name=None, sids=()):
    response = client.post(
        '/api/curated_group/create',
        data=json.dumps({
            'domain': domain,
            'name': name,
            'sids': sids,
        }),
        content_type='application/json',
    )
    std_commit(allow_test_environment=True)
    assert response.status_code == expected_status_code
    return response.json


def _api_get_curated_group(
    client,
    curated_group_id,
    expected_status_code=200,
    limit=50,
    offset=0,
    order_by='last_name',
    term_id='2178',
):
    response = client.get(f'/api/curated_group/{curated_group_id}?offset={offset}&limit={limit}&orderBy={order_by}&termId={term_id}')
    assert response.status_code == expected_status_code
    return response.json
