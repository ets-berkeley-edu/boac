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
from boac.models.curated_cohort import CuratedCohort
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
def cohorts_of_asc_advisor():
    advisor = AuthorizedUser.find_by_uid(asc_advisor_uid)
    return CuratedCohort.get_curated_cohorts_by_owner_id(advisor.id)


@pytest.fixture()
def cohorts_of_coe_advisor():
    advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
    return CuratedCohort.get_curated_cohorts_by_owner_id(advisor.id)


class TestGetCuratedCohort:
    """Curated Cohort API."""

    def test_not_authenticated(self, client):
        """Rejects anonymous user."""
        response = client.get('/api/curated_groups/my')
        assert response.status_code == 401

    def test_unauthorized(self, admin_user_session, client, cohorts_of_asc_advisor):
        """Rejects authenticated user if s/he does not own the curated_cohort."""
        cohort_id = cohorts_of_asc_advisor[0].id
        response = client.get(f'/api/curated_group/{cohort_id}')
        assert response.status_code == 403

    def test_coe_curated_groups(self, client, coe_advisor):
        """Gets curated groups of COE advisor."""
        response = client.get('/api/curated_groups/my')
        assert response.status_code == 200
        groups = response.json
        assert len(groups) == 1
        group = groups[0]
        assert 'id' in group
        assert 'alertCount' in group
        assert 'studentCount' in group
        assert group['name'] == 'Cohort of One'

    def test_asc_curated_groups(self, client, fake_auth):
        """Returns ASC advisor's curated groups."""
        fake_auth.login(asc_advisor_uid)
        response = client.get('/api/curated_groups/my')
        assert response.status_code == 200
        cohorts = response.json
        assert len(cohorts) == 2
        assert 'name' in cohorts[0]
        assert 'studentCount' in cohorts[0]

    def test_curated_cohort_includes_alert_count(self, asc_advisor, client, cohorts_of_asc_advisor, create_alerts):
        """Successfully fetches curated_cohort with alert count per student."""
        cohort_id = cohorts_of_asc_advisor[0].id
        response = client.get(f'/api/curated_group/{cohort_id}')
        students = response.json.get('students')
        assert students
        for student in students:
            assert isinstance(student.get('alertCount'), int)
        student_with_alerts = next((s for s in students if s['sid'] == '11667051'), None)
        assert student_with_alerts
        assert student_with_alerts['alertCount'] == 3

    def test_curated_cohort_includes_term_gpas(self, asc_advisor, client, cohorts_of_asc_advisor):
        cohort_id = cohorts_of_asc_advisor[0].id
        deborah = next(s for s in client.get(f'/api/curated_group/{cohort_id}').json['students'] if s['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}


class TestMyCuratedCohorts:
    """Curated Cohort API."""

    def test_students_without_alerts(self, asc_advisor, client, create_alerts, cohorts_of_asc_advisor, db_session):
        """Students with alerts per curated cohort id."""
        cohort_id = cohorts_of_asc_advisor[0].id
        students_with_alerts = client.get(f'/api/curated_group/{cohort_id}/students_with_alerts').json
        assert len(students_with_alerts) == 2
        assert students_with_alerts[0]['alertCount'] == 3

        student = client.get('/api/student/61889').json
        alert_to_dismiss = student['notifications']['alert'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        students_with_alerts = client.get(f'/api/curated_group/{cohort_id}/students_with_alerts').json
        assert students_with_alerts[0]['alertCount'] == 2

    def test_curated_cohort_detail_includes_students_without_alerts(self, asc_advisor, client, cohorts_of_asc_advisor, create_alerts):
        """When curated_cohort detail is requested, returns all students."""
        cohort_id = cohorts_of_asc_advisor[0].id
        cohort = client.get(f'/api/curated_group/{cohort_id}').json
        alert_counts = [s.get('alertCount') for s in cohort['students']]
        assert alert_counts == [3, 0, 0, 1]

    def test_curated_cohort_index_includes_summary(self, asc_advisor, client, cohorts_of_asc_advisor, create_alerts):
        """Returns summary details but not full term and analytics data for curated_cohort index."""
        cohort_id = cohorts_of_asc_advisor[0].id
        students = client.get(f'/api/curated_group/{cohort_id}/students_with_alerts').json
        assert students[0]['cumulativeGPA'] == 3.8
        assert students[0]['cumulativeUnits'] == 101.3
        assert students[0]['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert students[0]['level'] == 'Junior'
        assert students[0]['termGpa'][0]['gpa'] == 2.9
        assert len(students[0]['majors']) == 2

    def test_curated_cohort_detail_includes_analytics(self, asc_advisor, client, cohorts_of_asc_advisor, create_alerts):
        """Returns all students with full term and analytics data for detailed curated_cohort listing."""
        cohort_id = cohorts_of_asc_advisor[0].id
        cohort = client.get(f'/api/curated_group/{cohort_id}').json
        student = cohort['students'][0]
        assert student['cumulativeGPA'] == 3.8
        assert student['cumulativeUnits'] == 101.3
        assert student['level'] == 'Junior'
        assert len(student['majors']) == 2
        assert 'analytics' in student

    def test_curated_cohort_detail_includes_athletics(self, asc_advisor, client, cohorts_of_asc_advisor):
        """Returns all students with athletic memberships for detailed curated_cohort listing."""
        cohort_id = cohorts_of_asc_advisor[0].id
        cohort = client.get(f'/api/curated_group/{cohort_id}').json
        students = cohort['students']
        teams = students[0]['athleticsProfile']['athletics']
        assert len(teams) == 2
        assert teams[0]['name'] == 'Women\'s Field Hockey'
        assert teams[0]['groupCode'] == 'WFH'
        assert teams[1]['name'] == 'Women\'s Tennis'
        assert teams[1]['groupCode'] == 'WTE'

    def test_curated_cohort_detail_omits_athletics_non_asc(self, client, coe_advisor, cohorts_of_coe_advisor):
        cohort_id = cohorts_of_coe_advisor[0].id
        cohort = client.get(f'/api/curated_group/{cohort_id}').json
        assert 'athleticsProfile' not in cohort['students'][0]

    def test_my_curated_cohorts_by_sid(self, client, coe_advisor, cohorts_of_coe_advisor):
        cohort = cohorts_of_coe_advisor[0]
        sid = cohort.students[0].sid
        curated_cohort_ids = client.get(f'/api/curated_groups/my/{sid}').json
        assert curated_cohort_ids == [cohort.id]


class TestCuratedCohortCreate:
    """Curated Cohort Create API."""

    def test_add_multiple_students_to_curated_cohort(self, asc_advisor, client):
        """Create curated cohort and add students."""
        name = 'Cheap Tricks'
        response = client.post(
            '/api/curated_group/create',
            data=json.dumps({
                'name': name,
                'sids': ['2345678901', '11667051'],
            }),
            content_type='application/json',
        )
        cohort = json.loads(response.data)
        assert cohort['name'] == name
        assert cohort['studentCount'] == 2

        # Add students and include invalid sid and dupe sids. Expect no "duplicate key violates" error.
        response = client.post(
            '/api/curated_group/students/add',
            data=json.dumps({
                'curatedCohortId': cohort['id'],
                'sids': ['7890123456', 'ABC'],
            }),
            content_type='application/json',
        )
        assert response.status_code == 200
        updated_cohort = json.loads(response.data)
        assert updated_cohort['id'] == cohort['id']
        assert updated_cohort['studentCount'] == 3


class TestCuratedCohortDelete:
    """Curated Cohort Create API."""

    def test_create_add_remove_and_delete(self, asc_advisor, client):
        """Create a curated_cohort, add a student, remove the student and then delete the curated_cohort."""
        name = 'Fun Boy Three'
        response = client.post(
            '/api/curated_group/create',
            data=json.dumps({'name': name}),
            content_type='application/json',
        )
        cohort = json.loads(response.data)
        curated_cohort_id = cohort['id']

        # Add student
        sid = '2345678901'
        student_count_before = cohort['studentCount']
        response = client.get(f'/api/curated_group/{curated_cohort_id}/add_student/{sid}')
        assert response.status_code == 200
        assert response.json['studentCount'] == student_count_before + 1

        cohort = client.get(f'/api/curated_group/{curated_cohort_id}').json
        assert cohort['name'] == name
        student = cohort['students'][0]
        assert student['sid'] == sid
        assert isinstance(student.get('alertCount'), int)
        # Remove student
        student_count_before = cohort['studentCount']
        response = client.delete(f'/api/curated_group/{curated_cohort_id}/remove_student/{sid}')
        assert response.status_code == 200
        assert response.json['studentCount'] == student_count_before - 1

        cohort = client.get(f'/api/curated_group/{curated_cohort_id}').json
        assert cohort['name'] == name
        assert not len(cohort['students'])
        # Rename curated_cohort
        new_name = 'Teenage Wasteland'
        response = client.post(
            '/api/curated_group/rename',
            data=json.dumps({'id': curated_cohort_id, 'name': new_name}),
            content_type='application/json',
        )
        assert response.status_code == 200
        cohort = client.get(f'/api/curated_group/{curated_cohort_id}').json
        assert cohort['name'] == new_name
        # Delete curated_cohort
        response = client.delete(f'/api/curated_group/delete/{curated_cohort_id}')
        assert response.status_code == 200
        # Verify
        response = client.get(f'/api/curated_group/{curated_cohort_id}')
        assert response.status_code == 404
