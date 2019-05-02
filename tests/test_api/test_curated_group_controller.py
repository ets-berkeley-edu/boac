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
from boac.models.curated_group import CuratedGroup
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
def asc_curated_group():
    advisor = AuthorizedUser.find_by_uid(asc_advisor_uid)
    name = 'Curated group with four ASC students and one student from COE'
    groups = CuratedGroup.get_curated_groups_by_owner_id(advisor.id)
    return next((g for g in groups if g.name == name), None)


@pytest.fixture()
def coe_advisor_group():
    advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
    return CuratedGroup.get_curated_groups_by_owner_id(advisor.id)[0]


class TestGetCuratedGroup:
    """Curated Group API."""

    def test_not_authenticated(self, client):
        """Anonymous user is rejected."""
        assert client.get('/api/curated_groups/my').status_code == 401

    def test_unauthorized(self, asc_curated_group, admin_user_session, client):
        """403 if user does not own the group."""
        assert client.get(f'/api/curated_group/{asc_curated_group.id}').status_code == 403

    def test_coe_curated_groups(self, client, coe_advisor):
        """Returns curated groups of COE advisor."""
        response = client.get('/api/curated_groups/my')
        assert response.status_code == 200
        groups = response.json
        assert len(groups) == 1
        group = groups[0]
        assert 'id' in group
        assert 'alertCount' in group
        assert 'studentCount' in group
        assert group['name'] == 'I have one student'

    def test_asc_curated_groups(self, client, fake_auth):
        """Returns curated groups of ASC advisor."""
        fake_auth.login(asc_advisor_uid)
        response = client.get('/api/curated_groups/my')
        assert response.status_code == 200
        groups = response.json
        assert len(groups) == 2
        assert 'name' in groups[0]
        assert 'studentCount' in groups[0]

    def test_curated_group_includes_alert_count(self, asc_advisor, asc_curated_group, client, create_alerts):
        """Includes alert count per student."""
        response = client.get(f'/api/curated_group/{asc_curated_group.id}')
        students = response.json.get('students')
        assert students
        for student in students:
            assert isinstance(student.get('alertCount'), int)
        student_with_alerts = next((s for s in students if s['sid'] == '11667051'), None)
        assert student_with_alerts
        assert student_with_alerts['alertCount'] == 3

    def test_curated_group_includes_term_gpas(self, asc_advisor, asc_curated_group, client):
        students = client.get(f'/api/curated_group/{asc_curated_group.id}').json['students']
        deborah = next(s for s in students if s['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}


class TestMyCuratedGroups:
    """Curated Group API."""

    def test_students_without_alerts(self, asc_advisor, asc_curated_group, client, create_alerts, db_session):
        """Students with alerts per group id."""
        students_with_alerts = client.get(f'/api/curated_group/{asc_curated_group.id}/students_with_alerts').json
        assert len(students_with_alerts) == 2
        assert students_with_alerts[0]['alertCount'] == 3

        student = client.get('/api/student/61889').json
        alert_to_dismiss = student['notifications']['alert'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        students_with_alerts = client.get(f'/api/curated_group/{asc_curated_group.id}/students_with_alerts').json
        assert students_with_alerts[0]['alertCount'] == 2

    def test_curated_group_detail_includes_students_without_alerts(
            self,
            asc_advisor,
            asc_curated_group,
            client,
            create_alerts,
    ):
        """Includes students in response."""
        group = client.get(f'/api/curated_group/{asc_curated_group.id}').json
        alert_counts = [s.get('alertCount') for s in group['students']]
        assert alert_counts == [3, 0, 0, 1]

    def test_excludes_sids_per_advisor_access_privileges(self, asc_advisor, asc_curated_group, client, create_alerts):
        """Excludes SIDs in curated-group view based on advisor's access privileges."""
        actual_student_count = len(asc_curated_group.students)
        assert actual_student_count == 5
        expected_student_count = 4
        coe_student_sid = '9000000000'

        group = client.get(f'/api/curated_group/{asc_curated_group.id}').json
        assert len(group['students']) == expected_student_count
        # Adjusted student count should be consistent across the curated_group API
        my_groups = client.get('/api/curated_groups/my').json
        group = next((g for g in my_groups if g['id'] == asc_curated_group.id), None)
        assert group['studentCount'] == expected_student_count
        # Group by id
        group = client.get(f'/api/curated_group/{asc_curated_group.id}').json
        assert group['studentCount'] == expected_student_count
        # Group with alerts
        students = client.get(f'/api/curated_group/{asc_curated_group.id}/students_with_alerts').json
        assert not next((s for s in students if s['sid'] == coe_student_sid), None)

    def test_group_includes_student_summary(self, asc_advisor, asc_curated_group, client, create_alerts):
        """Returns summary details but not full term and analytics data."""
        students = client.get(f'/api/curated_group/{asc_curated_group.id}/students_with_alerts').json
        assert students[0]['cumulativeGPA'] == 3.8
        assert students[0]['cumulativeUnits'] == 101.3
        assert students[0]['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert students[0]['level'] == 'Junior'
        assert students[0]['termGpa'][0]['gpa'] == 2.9
        assert len(students[0]['majors']) == 2

    def test_curated_group_detail_includes_analytics(self, asc_advisor, asc_curated_group, client, create_alerts):
        """Returns all students with full term and analytics data."""
        group = client.get(f'/api/curated_group/{asc_curated_group.id}').json
        student = group['students'][0]
        assert student['cumulativeGPA'] == 3.8
        assert student['cumulativeUnits'] == 101.3
        assert student['level'] == 'Junior'
        assert len(student['majors']) == 2
        assert 'analytics' in student

    def test_curated_group_detail_includes_athletics(self, asc_advisor, asc_curated_group, client):
        """Returns student athletes."""
        group = client.get(f'/api/curated_group/{asc_curated_group.id}').json
        students = group['students']
        teams = students[0]['athleticsProfile']['athletics']
        assert len(teams) == 2
        assert teams[0]['name'] == 'Women\'s Field Hockey'
        assert teams[0]['groupCode'] == 'WFH'
        assert teams[1]['name'] == 'Women\'s Tennis'
        assert teams[1]['groupCode'] == 'WTE'

    def test_curated_group_detail_omits_athletics_non_asc(self, client, coe_advisor, coe_advisor_group):
        """Omits student athletes from COE group."""
        group = client.get(f'/api/curated_group/{coe_advisor_group.id}').json
        assert 'athleticsProfile' not in group['students'][0]

    def test_my_curated_groups_by_sid(self, client, coe_advisor, coe_advisor_group):
        """API delivers accurate set of student SIDs."""
        ids = client.get(f'/api/curated_groups/my/{coe_advisor_group.students[0].sid}').json
        assert ids == [coe_advisor_group.id]


class TestCuratedGroupCreate:
    """Curated Group API."""

    def test_add_multiple_students_to_curated_group(self, asc_advisor, client):
        """Create group and add students."""
        name = 'Cheap Tricks'
        response = client.post(
            '/api/curated_group/create',
            data=json.dumps({
                'name': name,
                'sids': ['2345678901', '11667051'],
            }),
            content_type='application/json',
        )
        group = json.loads(response.data)
        assert group['name'] == name
        assert group['studentCount'] == 2

        # Add students and include invalid sid and dupe sids. Expect no "duplicate key violates" error.
        response = client.post(
            '/api/curated_group/students/add',
            data=json.dumps({
                'curatedGroupId': group['id'],
                'sids': ['7890123456', 'ABC'],
            }),
            content_type='application/json',
        )
        assert response.status_code == 200
        updated_group = json.loads(response.data)
        assert updated_group['id'] == group['id']
        assert updated_group['studentCount'] == 3


class TestCuratedStudents:
    """Curated Group API."""

    def test_add_student(self, asc_advisor, client):
        """Create a group and add a student."""
        group_name = 'Trams of Old London'
        group = _create_group(client, group_name)
        group_id = group['id']
        assert group['studentCount'] == 0
        sid = '2345678901'
        response = client.get(f'/api/curated_group/{group_id}/add_student/{sid}')
        assert response.status_code == 200
        updated_group = response.json
        assert updated_group['name'] == group_name
        assert updated_group['studentCount'] == 1
        student = updated_group['students'][0]
        assert student['sid'] == sid

    def test_remove_student(self, asc_advisor, client):
        """Remove student from a group."""
        group = _create_group(client, 'Furry Green Atom Bowl')
        group_id = group['id']
        sid = '2345678901'
        updated_group = client.get(f'/api/curated_group/{group_id}/add_student/{sid}').json
        assert updated_group['studentCount'] == 1
        response = client.delete(f'/api/curated_group/{group_id}/remove_student/{sid}')
        assert response.status_code == 200
        assert response.json['studentCount'] == 0


class TestUpdateCuratedGroup:
    """Curated Group API."""

    def test_rename_group(self, asc_advisor, client):
        """Rename curated group."""
        group = _create_group(client, 'The Bones In The Ground')
        new_name = 'My Favourite Buildings'
        group_id = group['id']
        response = client.post(
            '/api/curated_group/rename',
            data=json.dumps({'id': group_id, 'name': new_name}),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert client.get(f'/api/curated_group/{group_id}').json['name'] == new_name

    def test_delete_group(self, asc_advisor, client):
        """Delete curated group."""
        group = _create_group(client, 'Mellow Together')
        group_id = group['id']
        assert client.delete(f'/api/curated_group/delete/{group_id}').status_code == 200
        assert client.get(f'/api/curated_group/{group_id}').status_code == 404


def _create_group(client, name):
    response = client.post(
        '/api/curated_group/create',
        data=json.dumps({'name': name}),
        content_type='application/json',
    )
    return json.loads(response.data)
