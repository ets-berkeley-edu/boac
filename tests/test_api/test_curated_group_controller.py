"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.curated_group import CuratedGroup, CuratedGroupStudent
import pytest
import simplejson as json


admin_uid = '2040'
asc_advisor_uid = '6446'
coe_advisor_uid = '1133399'


@pytest.fixture()
def asc_advisor(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor(fake_auth):
    fake_auth.login(coe_advisor_uid)


@pytest.fixture()
def admin_user_session(fake_auth):
    fake_auth.login(admin_uid)


@pytest.fixture()
def asc_curated_groups():
    advisor = AuthorizedUser.find_by_uid(asc_advisor_uid)
    return CuratedGroup.get_curated_groups_by_owner_id(advisor.id)


@pytest.fixture()
def coe_advisor_groups():
    advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
    return CuratedGroup.get_curated_groups_by_owner_id(advisor.id)


class TestGetCuratedGroup:
    """Curated Group API."""

    @staticmethod
    def _api_get_curated_group(
            client,
            curated_group_id,
            order_by='last_name',
            offset=0,
            limit=50,
            expected_status_code=200,
    ):
        response = client.get(f'/api/curated_group/{curated_group_id}?offset={offset}&limit={limit}&orderBy={order_by}')
        assert response.status_code == expected_status_code
        return response.json

    @staticmethod
    def _api_students_with_alerts(client, curated_group_id, expected_status_code=200):
        response = client.get(f'/api/curated_group/{curated_group_id}/students_with_alerts')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, asc_curated_groups, client):
        """Anonymous user is rejected."""
        self._api_get_curated_group(client, asc_curated_groups[0].id, expected_status_code=401)

    def test_unauthorized(self, asc_curated_groups, admin_user_session, client):
        """403 if user does not own the group."""
        self._api_get_curated_group(client, asc_curated_groups[0].id, expected_status_code=403)

    def test_curated_group_includes_alert_count(self, asc_advisor, asc_curated_groups, client, create_alerts):
        """Includes alert count per student."""
        api_json = self._api_get_curated_group(client, asc_curated_groups[0].id)
        students = api_json.get('students')
        assert students
        for student in students:
            assert isinstance(student.get('alertCount'), int)
        student_with_alerts = next((s for s in students if s['sid'] == '11667051'), None)
        assert student_with_alerts
        assert student_with_alerts['alertCount'] == 3

    def test_curated_group_includes_term_gpa(self, asc_advisor, asc_curated_groups, client):
        api_json = self._api_get_curated_group(client, asc_curated_groups[0].id)
        students = api_json['students']
        deborah = next(s for s in students if s['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}

    def test_curated_group_includes_students_without_alerts(
            self,
            asc_advisor,
            asc_curated_groups,
            client,
            create_alerts,
    ):
        """Includes students in response."""
        api_json = self._api_get_curated_group(client, asc_curated_groups[0].id, order_by='first_name')
        last_names = [s.get('lastName') for s in api_json['students']]
        assert last_names == ['Davies', 'Farestveit', 'Kerschen', 'Jayaprakash']
        alert_counts = [s.get('alertCount') for s in api_json['students']]
        assert alert_counts == [3, 0, 1, 0]

    def test_order_by_level(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response."""
        api_json = self._api_get_curated_group(client, asc_curated_groups[0].id, order_by='level', offset=1, limit=2)
        names = [f"{s.get('level')} ({s.get('lastName')})" for s in api_json['students']]
        assert names == ['Junior (Kerschen)', 'Senior (Farestveit)']

    def test_order_by_major(self, asc_advisor, asc_curated_groups, client):
        """Includes students in response."""
        api_json = self._api_get_curated_group(client, asc_curated_groups[0].id, order_by='major', offset=1)
        majors = [f"{s.get('majors')[0]} ({s.get('lastName')})" for s in api_json['students']]
        assert majors == [
            'English BA (Kerschen)',
            'Letters & Sci Undeclared UG (Jayaprakash)',
            'Nuclear Engineering BS (Farestveit)',
        ]

    def test_curated_group_detail_includes_analytics(self, asc_advisor, asc_curated_groups, client, create_alerts):
        """Returns all students with full term and analytics data."""
        api_json = self._api_get_curated_group(client, asc_curated_groups[0].id)
        student = api_json['students'][0]
        assert student['cumulativeGPA'] == 3.8
        assert student['cumulativeUnits'] == 101.3
        assert student['level'] == 'Junior'
        assert len(student['majors']) == 2
        assert 'analytics' in student

    def test_curated_group_detail_includes_athletics(self, asc_advisor, asc_curated_groups, client):
        """Returns student athletes."""
        api_json = self._api_get_curated_group(client, asc_curated_groups[0].id)
        students = api_json['students']
        teams = students[0]['athleticsProfile']['athletics']
        assert len(teams) == 2
        assert teams[0]['name'] == 'Women\'s Field Hockey'
        assert teams[0]['groupCode'] == 'WFH'
        assert teams[1]['name'] == 'Women\'s Tennis'
        assert teams[1]['groupCode'] == 'WTE'

    def test_curated_group_detail_omits_athletics_non_asc(self, client, coe_advisor, coe_advisor_groups):
        """Omits student athletes from COE group."""
        api_json = self._api_get_curated_group(client, coe_advisor_groups[0].id)
        assert 'athleticsProfile' not in api_json['students'][0]

    def test_students_with_alerts(self, asc_advisor, asc_curated_groups, client, create_alerts, db_session):
        """Students with alerts per group id."""
        api_json = self._api_students_with_alerts(client, asc_curated_groups[0].id)
        assert len(api_json) == 2
        assert api_json[0]['alertCount'] == 3
        assert api_json[1]['alertCount'] == 1

        student = client.get('/api/student/61889').json
        alert_to_dismiss = student['notifications']['alert'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        students_with_alerts = client.get(f'/api/curated_group/{asc_curated_groups[0].id}/students_with_alerts').json
        assert students_with_alerts[0]['alertCount'] == 2

    def test_group_includes_student_summary(self, asc_advisor, asc_curated_groups, client, create_alerts):
        """Returns summary details but not full term and analytics data."""
        api_json = self._api_students_with_alerts(client, asc_curated_groups[0].id)
        assert api_json[0]['cumulativeGPA'] == 3.8
        assert api_json[0]['cumulativeUnits'] == 101.3
        assert api_json[0]['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert api_json[0]['level'] == 'Junior'
        assert api_json[0]['termGpa'][0]['gpa'] == 2.9
        assert len(api_json[0]['majors']) == 2


class TestMyCuratedGroups:
    """Curated Group API."""

    @staticmethod
    def _api_my_curated_groups(client, expected_status_code=200):
        response = client.get('/api/curated_groups/my')
        assert response.status_code == expected_status_code
        return response.json

    @staticmethod
    def _api_my_curated_groups_by_sid(client, sid, expected_status_code=200):
        response = client.get(f'/api/curated_groups/my/{sid}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Anonymous user is rejected."""
        self._api_my_curated_groups(client, expected_status_code=401)

    def test_excludes_sids_per_advisor_access_privileges(self, client, create_alerts, fake_auth):
        """Excludes SIDs in curated-group view based on advisor's access privileges."""
        advisor_uid = '1081940'
        fake_auth.login(advisor_uid)
        curated_group = CuratedGroup.create(
            owner_id=AuthorizedUser.find_by_uid(advisor_uid).id,
            name='Four ASC students, one COE student',
        )
        CuratedGroup.add_student(curated_group.id, '3456789012')
        CuratedGroup.add_student(curated_group.id, '5678901234')
        CuratedGroup.add_student(curated_group.id, '11667051')
        CuratedGroup.add_student(curated_group.id, '7890123456')
        # TODO: When the BOA business rules change and all advisors have access to all students
        #  then the following SID will be served to the ASC advisor who owns the group. See BOAC-2130
        coe_student_sid = '9000000000'
        CuratedGroup.add_student(curated_group.id, coe_student_sid)

        actual_student_count = len(CuratedGroupStudent.get_sids(curated_group_id=curated_group.id))
        assert actual_student_count == 5
        expected_student_count = 4

        response = client.get(f'/api/curated_group/{curated_group.id}')
        assert response.status_code == 200
        assert len(response.json['students']) == expected_student_count
        # Adjusted student count should be consistent across the curated_group API
        api_json = self._api_my_curated_groups(client)
        group = next((g for g in api_json if g['id'] == curated_group.id), None)
        assert group['studentCount'] == expected_student_count
        # Group by id
        response = client.get(f'/api/curated_group/{curated_group.id}')
        assert response.status_code == 200
        assert response.json['studentCount'] == expected_student_count
        # Group with alerts
        response = client.get(f'/api/curated_group/{curated_group.id}/students_with_alerts')
        assert response.status_code == 200
        assert not next((s for s in response.json if s['sid'] == coe_student_sid), None)

    def test_coe_curated_groups(self, client, coe_advisor):
        """Returns curated groups of COE advisor."""
        api_json = self._api_my_curated_groups(client)
        assert len(api_json) == 1
        group = api_json[0]
        assert 'id' in group
        assert 'alertCount' in group
        assert 'studentCount' in group
        assert group['name'] == 'I have one student'

    def test_asc_curated_groups(self, asc_advisor, client):
        """Returns curated groups of ASC advisor."""
        api_json = self._api_my_curated_groups(client)
        group = api_json[0]
        assert group['name'] == 'Four students'
        assert group['studentCount'] == 4

    def test_not_authenticated_curated_groups_by_sid(self, client):
        """Anonymous user is rejected."""
        assert self._api_my_curated_groups_by_sid(client, sid='7890123456', expected_status_code=401)

    def test_curated_groups_by_sid(self, client, coe_advisor, coe_advisor_groups):
        """API delivers accurate set of student SIDs."""
        sids = CuratedGroup.get_all_sids(curated_group_id=coe_advisor_groups[0].id)
        sample_sid = sids[0]
        assert self._api_my_curated_groups_by_sid(client, sid=sample_sid) == [coe_advisor_groups[0].id]


class TestAddStudents:
    """Curated Group API."""

    @staticmethod
    def _api_add_students(client, curated_group_id, expected_status_code=200, return_student_profiles=False, sids=()):
        response = client.post(
            '/api/curated_group/students/add',
            data=json.dumps({
                'curatedGroupId': curated_group_id,
                'returnStudentProfiles': return_student_profiles,
                'sids': sids,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, asc_curated_groups, client):
        """Anonymous user is rejected."""
        assert self._api_add_students(client, asc_curated_groups[0].id, expected_status_code=401, sids=['2345678901'])

    def test_unauthorized(self, asc_curated_groups, admin_user_session, client):
        """403 if user does not own the group."""
        assert self._api_add_students(client, asc_curated_groups[0].id, expected_status_code=403, sids=['2345678901'])

    def test_add_student(self, asc_advisor, client):
        """Create a group and add a student."""
        group_name = 'Trams of Old London'
        group = _api_create_group(client, name=group_name)
        assert group['studentCount'] == 0
        sid = '2345678901'
        updated_group = self._api_add_students(client, group['id'], sids=[sid])
        assert updated_group['name'] == group_name
        assert updated_group['studentCount'] == 1
        assert updated_group['students'][0]['sid'] == sid

    def test_add_students(self, asc_advisor, client):
        """Create group and add students."""
        name = 'Cheap Tricks'
        group = _api_create_group(client, name=name, sids=['2345678901', '11667051'])
        assert group['name'] == name
        assert group['studentCount'] == 2
        # Add students
        updated_group = self._api_add_students(
            client,
            group['id'],
            return_student_profiles=True,
            sids=['7890123456'],
        )
        assert updated_group['studentCount'] == 3
        students = updated_group['students']
        sids = [s['sid'] for s in students]
        assert sids == ['11667051', '2345678901', '7890123456']
        # Add more and ask for FULL student profiles in payload
        updated_group = self._api_add_students(
            client,
            group['id'],
            return_student_profiles=True,
            sids=['890127492', '8901234567'],
        )
        assert updated_group['studentCount'] == 5
        students = updated_group['students']
        students.sort(key=lambda s: s['sid'])
        student = students[0]
        assert student['sid'] == '11667051'
        assert student['canvasUserId'] == '9000100'
        for expected_key in ('cumulativeGPA', 'cumulativeGPA', 'cumulativeUnits', 'majors', 'termGpa'):
            assert expected_key in student, f'Failed to find {expected_key} in student'


class TestRemoveStudent:
    """Curated Group API."""

    def test_not_authenticated(self, asc_curated_groups, client):
        """Anonymous user is rejected."""
        response = client.delete(f'/api/curated_group/{asc_curated_groups[0].id}/remove_student/2345678901')
        assert response.status_code == 401

    def test_unauthorized(self, asc_curated_groups, admin_user_session, client):
        """403 if user does not own the group."""
        response = client.delete(f'/api/curated_group/{asc_curated_groups[0].id}/remove_student/2345678901')
        assert response.status_code == 403

    def test_remove_student(self, asc_advisor, client):
        """Remove student from a curated group."""
        name = 'Furry Green Atom Bowl'
        group = _api_create_group(client, name=name)
        group_id = group['id']
        sid = '2345678901'
        response = client.post(
            '/api/curated_group/students/add',
            data=json.dumps({'curatedGroupId': group_id, 'sids': [sid]}),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.json['name'] == name
        assert response.json['studentCount'] == 1
        response = client.delete(f'/api/curated_group/{group_id}/remove_student/{sid}')
        assert response.status_code == 200
        empty_group = response.json
        assert empty_group['name'] == name
        assert empty_group['studentCount'] == 0


class TestUpdateCuratedGroup:
    """Curated Group API."""

    def test_rename_group(self, asc_advisor, client):
        """Rename curated group."""
        group = _api_create_group(client, name='The Bones In The Ground')
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

    def test_delete_group(self, asc_advisor, client):
        """Delete curated group."""
        group = _api_create_group(client, name='Mellow Together')
        group_id = group['id']
        assert client.delete(f'/api/curated_group/delete/{group_id}').status_code == 200
        assert client.get(f'/api/curated_group/{group_id}').status_code == 404


def _api_create_group(client, expected_status_code=200, name=None, sids=()):
    response = client.post(
        '/api/curated_group/create',
        data=json.dumps({
            'name': name,
            'sids': sids,
        }),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json
