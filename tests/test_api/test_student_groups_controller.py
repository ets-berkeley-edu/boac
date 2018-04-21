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
from boac.models.student_group import StudentGroup
import pytest
import simplejson as json

test_uid = '6446'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


@pytest.fixture()
def authenticated_session_empty_primary(fake_auth):
    fake_auth.login('2040')


class TestStudentGroupsController:
    """StudentGroup API."""

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/groups/my').status_code == 401

    def test_unauthorized(self, authenticated_session_empty_primary, client):
        """Rejects authenticated user if s/he does not own the group."""
        advisor_with_group = AuthorizedUser.find_by_uid('6446')
        groups = StudentGroup.get_groups_by_owner_id(advisor_with_group.id)
        response = client.get(f'/api/group/{groups[0].id}')
        assert response.status_code == 403

    def test_my_groups(self, authenticated_session, client):
        """Returns all of current_user's student groups."""
        response = client.get('/api/groups/my')
        assert response.status_code == 200
        groups = response.json
        assert len(groups) == 2
        default_group = next(group for group in groups if group['name'] == 'My Students')
        assert len(default_group['students']) == 0
        cool_kids_group = next(group for group in groups if group['name'] == 'Cool Kids')
        assert cool_kids_group['studentCount'] == 4

    def test_empty_group(self, authenticated_session_empty_primary, client):
        """Returns default empty group requested."""
        groups = client.get('/api/groups/my').json
        default_group = next(group for group in groups if group['name'] == 'My Students')
        response = client.get(f'/api/group/{default_group["id"]}')
        assert response.status_code == 200
        assert response.json['students'] == []

    def test_group_summary_excludes_students_without_alerts(self, create_alerts, authenticated_session, client):
        """When all groups are requested, returns only students with alerts."""
        groups = client.get('/api/groups/my').json
        assert groups[0]['studentCount'] == 4
        assert len(groups[0]['students']) == 1
        assert groups[0]['students'][0]['alertCount'] == 3

        alert_to_dismiss = client.get('/api/alerts/current/11667051').json['shown'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        groups = client.get('/api/groups/my').json
        assert groups[0]['students'][0]['alertCount'] == 2

    def test_group_detail_includes_students_without_alerts(self, create_alerts, authenticated_session, client):
        """When group detail is requested, returns all students."""
        groups = client.get('/api/groups/my').json
        group = client.get(f'/api/group/{groups[0]["id"]}').json
        assert group['students'][0]['alertCount'] == 3
        assert 'alertCount' not in group['students'][1]
        assert 'alertCount' not in group['students'][2]
        assert 'alertCount' not in group['students'][3]

    def test_group_index_includes_summary(self, authenticated_session, client):
        """Returns summary details but not full term and analytics data for group index."""
        groups = client.get('/api/groups/my').json
        students = groups[0]['students']
        assert students[0]['cumulativeGPA'] == 3.8
        assert students[0]['cumulativeUnits'] == 101.3
        assert students[0]['level'] == 'Junior'
        assert len(students[0]['majors']) == 2
        assert 'analytics' not in students[0]
        assert 'enrollments' not in students[0]['term']

    def test_group_detail_includes_analytics(self, authenticated_session, client):
        """Returns all students with full term and analytics data for detailed group listing."""
        groups = client.get('/api/groups/my').json
        group = next(group for group in groups if group['name'] == 'Cool Kids')
        group_id = group['id']
        group = client.get(f'/api/group/{group_id}').json
        students = group['students']
        assert students[0]['cumulativeGPA'] == 3.8
        assert students[0]['cumulativeUnits'] == 101.3
        assert students[0]['level'] == 'Junior'
        assert len(students[0]['majors']) == 2
        assert 'analytics' in students[0]
        assert 'enrollments' in students[0]['term']

    def test_group_detail_includes_athletics(self, authenticated_session, client):
        """Returns all students with athletic memberships for detailed group listing."""
        groups = client.get('/api/groups/my').json
        group = next(group for group in groups if group['name'] == 'Cool Kids')
        students = group['students']
        assert len(students[0]['athletics']) == 2
        assert students[0]['athletics'][0]['name'] == 'Women\'s Field Hockey'
        assert students[0]['athletics'][0]['groupCode'] == 'WFH'
        assert students[0]['athletics'][1]['name'] == 'Women\'s Tennis'
        assert students[0]['athletics'][1]['groupCode'] == 'WTE'

    def test_create_add_remove_and_delete(self, authenticated_session, client):
        """Create a group, add a student, remove the student and then delete the group."""
        name = 'Fun Boy Three'
        response = client.post(
            '/api/group/create',
            data=json.dumps({'name': name}),
            content_type='application/json',
        )
        group = json.loads(response.data)
        group_id = group['id']

        # Add student
        sid = '2345678901'
        response = client.get(f'/api/group/{group_id}/add_student/{sid}')
        assert response.status_code == 200
        group = client.get(f'/api/group/{group_id}').json
        assert group['name'] == name
        assert group['students'][0]['sid'] == sid
        # Remove student
        response = client.delete(f'/api/group/{group_id}/remove_student/{sid}')
        assert response.status_code == 200
        group = client.get(f'/api/group/{group_id}').json
        assert group['name'] == name
        assert not len(group['students'])
        # Rename group
        new_name = 'Teenage Wasteland'
        response = client.post(
            '/api/group/update',
            data=json.dumps({'id': group_id, 'name': new_name}),
            content_type='application/json',
        )
        assert response.status_code == 200
        group = client.get(f'/api/group/{group_id}').json
        assert group['name'] == new_name
        # Delete group
        response = client.delete(f'/api/group/delete/{group_id}')
        assert response.status_code == 200
        # Verify
        response = client.get(f'/api/group/{group_id}')
        assert response.status_code == 404
