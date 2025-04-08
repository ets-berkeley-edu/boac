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

from boac import std_commit
from boac.api.csv_file_download_utils import get_students_csv_header_labels
from boac.merged.sis_terms import current_term_id
from boac.models.authorized_user import AuthorizedUser
from boac.models.curated_group import CuratedGroup
import pytest
import simplejson as json
from tests.test_api.api_test_utils import api_curated_group_add_students, api_curated_group_remove_student

admin_uid = '177473'
asc_advisor_uid = '6446'
asc_director_uid = '90412'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'


class TestCreateCuratedGroup:

    def test_not_authenticated(self, client):
        """Reject anonymous user."""
        _api_curated_group_create(client, expected_status_code=401, name='The Awkward Age', sids=['5678901234'])

    def test_authorized(self, client, fake_auth):
        # CoE advisor
        fake_auth.login(coe_advisor_uid)
        curated_group_id = _api_curated_group_create(
            client,
            name='The Awkward Age',
            sids=['5678901234'],
        )['id']
        curated_group = _api_get_curated_group(client, curated_group_id)
        assert 'analytics' in curated_group['students'][0]['term']['enrollments'][0]['canvasSites'][0]
        assert 'underrepresented' in curated_group['students'][0]
        # CE3 advisor
        fake_auth.login(ce3_advisor_uid)
        curated_group = _api_get_curated_group(client, curated_group_id)
        assert curated_group['ownerName'] == 'Joni Mitchell'

    def test_unauthorized(self, app, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        _api_curated_group_create(
            client=client,
            domain='admitted_students',
            expected_status_code=403,
            name="Ain't gonna happen",
            sids=['5678901234'],
        )

    def test_authorized_ce3(self, app, client, fake_auth):
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

    @classmethod
    def setup_class(cls):
        asc_advisor_user_id = AuthorizedUser.get_id_per_uid(asc_advisor_uid)
        coe_advisor_user_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        cls.asc_curated_groups = [c.to_api_json(include_students=False) for c in CuratedGroup.get_curated_groups(asc_advisor_user_id)]
        cls.coe_advisor_groups = [c.to_api_json(include_students=False) for c in CuratedGroup.get_curated_groups(coe_advisor_user_id)]

    def test_not_authenticated(self, client):
        """Anonymous user is rejected."""
        _api_get_curated_group(client, self.asc_curated_groups[0]['id'], expected_status_code=401)

    def test_advisor_cannot_see_admin_curated_group(self, client, fake_auth):
        """403 if advisor tries to access curated group owned by Admin-user."""
        fake_auth.login(coe_advisor_uid)
        admin_curated_groups = CuratedGroup.get_curated_groups(AuthorizedUser.get_id_per_uid(admin_uid))
        _api_get_curated_group(client, admin_curated_groups[0].id, expected_status_code=403)

    def test_curated_group_includes_alert_count(self, client, fake_auth, create_alerts):
        """Includes alert count per student."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'])
        students = api_json.get('students')
        assert students
        for student in students:
            assert isinstance(student.get('alertCount'), int)
        student_with_alerts = next((s for s in students if s['sid'] == '11667051'), None)
        assert student_with_alerts
        assert student_with_alerts['alertCount'] == 4

    def test_curated_group_includes_term_gpa(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'])
        students = api_json['students']
        deborah = next(s for s in students if s['firstName'] == 'Deborah')
        assert len(deborah['termGpa']) == 4
        assert deborah['termGpa'][0] == {'termName': 'Spring 2018', 'gpa': 2.9}
        assert deborah['termGpa'][3] == {'termName': 'Spring 2016', 'gpa': 3.8}

    def test_curated_group_includes_academic_standing(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'])
        students = api_json['students']
        deborah = next(s for s in students if s['firstName'] == 'Deborah')
        assert deborah['academicStanding'] == {
            'actionDate': '2018-05-31',
            'status': 'GST',
            'termName': 'Spring 2018',
        }

    def test_view_permitted_shared_dept(self, client, fake_auth):
        """Advisor can view group if they share the group owner's department memberships."""
        fake_auth.login(asc_director_uid)
        curated_group_id = self.asc_curated_groups[0]['id']
        group = _api_get_curated_group(client, curated_group_id)
        assert group['students']
        response = client.get(f'/api/curated_group/{curated_group_id}/students_with_alerts')
        assert response.status_code == 200

    def test_curated_group_includes_students_without_alerts(
            self,
            client,
            fake_auth,
            create_alerts,
    ):
        """Includes students in response."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='first_name')
        last_names = [s.get('lastName') for s in api_json['students']]
        assert last_names == ['Davies', 'Farestveit', 'Kerschen', 'Jayaprakash']
        alert_counts = [s.get('alertCount') for s in api_json['students']]
        assert alert_counts == [4, 0, 1, 0]

    def test_order_by_level(self, client, fake_auth):
        """Includes students in response, ordered by level."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='level', offset=1, limit=2)
        names = [f"{s.get('level')} ({s.get('lastName')})" for s in api_json['students']]
        assert names == ['Junior (Kerschen)', 'Senior (Farestveit)']

    def test_order_by_major(self, client, fake_auth):
        """Includes students in response, ordered by major."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='major', offset=1)
        majors = [f"{s.get('majors')[0] if len(s.get('majors')) else None} ({s.get('lastName')})" for s in api_json['students']]
        assert majors == [
            'English BA (Kerschen)',
            'Letters & Sci Undeclared UG (Jayaprakash)',
            'Nuclear Engineering BS (Farestveit)',
        ]

    def test_order_by_gpa_desc(self, client, fake_auth):
        """Includes students in response, ordered by cumulative GPA descending."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='gpa desc')
        gpas = [f"{s.get('cumulativeGPA')} ({s.get('lastName')})" for s in api_json['students']]
        assert gpas == [
            '3.9 (Farestveit)',
            '3.8 (Davies)',
            '3.501 (Jayaprakash)',
            '3.005 (Kerschen)',
        ]

    def test_order_by_term_gpa(self, client, fake_auth):
        """Includes students in response, ordered by term GPA, nulls last."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='term_gpa_2178')

        def _fall_2017_gpa(student):
            return next((t['gpa'] for t in student['termGpa'] if t['termName'] == 'Fall 2017'), None) if student['termGpa'] else None
        gpas = [f"{_fall_2017_gpa(s)} ({s.get('lastName')})" for s in api_json['students']]
        assert gpas == [
            '1.8 (Davies)',
            '2.1 (Jayaprakash)',
            '3.2 (Kerschen)',
            'None (Farestveit)',
        ]

    def test_order_by_term_gpa_desc(self, client, fake_auth):
        """Includes students in response, ordered by term GPA descending, nulls last."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='term_gpa_2178 desc')

        def _fall_2017_gpa(student):
            return next((t['gpa'] for t in student['termGpa'] if t['termName'] == 'Fall 2017'), None) if student['termGpa'] else None
        gpas = [f"{_fall_2017_gpa(s)} ({s.get('lastName')})" for s in api_json['students']]
        assert gpas == [
            '3.2 (Kerschen)',
            '2.1 (Jayaprakash)',
            '1.8 (Davies)',
            'None (Farestveit)',
        ]

    def test_order_by_units_enrolled(self, client, fake_auth):
        """Includes students in response, ordered by units in progress, nulls first."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='enrolled_units')
        units = [f"{s['term'].get('enrolledUnits') if s.get('term') else None} ({s.get('lastName')})" for s in api_json['students']]
        assert units == [
            '5 (Kerschen)',
            '7 (Jayaprakash)',
            '12.5 (Davies)',
            'None (Farestveit)',
        ]

    def test_order_by_units_enrolled_desc(self, client, fake_auth):
        """Includes students in response, ordered by units in progress descending, nulls last."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='enrolled_units desc')
        units = [f"{s['term'].get('enrolledUnits') if s.get('term') else None} ({s.get('lastName')})" for s in api_json['students']]
        assert units == [
            '12.5 (Davies)',
            '7 (Jayaprakash)',
            '5 (Kerschen)',
            'None (Farestveit)',
        ]

    def test_order_by_terms_in_attendance(self, client, fake_auth):
        """Includes students in response, ordered by terms completed, nulls last."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='terms_in_attendance')
        units = [f"{s['termsInAttendance']} ({s.get('lastName')})" for s in api_json['students']]
        assert units == [
            '2 (Farestveit)',
            '5 (Kerschen)',
            'None (Davies)',
            'None (Jayaprakash)',
        ]

    def test_curated_group_detail_includes_profiles(self, client, fake_auth, create_alerts):
        """Returns all students with profile data."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'])
        student = api_json['students'][0]
        assert student['cumulativeGPA'] == 3.8
        assert student['cumulativeUnits'] == 101.3
        assert student['level'] == 'Junior'
        assert len(student['majors']) == 2

    def test_coe_advisor_cannot_view_sensitive_asc_data(self, client, fake_auth):
        """Returns athletics data, including intensive and inactive, for ASC advisors."""
        def _get_student_athlete_from_curated_group(sid_):
            curated_groups_id = self.asc_curated_groups[0]['id']
            api_json = _api_get_curated_group(client, curated_groups_id)
            return next((s for s in api_json['students'] if s['sid'] == sid_), None)

        fake_auth.login(coe_advisor_uid)
        sid = '7890123456'
        student_athlete = _get_student_athlete_from_curated_group(sid)
        assert 'athleticsProfile' in student_athlete
        # Next, log in as ASC advisor.
        fake_auth.login(asc_advisor_uid)
        student_athlete = _get_student_athlete_from_curated_group(sid)
        assert 'athleticsProfile' in student_athlete

    def test_curated_group_detail_includes_current_enrollments(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='first_name')
        student_term = api_json['students'][0]['term']
        assert student_term['termName'] == 'Fall 2017'
        assert student_term['enrolledUnits'] == 12.5
        assert len(student_term['enrollments']) == 5
        assert student_term['enrollments'][0]['displayName'] == 'BURMESE 1A'
        assert len(student_term['enrollments'][0]['canvasSites']) == 1

    def test_curated_group_detail_includes_past_enrollments(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        api_json = _api_get_curated_group(client, self.asc_curated_groups[0]['id'], order_by='first_name', term_id='2172')
        student_term = api_json['students'][0]['term']
        assert student_term['termName'] == 'Spring 2017'
        assert student_term['enrolledUnits'] == 10.0
        assert len(student_term['enrollments']) == 3
        assert student_term['enrollments'][0]['displayName'] == 'CLASSIC 130 LEC 001'
        assert student_term['enrollments'][0]['grade'] == 'P'

    def test_curated_group_detail_suppresses_canvas_data_when_unauthorized(self, user_factory, client, fake_auth):
        """Suppress Canvas data when unauthorized."""
        advisor = user_factory(can_access_canvas_data=False)
        fake_auth.login(advisor.uid)
        group = _api_curated_group_create(client, name='The Awkward Age', sids=['5678901234'])
        student_feed = _api_get_curated_group(client, group['id'])['students'][0]
        assert student_feed['term']['enrollments'][0]['canvasSites'] == []

    def test_curated_groups_all(self, client, fake_auth):
        """Returns all groups to which user has viewing access, per owner."""
        fake_auth.login(asc_director_uid)
        response = client.get('/api/curated_groups/by_dept_code/qcadv')
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


class TestGetCuratedGroupStudentsWithAlerts:

    @classmethod
    def setup_class(cls):
        asc_advisor_user_id = AuthorizedUser.get_id_per_uid(asc_advisor_uid)
        cls.asc_curated_groups = [c.to_api_json(include_students=False) for c in CuratedGroup.get_curated_groups(asc_advisor_user_id)]

    @staticmethod
    def _api_students_with_alerts(client, curated_group_id, expected_status_code=200):
        response = client.get(f'/api/curated_group/{curated_group_id}/students_with_alerts')
        assert response.status_code == expected_status_code
        return response.json

    def test_students_with_alerts(self, client, fake_auth, create_alerts, db_session):
        """Students with alerts per group id."""
        fake_auth.login(asc_advisor_uid)
        api_json = self._api_students_with_alerts(client, self.asc_curated_groups[0]['id'])
        assert len(api_json) == 2
        assert api_json[0]['alertCount'] == 4
        assert api_json[1]['alertCount'] == 1

        student = client.get('/api/student/by_uid/61889').json
        alert_to_dismiss = student['notifications']['alert'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        curated_group_id = self.asc_curated_groups[0]['id']
        students_with_alerts = client.get(f'/api/curated_group/{curated_group_id}/students_with_alerts').json
        assert students_with_alerts[0]['alertCount'] == 3

    def test_group_includes_student_summary(self, client, fake_auth, create_alerts):
        """Returns summary details but not full term and analytics data."""
        fake_auth.login(asc_advisor_uid)
        api_json = self._api_students_with_alerts(client, self.asc_curated_groups[0]['id'])
        assert api_json[0]['academicStanding']['status'] == 'GST'
        assert api_json[0]['cumulativeGPA'] == 3.8
        assert api_json[0]['cumulativeUnits'] == 101.3
        assert api_json[0]['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert api_json[0]['level'] == 'Junior'
        assert api_json[0]['termGpa'][0]['gpa'] == 2.9
        assert len(api_json[0]['majors']) == 2


class TestAddStudents:

    @classmethod
    def setup_class(cls):
        user_id = AuthorizedUser.get_id_per_uid(asc_advisor_uid)
        cls.asc_curated_groups = [c.to_api_json(include_students=False) for c in CuratedGroup.get_curated_groups(user_id)]

    def test_not_authenticated(self, client):
        """Anonymous user is rejected."""
        assert api_curated_group_add_students(
            client,
            curated_group_ids=[self.asc_curated_groups[0]['id']],
            expected_status_code=401,
            sids=['2345678901'],
        )

    def test_unauthorized(self, client, fake_auth):
        """403 if user does not own the group."""
        fake_auth.login(admin_uid)
        assert api_curated_group_add_students(client, [self.asc_curated_groups[0]['id']], expected_status_code=403, sids=['2345678901'])

    def test_add_student(self, client, fake_auth):
        """Create a group and add a student."""
        fake_auth.login(asc_advisor_uid)
        group_name = 'Trams of Old London'
        group = _api_curated_group_create(client, name=group_name)
        assert group['totalStudentCount'] == 0
        sid = '2345678901'
        updated_groups = api_curated_group_add_students(client, [group['id']], sids=[sid])
        assert updated_groups[0]['name'] == group_name
        assert updated_groups[0]['totalStudentCount'] == 1
        assert updated_groups[0]['sids'] == [sid]

    def test_add_students(self, client, fake_auth):
        """Create group and add students."""
        fake_auth.login(asc_advisor_uid)
        name = 'Cheap Tricks'
        group = _api_curated_group_create(client, name=name, sids=['2345678901', '11667051'])
        assert group['name'] == name
        assert group['totalStudentCount'] == 2
        # Add students
        updated_groups = api_curated_group_add_students(
            client,
            [group['id']],
            return_student_profiles=True,
            sids=['7890123456'],
        )
        assert updated_groups[0]['totalStudentCount'] == 3
        students = updated_groups[0]['students']
        sids = [s['sid'] for s in students]
        assert sids == ['11667051', '2345678901', '7890123456']
        # Add more and ask for FULL student profiles in payload
        updated_groups = api_curated_group_add_students(
            client,
            [group['id']],
            return_student_profiles=True,
            sids=['890127492', '8901234567'],
        )
        assert updated_groups[0]['totalStudentCount'] == 5
        students = updated_groups[0]['students']
        students.sort(key=lambda s: s['sid'])
        student = students[0]
        assert student['sid'] == '11667051'
        assert student['canvasUserId'] == '9000100'
        for expected_key in ('academicStanding', 'cumulativeGPA', 'cumulativeGPA', 'cumulativeUnits', 'majors', 'termGpa'):
            assert expected_key in student, f'Failed to find {expected_key} in student'

    def test_add_students_to_groups(self, client, fake_auth):
        """Create two groups and add students to both."""
        fake_auth.login(asc_advisor_uid)
        names = ['Everybody Loves the Sunshine', 'Wind Parade']
        groups = [_api_curated_group_create(client, name=name) for name in names]
        # Add students
        updated_groups = api_curated_group_add_students(
            client,
            [group['id'] for group in groups],
            return_student_profiles=True,
            sids=['11667051', '2345678901', '7890123456'],
        )
        for group in updated_groups:
            assert group['totalStudentCount'] == 3
            students = group['students']
            sids = [s['sid'] for s in students]
            assert sids == ['11667051', '2345678901', '7890123456']


class TestRemoveStudent:
    """Curated Group API."""

    @classmethod
    def setup_class(cls):
        user_id = AuthorizedUser.get_id_per_uid(asc_advisor_uid)
        cls.asc_curated_groups = [c.to_api_json(include_students=False) for c in CuratedGroup.get_curated_groups(user_id)]

    def test_not_authenticated(self, client):
        """Anonymous user is rejected."""
        api_curated_group_remove_student(client, [self.asc_curated_groups[0]['id']], '2345678901', expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """403 if user does not own the group."""
        fake_auth.login(admin_uid)
        api_curated_group_remove_student(client, [self.asc_curated_groups[0]['id']], '2345678901', expected_status_code=403)

    def test_remove_student(self, client, fake_auth):
        """Remove student from a curated group."""
        fake_auth.login(asc_advisor_uid)
        name = 'Furry Green Atom Bowl'
        sid = '2345678901'
        curated_group = _api_curated_group_create(client, name=name)
        curated_group_id = curated_group['id']
        curated_groups = api_curated_group_add_students(client, [curated_group_id], sids=[sid])
        assert curated_groups[0]['sids'] == [sid]
        assert curated_groups[0]['totalStudentCount'] == 1
        # Remove the SID
        curated_groups = api_curated_group_remove_student(client, [curated_group_id], sid)
        assert curated_groups[0]['totalStudentCount'] == 0

    def test_remove_student_from_groups(self, client, fake_auth):
        """Remove student from two curated groups."""
        fake_auth.login(asc_advisor_uid)
        names = ['Carcajou', 'Daylight']
        sid = '2345678901'
        curated_groups = [_api_curated_group_create(client, name=name) for name in names]
        curated_group_ids = [curated_group['id'] for curated_group in curated_groups]
        updated_curated_groups = api_curated_group_add_students(client, curated_group_ids, sids=[sid])
        for curated_group in updated_curated_groups:
            assert curated_group['sids'] == [sid]
            assert curated_group['totalStudentCount'] == 1
        updated_curated_groups = api_curated_group_remove_student(client, curated_group_ids, sid)
        for curated_group in updated_curated_groups:
            assert curated_group['sids'] == []
            assert curated_group['totalStudentCount'] == 0


class TestUpdateCuratedGroup:
    """Curated Group API."""

    def test_rename_group(self, client, fake_auth):
        """Rename curated group."""
        fake_auth.login(asc_advisor_uid)
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

    @classmethod
    def setup_class(cls):
        user_id = AuthorizedUser.get_id_per_uid(asc_advisor_uid)
        cls.asc_curated_groups = [c.to_api_json(include_students=False) for c in CuratedGroup.get_curated_groups(user_id)]

    def test_not_authenticated(self, client):
        """Anonymous user is rejected."""
        curated_group_id = self.asc_curated_groups[0]['id']
        response = client.delete(f'/api/curated_group/delete/{curated_group_id}')
        assert response.status_code == 401

    def test_unauthorized(self, client, fake_auth):
        """403 if user does not own the group."""
        fake_auth.login(admin_uid)
        curated_group_id = self.asc_curated_groups[0]['id']
        response = client.delete(f'/api/curated_group/delete/{curated_group_id}')
        assert response.status_code == 403

    def test_delete_group(self, client, fake_auth):
        """Delete curated group."""
        fake_auth.login(asc_advisor_uid)
        group = _api_curated_group_create(client, name='Mellow Together')
        group_id = group['id']
        assert client.delete(f'/api/curated_group/delete/{group_id}').status_code == 200
        assert client.get(f'/api/curated_group/{group_id}').status_code == 404


class TestCuratedGroupWithInactives:

    active_sid = '2345678901'
    inactive_sid = '3141592653'
    completed_sid = '2718281828'

    def test_create_group_with_inactives(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
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

    def test_add_inactive_to_group(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        group = _api_curated_group_create(
            client=client,
            name='Listening to the Higsons',
            sids=[self.active_sid],
        )
        assert group['totalStudentCount'] == 1
        updated_groups = api_curated_group_add_students(
            client,
            [group['id']],
            return_student_profiles=True,
            sids=[self.inactive_sid],
        )
        assert updated_groups[0]['totalStudentCount'] == 2
        assert updated_groups[0]['students'][1]['sid'] == self.active_sid
        assert updated_groups[0]['students'][0]['sid'] == self.inactive_sid


class TestDownloadCuratedGroupCSV:
    """Download Curated Group CSV API."""

    @classmethod
    def setup_class(cls):
        asc_user_id = AuthorizedUser.get_id_per_uid(asc_advisor_uid)
        coe_user_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        cls.asc_curated_groups = [c.to_api_json(include_students=False) for c in CuratedGroup.get_curated_groups(asc_user_id)]
        cls.coe_advisor_groups = [c.to_api_json(include_students=False) for c in CuratedGroup.get_curated_groups(coe_user_id)]

    def test_download_csv_not_authenticated(self, client):
        """Anonymous user is rejected."""
        data = {
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
            ],
        }
        curated_group_id = self.asc_curated_groups[0]['id']
        response = client.post(
            f'/api/curated_group/{curated_group_id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 401

    def test_download_csv_unauthorized(self, client, fake_auth):
        """403 if user does not share a department membership with group owner."""
        fake_auth.login(coe_advisor_uid)
        data = {
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
            ],
        }
        curated_group_id = self.asc_curated_groups[0]['id']
        client.post(
            f'/api/curated_group/{curated_group_id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        # TODO: Do we want to forbid such downloads?
        # assert response.status_code == 403

    def test_download_admits_csv(self, app, client, fake_auth):
        """Advisor can download CSV of 'admits' group."""
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
                'birthdate',
                'citizenship_country',
                'family_dependents_num',
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
            'birthdate,citizenship_country,family_dependents_num,highest_parent_education_level,non_immigrant_visa_current,xethnic',  # noqa: E501
            '1985-06-02,Greece,05,5 - College Attended,,NotSpecified',
        ]:
            assert str(snippet) in csv

    def test_download_csv(self, client, fake_auth):
        """Advisor can download CSV with ALL students of group."""
        fake_auth.login(asc_advisor_uid)
        data = {
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
                'email',
                'phone',
                'majors',
                'college',
                'level_by_units',
                'terms_in_attendance',
                'expected_graduation_term',
                'units_completed',
                'term_gpa_2172',
                'cumulative_gpa',
                'program_status',
                'college_advisor',
            ],
        }
        curated_group = next((g for g in self.asc_curated_groups if g['name'] == 'Four students'), None)
        assert curated_group
        curated_group_id = curated_group['id']
        response = client.post(
            f'/api/curated_group/{curated_group_id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = response.data.decode('UTF-8').split('\n')
        header_label_lookup = get_students_csv_header_labels(current_term_id())
        expected_headers = ['first_name', 'last_name', 'sid', 'email', 'phone', 'majors', 'level_by_units',
                            'terms_in_attendance', 'expected_graduation_term', 'units_completed', 'term_gpa_2172',
                            'cumulative_gpa', 'program_status']
        for expected_header in expected_headers:
            expected_label = header_label_lookup.get(expected_header, expected_header)
            assert expected_label in csv[0]
        for row in csv[1:]:
            if row.startswith('Deborah,Davies'):
                assert '11667051,barnburner@berkeley.edu,415/123-4567,English BA; Nuclear Engineering BS,Engineering; Undergrad Letters & Science,Junior,,Fall 2019,101.3,2.700,3.8,Active,' in row  # noqa: E501
            elif row.startswith('Pauline,Kerschen'):
                assert '3456789012,doctork@berkeley.edu,415/123-4567,English BA; Political Economy BA,Undergrad Letters & Science,Junior,5,Fall 2019,70,,3.005,Active,' in row  # noqa: E501
            elif row.startswith('Sandeep,Jayaprakash'):
                assert '5678901234,ilovela@berkeley.edu,415/123-4567,Letters & Sci Undeclared UG,Undergrad Letters & Science,Senior,,Fall 2019,102,,3.501,Active,' in row  # noqa: E501
            elif row.startswith('Paul,Farestveit'):
                assert '7890123456,qadept@berkeley.edu,415/123-4567,Nuclear Engineering BS,Undergrad Engineering,Senior,2,Spring 2020,110,,3.9,Active,Real Advisor' in row  # noqa: E501
            elif row:
                pytest.fail(f'Unexpected CSV content: {row}')

    def test_download_csv_shared_dept(self, client, fake_auth):
        """Advisor can download CSV if they share the group owner's department memberships."""
        fake_auth.login(asc_director_uid)
        data = {
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
            ],
        }
        curated_group = next((g for g in self.asc_curated_groups if g['name'] == 'Four students'), None)
        assert curated_group
        curated_group_id = curated_group['id']
        response = client.post(
            f'/api/curated_group/{curated_group_id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type

    def test_download_csv_custom_columns(self, client, fake_auth):
        """Advisor can generate a CSV with the columns they want."""
        fake_auth.login(asc_advisor_uid)
        data = {
            'csvColumnsSelected': [
                'majors',
                'college',
                'level_by_units',
                'terms_in_attendance',
                'expected_graduation_term',
                'units_completed',
                'term_gpa_2175',
                'cumulative_gpa',
                'program_status',
            ],
        }
        curated_group = next((g for g in self.asc_curated_groups if g['name'] == 'Four students'), None)
        assert curated_group
        curated_group_id = curated_group['id']
        response = client.post(
            f'/api/curated_group/{curated_group_id}/download_csv',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = response.data.decode('UTF-8').split('\n')
        header_label_lookup = get_students_csv_header_labels(current_term_id())
        expected_headers = ['majors', 'college', 'level_by_units', 'terms_in_attendance', 'expected_graduation_term',
                            'units_completed', 'term_gpa_2175', 'cumulative_gpa', 'program_status']
        for expected_header in expected_headers:
            expected_label = header_label_lookup.get(expected_header, expected_header)
            assert expected_label in csv[0]
        for row in csv[1:]:
            if row.startswith('English BA; Nuclear Engineering BS'):
                assert 'Junior,,Fall 2019,101.3,,3.8,Active' in row
            elif row.startswith('English BA; Political Economy BA'):
                assert 'Junior,5,Fall 2019,70,,3.005,Active' in row
            elif row.startswith('Letters & Sci Undeclared UG'):
                assert 'Senior,,Fall 2019,102,,3.501,Active' in row
            elif row.startswith('Nuclear Engineering BS'):
                assert 'Senior,2,Spring 2020,110,,3.9,Active' in row
            elif row:
                pytest.fail(f'Unexpected CSV content: {row}')

    def test_download_csv_per_term_id(self, client, fake_auth):
        """Advisor can download CSV per specified term_id."""
        fake_auth.login(asc_director_uid)
        curated_group = self.coe_advisor_groups[0]
        assert curated_group

        results = {}
        default_term_id = str(current_term_id())
        custom_term_id = '2172'
        assert default_term_id != custom_term_id

        for term_id in (default_term_id, custom_term_id):
            data = {
                'csvColumnsSelected': [
                    'units_in_progress',
                ],
                'termId': term_id,
            }
            curated_group_id = curated_group['id']
            response = client.post(
                f'/api/curated_group/{curated_group_id}/download_csv',
                data=json.dumps(data),
                content_type='application/json',
            )
            assert response.status_code == 200
            assert 'csv' in response.content_type
            results[term_id] = str(response.data)

        assert results[default_term_id] != results[custom_term_id]


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
