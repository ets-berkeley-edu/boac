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
from boac.merged import calnet
from boac.models.appointment import Appointment
from boac.models.authorized_user import AuthorizedUser
from boac.models.json_cache import insert_row as insert_in_json_cache
from boac.models.university_dept import UniversityDept
from flask import current_app as app
import simplejson as json
from tests.test_api.test_appointments_controller import AppointmentTestUtil
from tests.util import override_config

admin_uid = '2040'
asc_advisor_uid = '1081940'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'
coe_advisor_no_advising_data_uid = '1022796'
coe_scheduler_uid = '6972201'
deleted_user_uid = '33333'
l_s_college_scheduler_uid = '19735'
l_s_college_advisor_uid = '188242'
l_s_college_drop_in_advisor_uid = '53791'


class TestUserProfile:
    """User Profile API."""

    @staticmethod
    def _api_my_profile(client, expected_status_code=200):
        response = client.get('/api/profile/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_profile_not_authenticated(self, client):
        """Returns a well-formed response."""
        api_json = self._api_my_profile(client)
        assert api_json['isAuthenticated'] is False
        assert not api_json['uid']
        assert api_json['canEditDegreeProgress'] is False
        assert api_json['canReadDegreeProgress'] is False

    def test_current_user_profile(self, client, fake_auth):
        """Includes user profile info from Canvas."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_my_profile(client)
        assert api_json['isAuthenticated'] is True
        assert api_json['uid'] == coe_advisor_uid
        assert 'csid' in api_json
        assert 'firstName' in api_json
        assert 'lastName' in api_json
        assert api_json['canEditDegreeProgress'] is True
        assert api_json['canReadDegreeProgress'] is True

    def test_can_edit_degree_progress(self, client, fake_auth):
        """Degree check permissions."""
        def _assert(uid, has_permission):
            fake_auth.login(uid)
            api_json = self._api_my_profile(client)
            assert api_json['canEditDegreeProgress'] is has_permission
            assert api_json['canReadDegreeProgress'] is has_permission

        _assert(admin_uid, True)
        _assert(coe_advisor_uid, True)

    def test_user_with_no_dept_membership(self, client, fake_auth):
        """Returns zero or more departments."""
        fake_auth.login(admin_uid)
        api_json = self._api_my_profile(client)
        assert api_json['isAdmin'] is True
        assert not len(api_json['departments'])

    def test_user_with_scheduler_role(self, client, fake_auth):
        """Returns COE scheduler profile."""
        fake_auth.login(coe_scheduler_uid)
        api_json = self._api_my_profile(client)
        assert api_json['isAdmin'] is False
        assert api_json['canAccessAdvisingData'] is True
        assert api_json['canAccessCanvasData'] is False
        assert api_json['canEditDegreeProgress'] is False
        assert api_json['canReadDegreeProgress'] is True
        assert not api_json['dropInAdvisorStatus']
        departments = api_json['departments']
        assert len(departments) == 1
        assert departments[0]['code'] == 'COENG'
        assert departments[0]['name'] == 'College of Engineering'
        assert departments[0]['role'] == 'scheduler'

    def test_non_drop_in_dept_user(self, client, fake_auth):
        """Excludes drop-in status when dept is not configured for drop-in advising."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_my_profile(client)
        assert not api_json['dropInAdvisorStatus']

    def test_asc_advisor_exclude_cohorts(self, client, fake_auth):
        """Returns Athletic Study Center drop-in advisor."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['UWASC']):
            fake_auth.login(asc_advisor_uid)
            api_json = self._api_my_profile(client)
            assert api_json['canAccessAdvisingData'] is True
            assert api_json['canAccessCanvasData'] is True
            assert api_json['dropInAdvisorStatus'] == [{'deptCode': 'UWASC', 'available': True, 'status': None}]
            departments = api_json['departments']
            assert len(departments) == 1
            assert departments[0]['code'] == 'UWASC'
            assert departments[0]['name'] == 'Athletic Study Center'
            assert departments[0]['role'] == 'advisor'

    def test_other_user_profile(self, client, fake_auth):
        fake_auth.login(admin_uid)
        response = client.get('/api/profile/6446')
        api_json = response.json
        assert api_json['uid'] == '6446'
        assert 'firstName' in api_json
        assert 'lastName' in api_json
        assert 'canEditDegreeProgress' not in api_json
        assert 'canReadDegreeProgress' not in api_json

    def test_other_user_profile_not_found(self, client, fake_auth):
        fake_auth.login(admin_uid)
        response = client.get('/api/profile/2549')
        assert response.status_code == 404


class TestMyCohorts:

    @classmethod
    def _api_my_profile(cls, client, expected_status_code=200):
        response = client.get('/api/profile/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_my_cohorts(self, client, fake_auth):
        """Returns cohorts of COE advisor."""
        fake_auth.login(coe_advisor_uid)
        cohorts = self._api_my_profile(client)['myCohorts']
        for key in 'name', 'alertCount', 'criteria', 'totalStudentCount', 'isOwnedByCurrentUser':
            assert key in cohorts[0], f'Missing cohort element: {key}'

    def test_feature_flag_false_for_admitted_students_domain(self, client, fake_auth):
        """No 'admitted_students' cohorts if feature flag is false."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', False):
            fake_auth.login(ce3_advisor_uid)
            cohorts = self._api_my_profile(client)['myCohorts']
            assert not [c for c in cohorts if c['domain'] == 'admitted_students']

    def test_cohorts_all_for_ce3(self, client, fake_auth):
        """Returns all standard cohorts for CE3 advisor."""
        fake_auth.login(ce3_advisor_uid)
        cohorts = self._api_my_profile(client)['myCohorts']
        count = len(cohorts)
        assert count == 1
        assert cohorts[0]['name'] == 'Undeclared students'

    def test_admitted_students_cohorts_all_for_ce3(self, client, fake_auth):
        """Returns all standard cohorts for CE3 advisor."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            fake_auth.login(ce3_advisor_uid)
            cohorts = self._api_my_profile(client)['myCohorts']
            cohorts = [c for c in cohorts if c['domain'] == 'admitted_students']
            count = len(cohorts)
            assert count == 1
            assert cohorts[0]['name'] == 'First Generation Students'


class TestMyCuratedGroups:

    @staticmethod
    def _api_my_profile(client, expected_status_code=200):
        response = client.get('/api/profile/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_authorized(self, client, fake_auth):
        """Returns curated groups of authorized advisor."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_my_profile(client)['myCuratedGroups']
        assert len(api_json)
        group = api_json[0]
        assert 'id' in group
        assert 'alertCount' in group
        assert 'totalStudentCount' in group
        assert group['name'] == 'I have two students'

    def test_admitted_students_domain(self, app, client, fake_auth):
        """Returns 'admitted_students' groups of CE3 advisor."""
        fake_auth.login(ce3_advisor_uid)
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            curated_groups = self._api_my_profile(client)['myCuratedGroups']
            assert len(curated_groups) > 0
            domains = set([c['domain'] for c in curated_groups])
            assert len(domains) == 1
            assert list(domains)[0] == 'admitted_students'
            next((c for c in curated_groups if c['name'] == "My 'admitted_students' group"), False)


class TestCalnetProfileByUid:
    """Calnet Profile API."""

    def test_user_by_uid_not_authenticated(self, client):
        """Returns 401 when not authenticated."""
        user = AuthorizedUser.find_by_uid(asc_advisor_uid)
        response = client.get(f'/api/user/calnet_profile/by_uid/{user.uid}')
        assert response.status_code == 401

    def test_user_by_uid(self, client, fake_auth):
        """Advisor can view CalNet profile of another user."""
        current_user = AuthorizedUser.find_by_uid(coe_advisor_uid)
        fake_auth.login(current_user.uid)

        target_user = AuthorizedUser.find_by_uid(asc_advisor_uid)
        response = client.get(f'/api/user/calnet_profile/by_uid/{target_user.uid}')
        assert response.status_code == 200
        assert response.json['uid'] == target_user.uid
        response = client.get(f'/api/user/calnet_profile/by_user_id/{target_user.id}')
        assert response.status_code == 200
        assert response.json['uid'] == target_user.uid

    def test_user_by_csid_not_authenticated(self, client):
        """Returns 401 when not authenticated."""
        response = client.get(f'/api/user/calnet_profile/by_csid/{81067873}')
        assert response.status_code == 401

    def test_user_by_csid(self, client, fake_auth):
        """Delivers CalNet profile."""
        fake_auth.login(admin_uid)
        response = client.get(f'/api/user/calnet_profile/by_csid/{81067873}')
        assert response.status_code == 200
        assert response.json['csid'] == '81067873'


class TestUserByUid:
    """User by UID API."""

    def test_not_authenticated(self, client):
        """Returns 401 when not authenticated."""
        user = AuthorizedUser.find_by_uid(asc_advisor_uid)
        response = client.get(f'/api/user/by_uid/{user.uid}')
        assert response.status_code == 401

    def test_user_not_found(self, client, fake_auth):
        """404 when user not found."""
        fake_auth.login(admin_uid)
        assert client.get('/api/user/by_uid/99999999999999999').status_code == 404

    def test_deleted_user_not_found(self, client, fake_auth):
        """404 is default if get deleted user by UID."""
        fake_auth.login(admin_uid)
        assert client.get(f'/api/user/by_uid/{deleted_user_uid}').status_code == 404
        assert client.get(f'/api/user/by_uid/{deleted_user_uid}?ignoreDeleted=true').status_code == 404

    def test_get_deleted_user_by_uid(self, client, fake_auth):
        """Get deleted user by UID if specific param is passed."""
        fake_auth.login(admin_uid)
        response = client.get(f'/api/user/by_uid/{deleted_user_uid}?ignoreDeleted=false')
        assert response.status_code == 200
        assert response.json['uid'] == deleted_user_uid

    def test_user_by_csid(self, client, fake_auth):
        """Delivers CalNet profile."""
        fake_auth.login(admin_uid)
        response = client.get('/api/user/by_uid/1133399')
        assert response.status_code == 200
        assert response.json['csid'] == '800700600'
        assert response.json['uid'] == '1133399'


class TestUniversityDeptMember:
    """University Dept Member API."""

    @classmethod
    def _api_add(
            cls,
            client,
            role='advisor',
            automate_membership=False,
            expected_status_code=200,
    ):
        params = {
            'deptCode': 'ZZZZZ',
            'uid': coe_advisor_uid,
            'role': role,
            'automateMembership': automate_membership,
        }
        response = client.post(
            '/api/user/dept_membership/add',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_update(
            cls,
            client,
            role=None,
            automate_membership=None,
            expected_status_code=200,
    ):
        params = {
            'deptCode': 'ZZZZZ',
            'uid': coe_advisor_uid,
            'role': role,
            'automateMembership': automate_membership,
        }
        response = client.post(
            '/api/user/dept_membership/update',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_delete(cls, client, expected_status_code=200):
        university_dept_id = UniversityDept.find_by_dept_code('ZZZZZ').id
        authorized_user_id = AuthorizedUser.find_by_uid(coe_advisor_uid).id
        response = client.delete(
            f'/api/user/dept_membership/delete/{university_dept_id}/{authorized_user_id}',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_add_university_dept_membership_not_authenticated(self, client):
        """Returns 401 when unauthenticated user attempts to add."""
        self._api_add(client, expected_status_code=401)

    def test_add_university_dept_membership_not_authorized(self, client, fake_auth):
        """Returns 401 when non-admin attempts to add."""
        fake_auth.login(asc_advisor_uid)
        self._api_add(client, expected_status_code=401)

    def test_add_university_dept_membership(self, client, fake_auth):
        """Creates a UniversityDeptMember record."""
        fake_auth.login(admin_uid)
        membership = self._api_add(client)
        assert membership['universityDeptId'] == UniversityDept.find_by_dept_code('ZZZZZ').id
        assert membership['authorizedUserId'] == AuthorizedUser.find_by_uid(coe_advisor_uid).id
        assert membership['role'] == 'advisor'

    def test_update_university_dept_membership_not_authenticated(self, client):
        """Returns 401 when unauthenticated user attempts to update."""
        self._api_update(client, expected_status_code=401)

    def test_update_university_dept_membership_not_authorized(self, client, fake_auth):
        """Returns 401 when non-admin attempts to update."""
        fake_auth.login(asc_advisor_uid)
        self._api_update(client, expected_status_code=401)

    def test_update_nonexistant_university_dept_membership(self, client, fake_auth):
        """Returns 404 when attempting to update a nonexistant UniversityDeptMember record."""
        fake_auth.login(admin_uid)
        self._api_update(client, expected_status_code=400)

    def test_update_university_dept_membership(self, client, fake_auth):
        """Updates a UniversityDeptMember record."""
        fake_auth.login(admin_uid)
        self._api_add(client)
        membership = self._api_update(client, role='director')
        assert membership['universityDeptId'] == UniversityDept.find_by_dept_code('ZZZZZ').id
        assert membership['authorizedUserId'] == AuthorizedUser.find_by_uid(coe_advisor_uid).id
        assert membership['role'] == 'director'

    def test_delete_university_dept_membership_not_authenticated(self, client):
        """Returns 401 when unauthenticated user attempts to delete."""
        self._api_delete(client, 401)

    def test_delete_university_dept_membership_not_authorized(self, client, fake_auth):
        """Returns 401 when non-admin attempts to delete."""
        fake_auth.login(asc_advisor_uid)
        self._api_delete(client, 401)

    def test_delete_nonexistant_university_dept_membership(self, client, fake_auth):
        """Returns 404 when attempting to delete a nonexistant UniversityDeptMember record."""
        fake_auth.login(admin_uid)
        self._api_delete(client, 404)

    def test_delete_university_dept_membership(self, client, fake_auth):
        """Deletes a UniversityDeptMember record."""
        fake_auth.login(admin_uid)
        membership = self._api_add(client)
        university_dept_id = membership['universityDeptId']
        authorized_user_id = membership['authorizedUserId']
        response = self._api_delete(client)
        assert response.get('message') == (
            f'University dept membership deleted: university_dept_id={university_dept_id} authorized_user_id={authorized_user_id}'
        )


class TestUsers:
    """Users API."""

    def test_not_authenticated(self, client):
        """Returns 'unauthorized' response status if user is not authenticated."""
        response = client.post('/api/users')
        assert response.status_code == 401
        response = client.get('/api/users/departments')
        assert response.status_code == 401

    def test_unauthorized(self, client, fake_auth):
        """Returns 'unauthorized' response status if user is not admin."""
        fake_auth.login(coe_advisor_uid)
        response = client.post('/api/users')
        assert response.status_code == 401
        response = client.get('/api/users/departments')
        assert response.status_code == 401

    def test_unauthorized_scheduler(self, client, fake_auth):
        """Returns 'unauthorized' response status if user is a scheduler."""
        fake_auth.login(coe_scheduler_uid)
        response = client.post('/api/users')
        assert response.status_code == 401

    def test_authorized(self, app, client, fake_auth):
        """Returns a well-formed response including cached, uncached, and deleted users."""
        fake_auth.login(admin_uid)
        response = client.post(
            '/api/users',
            data=json.dumps({
                'deptCode': 'QCADV',
            }),
            content_type='application/json',
        )
        assert response.status_code == 200
        users = response.json['users']
        assert len(users) == 4

    def test_drop_in_advisors_for_dept(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_scheduler_uid)
            response = client.get('/api/users/drop_in_advisors/qcadv')
            assert response.status_code == 200
            assert len(response.json) == 1
            assert response.json[0]['dropInAdvisorStatus'][0] == {
                'available': True,
                'deptCode': 'QCADV',
                'status': None,
            }

    def test_get_departments(self, client, fake_auth):
        """Get all departments."""
        fake_auth.login(admin_uid)
        response = client.get('/api/users/departments')
        assert response.status_code == 200


class TestGetAdminUsers:
    """Get Admin Users API."""

    @classmethod
    def _api_admin_users(
            cls,
            client,
            ignore_deleted,
            sort_by='lastName',
            sort_descending=False,
            expected_status_code=200,
    ):
        params = {
            'ignoreDeleted': ignore_deleted,
            'sortBy': sort_by,
            'sortDescending': sort_descending,
        }
        response = client.post(
            '/api/users/admins',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Returns 'unauthorized' response status if user is not authenticated."""
        self._api_admin_users(client, ignore_deleted=True, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Returns 'unauthorized' response status if user is not admin."""
        fake_auth.login(coe_advisor_uid)
        self._api_admin_users(client, ignore_deleted=True, expected_status_code=401)

    def test_get_admin_users(self, client, fake_auth):
        """Get all admin users."""
        fake_auth.login(admin_uid)
        api_json = self._api_admin_users(client, ignore_deleted=False, expected_status_code=200)
        users = api_json['users']
        user_count = len(users)
        assert user_count
        assert user_count == api_json['totalUserCount']
        assert next((u for u in users if u['deletedAt']), None) is not None

    def test_get_admin_users_ignore_deleted(self, client, fake_auth):
        """Get admin users, ignoring deleted users."""
        fake_auth.login(admin_uid)
        api_json = self._api_admin_users(client, ignore_deleted=True, expected_status_code=200)
        users = api_json['users']
        user_count = len(users)
        assert user_count
        assert user_count == api_json['totalUserCount']
        assert next((u for u in users if u['deletedAt']), None) is None


class TestManageSchedulers:

    @classmethod
    def _add_scheduler(cls, client, uid, dept_code, expected_status_code=200):
        response = client.post(
            f'/api/users/appointment_schedulers/{dept_code}/add',
            data=json.dumps({'uid': uid}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _remove_scheduler(cls, client, uid, dept_code, expected_status_code=200):
        response = client.post(
            f'/api/users/appointment_schedulers/{dept_code}/remove',
            data=json.dumps({'uid': uid}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_scheduler_list(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            response = client.get('/api/users/appointment_schedulers')
            assert len(response.json) == 1
            assert response.json[0]['code'] == 'QCADV'
            assert len(response.json[0]['schedulers']) == 1
            assert response.json[0]['schedulers'][0]['csid']
            assert response.json[0]['schedulers'][0]['firstName']
            assert response.json[0]['schedulers'][0]['lastName']
            assert response.json[0]['schedulers'][0]['uid'] == l_s_college_scheduler_uid

    def test_scheduler_list_respects_drop_in_configs(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(l_s_college_advisor_uid)
            response = client.get('/api/users/appointment_schedulers')
            assert response.status_code == 200
            assert len(response.json) == 0

    def test_scheduler_list_requires_advisor(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_scheduler_uid)
            assert client.get('/api/users/appointment_schedulers').status_code == 401

    def test_scheduler_list_requires_advising_data_access(self, app, client, fake_auth):
        """Denies list access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            assert client.get('/api/users/appointment_schedulers').status_code == 401

    def test_remove_then_add_scheduler(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            response = client.get('/api/users/appointment_schedulers')
            assert len(response.json[0]['schedulers']) == 1

            response = self._remove_scheduler(client, l_s_college_scheduler_uid, 'QCADV')
            std_commit(allow_test_environment=True)
            assert len(response['schedulers']) == 0

            response = client.get('/api/users/appointment_schedulers')
            assert len(response.json[0]['schedulers']) == 0

            response = self._add_scheduler(client, l_s_college_scheduler_uid, 'QCADV')
            std_commit(allow_test_environment=True)
            assert len(response['schedulers']) == 1
            assert response['schedulers'][0]['uid'] == l_s_college_scheduler_uid

            response = client.get('/api/users/appointment_schedulers')
            assert len(response.json[0]['schedulers']) == 1
            assert response.json[0]['schedulers'][0]['uid'] == l_s_college_scheduler_uid

    def test_add_then_remove_scheduler(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            response = client.get('/api/users/appointment_schedulers')
            assert len(response.json[0]['schedulers']) == 1

            response = self._add_scheduler(client, coe_scheduler_uid, 'QCADV')
            assert len(response['schedulers']) == 2
            assert coe_scheduler_uid in [s['uid'] for s in response['schedulers']]
            assert l_s_college_scheduler_uid in [s['uid'] for s in response['schedulers']]
            response = client.get('/api/users/appointment_schedulers')
            assert len(response.json[0]['schedulers']) == 2
            assert coe_scheduler_uid in [s['uid'] for s in response.json[0]['schedulers']]
            assert l_s_college_scheduler_uid in [s['uid'] for s in response.json[0]['schedulers']]

            response = self._remove_scheduler(client, coe_scheduler_uid, 'QCADV')
            assert len(response['schedulers']) == 1
            assert response['schedulers'][0]['uid'] == l_s_college_scheduler_uid
            response = client.get('/api/users/appointment_schedulers')
            assert len(response.json[0]['schedulers']) == 1
            assert response.json[0]['schedulers'][0]['uid'] == l_s_college_scheduler_uid

    def test_add_remove_scheduler_requires_advisor(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(coe_scheduler_uid)
            self._add_scheduler(client, coe_scheduler_uid, 'QCADV', expected_status_code=401)
            self._remove_scheduler(client, l_s_college_scheduler_uid, 'QCADV', expected_status_code=401)

    def test_add_remove_scheduler_requires_advising_data_access(self, app, client, fake_auth):
        """Denies add/remove to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            self._add_scheduler(client, coe_scheduler_uid, 'COENG', expected_status_code=401)
            self._remove_scheduler(client, coe_scheduler_uid, 'COENG', expected_status_code=401)

    def test_add_remove_scheduler_requires_dept_membership(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(coe_advisor_uid)
            self._add_scheduler(client, coe_scheduler_uid, 'QCADV', expected_status_code=403)
            self._remove_scheduler(client, l_s_college_scheduler_uid, 'QCADV', expected_status_code=403)

    def test_add_remove_scheduler_respects_drop_in_config(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(l_s_college_advisor_uid)
            self._add_scheduler(client, coe_scheduler_uid, 'QCADV', expected_status_code=403)
            self._remove_scheduler(client, l_s_college_scheduler_uid, 'QCADV', expected_status_code=403)

    def test_add_nonexistent_scheduler_reports_error(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            self._add_scheduler(client, '999999999999999999', 'QCADV', expected_status_code=400)

    def test_remove_non_scheduler_reports_error(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            self._remove_scheduler(client, coe_advisor_uid, 'QCADV', expected_status_code=400)


class TestUserSearch:

    @classmethod
    def _api_users_autocomplete(
            cls,
            client,
            snippet=None,
            expected_status_code=200,
    ):
        response = client.post(
            '/api/users/autocomplete',
            data=json.dumps({'snippet': snippet}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Deny anonymous user."""
        assert self._api_users_autocomplete(client, 'Jo', expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Deny non-admin user."""
        assert self._api_users_autocomplete(client, 'Jo', expected_status_code=401)

    def test_user_search_by_uid(self, client, fake_auth):
        """Search users by UID."""
        fake_auth.login(admin_uid)
        assert len(self._api_users_autocomplete(client, '339')) >= 2

    def test_search_for_deleted_user_by_uid(self, client, fake_auth):
        """Search for deleted user by UID."""
        fake_auth.login(admin_uid)
        users = self._api_users_autocomplete(client, '3333')
        assert len(users) == 1
        assert users[0]['uid'] == '33333'

    def test_search_for_deleted_user_by_name(self, client, fake_auth):
        """Search for deleted user by name."""
        fake_auth.login(admin_uid)
        calnet_users = list(calnet.get_calnet_users_for_uids(app, ['33333']).values())
        first_name = calnet_users[0]['firstName']
        last_name = calnet_users[0]['lastName']
        api_json = self._api_users_autocomplete(client, f'{first_name[:2]} {last_name[:3]}')
        assert len(api_json) == 1

    def test_space_separated_names_is_required(self, client, fake_auth):
        """When search users, names must be separated by spaces."""
        fake_auth.login(admin_uid)
        calnet_users = list(calnet.get_calnet_users_for_uids(app, ['1081940']).values())
        first_name = calnet_users[0]['firstName']
        last_name = calnet_users[0]['lastName']
        api_json = self._api_users_autocomplete(client, f'{first_name}{last_name}')
        assert len(api_json) == 0

    def test_user_search_by_last_name(self, client, fake_auth):
        """Search users by last name."""
        fake_auth.login(admin_uid)
        calnet_users = list(calnet.get_calnet_users_for_uids(app, ['1081940']).values())
        last_name = calnet_users[0]['lastName']
        api_json = self._api_users_autocomplete(client, f' {last_name[:3]}  ')
        assert len(api_json) == 1
        assert api_json[0]['uid'] == calnet_users[0]['uid']

    def test_user_search_by_name(self, client, fake_auth):
        """Search users by UID."""
        fake_auth.login(admin_uid)
        calnet_users = list(calnet.get_calnet_users_for_uids(app, ['1081940']).values())
        # Case-insensitive search
        first_name = calnet_users[0]['firstName'].lower()
        last_name = calnet_users[0]['lastName'].lower()
        api_json = self._api_users_autocomplete(client, f' {first_name[:2]} {last_name[:3]}  ')
        assert len(api_json) == 1
        assert api_json[0]['uid'] == calnet_users[0]['uid']


class TestDemoMode:

    def test_set_demo_mode_not_authenticated(self, app, client):
        """Require authentication."""
        with override_config(app, 'DEMO_MODE_AVAILABLE', True):
            assert client.post('/api/user/demo_mode').status_code == 401

    def test_demo_mode_unavailable(self, app, client, fake_auth):
        """Return 404 when dev_auth is not enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            # Enable dev_auth to confirm that it is ignored
            with override_config(app, 'DEMO_MODE_AVAILABLE', False):
                fake_auth.login(admin_uid)
                assert client.post('/api/user/demo_mode').status_code == 404

    def test_set_demo_mode(self, app, client, fake_auth):
        """Both admin and advisor can toggle demo mode."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            # Disable dev_auth to confirm that it is ignored
            with override_config(app, 'DEMO_MODE_AVAILABLE', True):
                for uid in admin_uid, coe_advisor_uid:
                    fake_auth.login(uid)
                    for in_demo_mode in [True, False]:
                        response = client.post(
                            '/api/user/demo_mode',
                            data=json.dumps({'demoMode': in_demo_mode}),
                            content_type='application/json',
                        )
                        assert response.status_code == 200
                        assert response.json['inDemoMode'] is in_demo_mode
                        user = AuthorizedUser.find_by_uid(uid)
                        assert user.in_demo_mode is in_demo_mode


class TestDownloadUsers:

    def test_not_authenticated(self, client):
        """Returns 'unauthorized' response status if user is not authenticated."""
        response = client.get('/api/users/csv')
        assert response.status_code == 401

    def test_unauthorized(self, client, fake_auth):
        """Returns 'unauthorized' response status if user is not admin."""
        fake_auth.login(coe_advisor_uid)
        response = client.get('/api/users/csv')
        assert response.status_code == 401

    def test_unauthorized_scheduler(self, client, fake_auth):
        """Returns 'unauthorized' response status if user is a scheduler."""
        fake_auth.login(coe_scheduler_uid)
        response = client.get('/api/users/csv')
        assert response.status_code == 401

    def test_authorized(self, client, fake_auth):
        """Returns a well-formed response."""
        fake_auth.login(admin_uid)
        response = client.get('/api/users/csv')
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = str(response.data)
        for snippet in [
            'last_name,first_name,uid,title,email,department,appointment_roles,can_access_advising_data,can_access_canvas_data,is_blocked,\
last_login',
            'Balthazar,Milicent,53791,,,{ QCADVMAJ: director (automated=False) },{ QCADVMAJ: Drop-in Advisor },True,True,False',
            'Balthazar,Milicent,53791,,,{ QCADV: director (automated=False) },{ QCADV: Drop-in Advisor },True,True,False',
            'Visor,COE Add,90412,,,{ UWASC: director (automated=False) },{ },True,True,False',
            'Visor,COE Add,90412,,,{ COENG: advisor (automated=True) },{ COENG: Drop-in Advisor },True,True,False',
        ]:
            assert str(snippet) in csv


class TestToggleDropInAppointmentStatus:

    @classmethod
    def _api_drop_in_advisors(
            cls,
            client,
            dept_code,
            expected_status_code=200,
    ):
        response = client.get(f'/api/users/drop_in_advisors/{dept_code}')
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_drop_in_advising_available(
            cls,
            client,
            dept_code,
            uid,
            expected_status_code=200,
    ):
        response = client.post(
            f'/api/user/{uid}/drop_in_advising/{dept_code}/available',
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_drop_in_advising_unavailable(
            cls,
            client,
            dept_code,
            uid,
            expected_status_code=200,
    ):
        response = client.post(
            f'/api/user/{uid}/drop_in_advising/{dept_code}/unavailable',
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            self._api_drop_in_advising_unavailable(
                client=client,
                dept_code='QCADV',
                expected_status_code=401,
                uid=l_s_college_drop_in_advisor_uid,
            )

    def test_denies_non_drop_in_advisor(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            self._api_drop_in_advising_unavailable(
                client=client,
                dept_code='QCADV',
                expected_status_code=401,
                uid=l_s_college_drop_in_advisor_uid,
            )

    def test_denies_scheduler_in_other_department(self, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG', 'QCADV']):
            fake_auth.login(coe_scheduler_uid)
            self._api_drop_in_advising_unavailable(
                client=client,
                dept_code='QCADV',
                expected_status_code=403,
                uid=l_s_college_drop_in_advisor_uid,
            )

    def test_denies_advisor_toggling_another_advisor(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            self._api_drop_in_advising_unavailable(
                client=client,
                dept_code='QCADV',
                expected_status_code=403,
                uid=asc_advisor_uid,
            )

    def test_handles_drop_in_status_not_found(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            self._api_drop_in_advising_unavailable(
                client=client,
                dept_code='COENG',
                expected_status_code=404,
                uid=l_s_college_drop_in_advisor_uid,
            )

    def test_advisor_can_toggle_own_status(self, client, fake_auth):
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            advisor = AuthorizedUser.find_by_uid(l_s_college_drop_in_advisor_uid)
            uid = advisor.uid
            fake_auth.login(uid)
            response = client.post(f'/api/user/{uid}/drop_in_advising/QCADV/unavailable')
            assert response.status_code == 200
            api_json = self._api_drop_in_advisors(client, dept_code)
            assert len(api_json) == 1
            expected = {
                'deptCode': dept_code,
                'available': False,
                'status': None,
            }
            assert expected in api_json[0]['dropInAdvisorStatus']
            self._api_drop_in_advising_available(
                client=client,
                dept_code='QCADV',
                uid=uid,
            )
            expected = {
                'deptCode': dept_code,
                'available': True,
                'status': None,
            }
            assert expected in client.get('/api/profile/my').json['dropInAdvisorStatus']

    def test_scheduler_can_toggle_advisor_status(self, client, fake_auth):
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(l_s_college_scheduler_uid)
            # Assert that response status is 200.
            self._api_drop_in_advising_unavailable(
                client=client,
                dept_code=dept_code,
                uid=l_s_college_drop_in_advisor_uid,
            )
            api_json = self._api_drop_in_advisors(client, dept_code)
            assert len(api_json) == 1
            assert api_json[0]['available'] is False
            expected = {
                'deptCode': dept_code,
                'available': False,
                'status': None,
            }
            assert expected in api_json[0]['dropInAdvisorStatus']
            # Assert that response status is 200.
            self._api_drop_in_advising_available(
                client=client,
                dept_code=dept_code,
                uid=l_s_college_drop_in_advisor_uid,
            )
            api_json = self._api_drop_in_advisors(client, dept_code)
            assert len(api_json) == 1
            assert api_json[0]['available'] is True
            expected = {
                'deptCode': dept_code,
                'available': True,
                'status': None,
            }
            assert expected in api_json[0]['dropInAdvisorStatus']

    def test_unreserve_appointments_when_advisor_goes_off_duty(self, app, client, fake_auth):
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(l_s_college_scheduler_uid)

            # Put advisor on duty.
            self._api_drop_in_advising_available(
                client=client,
                dept_code=dept_code,
                uid=l_s_college_drop_in_advisor_uid,
            )
            # Reserve a couple of appointments for the advisor via different paths.
            details = 'Concurrent enrollment in beauty school'
            pre_reserved_appointment = AppointmentTestUtil.create_drop_in_appointment(
                client=client,
                dept_code=dept_code,
                details=details,
                advisor_uid=l_s_college_drop_in_advisor_uid,
            )
            pre_reserved_appointment_id = pre_reserved_appointment['id']
            subsequently_reserved_appointment = AppointmentTestUtil.create_drop_in_appointment(client, dept_code, details)
            subsequently_reserved_appointment_id = subsequently_reserved_appointment['id']
            AppointmentTestUtil.reserve_appointment(client, subsequently_reserved_appointment_id, l_s_college_drop_in_advisor_uid)

            # Verify reserved appointment data.
            waitlist = client.get(f'/api/appointments/waitlist/{dept_code}').json['waitlist']
            pre_reserved_appointment_feed = next(a for a in waitlist['unresolved'] if a['id'] == pre_reserved_appointment_id)
            assert pre_reserved_appointment_feed['status'] == 'reserved'
            assert pre_reserved_appointment_feed['statusBy']['uid'] == l_s_college_scheduler_uid
            assert pre_reserved_appointment_feed['advisorUid'] == l_s_college_drop_in_advisor_uid
            subsequently_reserved_appointment_feed =\
                next(appt for appt in waitlist['unresolved'] if appt['id'] == subsequently_reserved_appointment_id)
            assert subsequently_reserved_appointment_feed['status'] == 'reserved'
            assert subsequently_reserved_appointment_feed['statusBy']['uid'] == l_s_college_scheduler_uid
            assert subsequently_reserved_appointment_feed['advisorUid'] == l_s_college_drop_in_advisor_uid

            # Take advisor off duty.
            self._api_drop_in_advising_unavailable(
                client=client,
                dept_code=dept_code,
                uid=l_s_college_drop_in_advisor_uid,
            )
            # Verify appointments are back to waiting.
            waitlist = client.get(f'/api/appointments/waitlist/{dept_code}').json['waitlist']
            pre_reserved_appointment_feed = next(appt for appt in waitlist['unresolved'] if appt['id'] == pre_reserved_appointment_id)
            assert pre_reserved_appointment_feed['status'] == 'waiting'
            assert pre_reserved_appointment_feed['statusBy']['uid'] == l_s_college_scheduler_uid
            assert pre_reserved_appointment_feed['advisorUid'] is None
            subsequently_reserved_appointment_feed = next(a for a in waitlist['unresolved'] if a['id'] == subsequently_reserved_appointment_id)
            assert subsequently_reserved_appointment_feed['status'] == 'waiting'
            assert subsequently_reserved_appointment_feed['statusBy']['uid'] == l_s_college_scheduler_uid
            assert subsequently_reserved_appointment_feed['advisorUid'] is None

            # Clean up.
            Appointment.delete(pre_reserved_appointment_id)
            Appointment.delete(subsequently_reserved_appointment_id)


class TestUserUpdate:

    @classmethod
    def _profile_object(
            cls,
            uid,
            automate_degree_progress_permission=False,
            authorized_user_id=None,
            can_access_advising_data=True,
            can_access_canvas_data=True,
            is_admin=False,
            is_blocked=False,
    ):
        return {
            'automateDegreeProgressPermission': automate_degree_progress_permission,
            'canAccessAdvisingData': can_access_advising_data,
            'canAccessCanvasData': can_access_canvas_data,
            'id': authorized_user_id,
            'isAdmin': is_admin,
            'isBlocked': is_blocked,
            'uid': uid,
        }

    @classmethod
    def _api_create_or_update(
            cls,
            client,
            profile,
            expected_status_code=200,
            memberships=(),
            delete_action=None,
    ):
        response = client.post(
            '/api/user/create_or_update',
            data=json.dumps({
                'deleteAction': delete_action,
                'profile': profile,
                'memberships': memberships,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Authentication required."""
        self._api_create_or_update(
            client,
            profile=self._profile_object(uid='2040'),
            expected_status_code=401,
        )

    def test_unauthorized(self, client, fake_auth):
        """Admin required."""
        fake_auth.login(coe_advisor_uid)
        self._api_create_or_update(
            client,
            profile=self._profile_object(uid='2040'),
            expected_status_code=401,
        )

    def test_unrecognized_uid(self, client, fake_auth):
        """Unrecognized UID."""
        fake_auth.login(admin_uid)
        self._api_create_or_update(
            client,
            profile=self._profile_object(uid='9999999999'),
            expected_status_code=400,
        )

    def test_error_when_add_existing_uid(self, client, fake_auth):
        """Raises error if UID exists."""
        fake_auth.login(admin_uid)
        self._api_create_or_update(
            client,
            profile=self._profile_object(uid=deleted_user_uid),
            expected_status_code=400,
        )

    def test_create_scheduler(self, client, fake_auth):
        """Admin creates new Scheduler."""
        fake_auth.login(admin_uid)
        uid = '900000001'
        insert_in_json_cache(
            f'calnet_user_for_uid_{uid}',
            {
                'uid': uid,
                'csid': '100000009',
            },
        )
        user = self._api_create_or_update(
            client,
            profile=self._profile_object(uid=uid),
            memberships=[
                {
                    'code': 'QCADVMAJ',
                    'role': 'scheduler',
                    'automateMembership': False,
                },
            ],
        )
        uid = user['uid']
        assert user['id']
        assert uid
        assert user['isAdmin'] is False
        assert user['isBlocked'] is False
        assert user['canAccessAdvisingData'] is True
        assert user['canAccessCanvasData'] is True
        assert len(user['departments']) == 1

        qcadvmaj = next(d for d in user['departments'] if d['code'] == 'QCADVMAJ')
        assert qcadvmaj['role'] == 'scheduler'
        assert qcadvmaj['automateMembership'] is False

        # Clean up
        AuthorizedUser.delete(uid)

    def test_update_advisor(self, client, fake_auth):
        """Add Advisor to another department, assign Scheduler role."""
        fake_auth.login(admin_uid)
        # First, create advisor
        uid = '9000000002'
        insert_in_json_cache(
            f'calnet_user_for_uid_{uid}',
            {
                'uid': uid,
                'csid': '200000009',
            },
        )
        user = self._api_create_or_update(
            client,
            profile=self._profile_object(automate_degree_progress_permission=True, uid=uid),
            memberships=[
                {
                    'code': 'COENG',
                    'role': 'advisor',
                    'automateMembership': True,
                },
            ],
        )
        user_id = user['id']
        assert user_id
        assert user['uid'] == uid
        assert user['automateDegreeProgressPermission'] is True

        departments = user['departments']
        assert len(departments) == 1
        assert departments[0]['code'] == 'COENG'
        assert departments[0]['role'] == 'advisor'
        assert departments[0]['automateMembership'] is True

        # Next, remove advisor from 'QCADV' and add him to 'QCADVMAJ', as "Scheduler".
        authorized_user_id = AuthorizedUser.get_id_per_uid(uid)
        self._api_create_or_update(
            client,
            profile=self._profile_object(
                uid=uid,
                authorized_user_id=authorized_user_id,
            ),
            memberships=[
                {
                    'code': 'QCADVMAJ',
                    'role': 'scheduler',
                    'automateMembership': False,
                },
            ],
        )
        std_commit(allow_test_environment=True)

        user = AuthorizedUser.find_by_uid(uid)
        assert len(user.drop_in_departments) == 0
        assert len(user.department_memberships) == 1
        assert user.department_memberships[0].university_dept.dept_code == 'QCADVMAJ'
        assert user.department_memberships[0].automate_membership is False

    def test_update_deleted_user(self, client, fake_auth):
        """Update and then un-delete user."""
        fake_auth.login(admin_uid)
        # First, create advisor
        uid = '9000000003'
        insert_in_json_cache(
            f'calnet_user_for_uid_{uid}',
            {
                'uid': uid,
                'csid': '300000009',
            },
        )
        profile = self._profile_object(uid=uid, is_admin=True)
        user = self._api_create_or_update(client, profile=profile, memberships=[])
        profile['id'] = user['id']

        # Next, delete the user.
        self._api_create_or_update(client, profile=profile, delete_action=True)
        std_commit(allow_test_environment=True)

        user = AuthorizedUser.find_by_uid(uid, ignore_deleted=False)
        assert user.deleted_at

        # Finally, un-delete the user.
        self._api_create_or_update(client, profile=profile, delete_action=False)
        std_commit(allow_test_environment=True)

        user = AuthorizedUser.find_by_uid(uid, ignore_deleted=False)
        assert not user.deleted_at

    def test_change_drop_in_advisor_to_scheduler(self, client, fake_auth):
        """A drop-in advisor loses their appointments and drop-in status when they become a scheduler."""
        fake_auth.login(admin_uid)

        user = AuthorizedUser.find_by_uid(l_s_college_drop_in_advisor_uid)
        assert len(user.drop_in_departments) == 2

        appointments = Appointment.query.filter_by(advisor_uid=l_s_college_drop_in_advisor_uid, status='reserved').all()
        assert len(appointments) == 0

        # Reserve a new appointment
        advisor_attrs = {
            'id': user.id,
            'uid': l_s_college_drop_in_advisor_uid,
            'name': 'Cornelius Conway III',
            'role': 'Advisor',
            'deptCodes': ['QCADV'],
        }
        appointment = Appointment.create(
            appointment_type='Drop-in',
            created_by=advisor_attrs['id'],
            dept_code='QCADV',
            details='Mine!',
            student_sid='7890123456',
            advisor_attrs=advisor_attrs,
        )
        assert appointment.status == 'reserved'
        assert appointment.advisor_uid == advisor_attrs['uid']
        assert appointment.advisor_name == advisor_attrs['name']
        assert appointment.advisor_role == advisor_attrs['role']
        assert appointment.advisor_dept_codes == advisor_attrs['deptCodes']

        appointments = Appointment.query.filter_by(advisor_uid=l_s_college_drop_in_advisor_uid, status='reserved').all()
        assert len(appointments) == 1

        self._api_create_or_update(
            client,
            profile=self._profile_object(uid=l_s_college_drop_in_advisor_uid, authorized_user_id=user.id),
            memberships=[
                {
                    'code': 'QCADV',
                    'role': 'scheduler',
                    'automateMembership': True,
                },
            ],
        )
        std_commit(allow_test_environment=True)
        user = AuthorizedUser.find_by_uid(l_s_college_drop_in_advisor_uid)
        assert len(user.drop_in_departments) == 1

        appointments = Appointment.query.filter_by(advisor_uid=l_s_college_drop_in_advisor_uid, status='reserved').all()
        assert len(appointments) == 0

        appointment = Appointment.find_by_id(appointment.id)
        assert appointment.status == 'waiting'
        assert appointment.advisor_uid is None
        assert appointment.advisor_name is None
        assert appointment.advisor_role is None
        assert appointment.advisor_dept_codes is None

    def test_revoke_advising_and_canvas_data_access(self, client, fake_auth):
        """Admin revokes user access to notes, appointments, and canvas data."""
        fake_auth.login(admin_uid)
        uid = '900000001'
        insert_in_json_cache(
            f'calnet_user_for_uid_{uid}',
            {
                'uid': uid,
                'csid': '100000009',
            },
        )
        user = self._api_create_or_update(
            client,
            profile=self._profile_object(
                uid=uid,
                can_access_advising_data=False,
                can_access_canvas_data=False,
            ),
            memberships=[
                {
                    'code': 'QCADVMAJ',
                    'role': 'scheduler',
                    'automateMembership': False,
                },
            ],
        )
        uid = user['uid']
        assert user['id']
        assert uid
        assert user['isAdmin'] is False
        assert user['isBlocked'] is False
        assert user['canAccessAdvisingData'] is False
        assert user['canAccessCanvasData'] is False
        assert len(user['departments']) == 1


class TestDropInAdvising:

    @classmethod
    def _api_toggle_drop_in_advising(
            cls,
            client,
            dept_code,
            action,
            expected_status_code=200,
    ):
        response = client.post(
            f'/api/user/drop_in_advising/{dept_code}/{action}',
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_set_drop_in_status(
            cls,
            client,
            dept_code,
            status,
            expected_status_code=200,
    ):
        response = client.post(
            f'/api/user/drop_in_advising/{dept_code}/status',
            content_type='application/json',
            data=json.dumps({'status': status}),
        )
        assert response.status_code == expected_status_code
        return response.json

    def _expect_unauthenticated(self, client):
        self._api_toggle_drop_in_advising(
            client,
            dept_code='COENG',
            action='enable',
            expected_status_code=401,
        )
        self._api_toggle_drop_in_advising(
            client,
            dept_code='COENG',
            action='disable',
            expected_status_code=401,
        )
        self._api_set_drop_in_status(
            client,
            dept_code='COENG',
            status='Coffee is for closers',
            expected_status_code=401,
        )

    def test_not_authenticated(self, client):
        """Authentication required."""
        self._expect_unauthenticated(client)

    def test_non_advisor(self, client, fake_auth):
        """Prevents advisor from toggling for a department they aren't an advisor for."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(coe_advisor_uid)
            self._expect_unauthenticated(client)

    def test_non_drop_in_dept(self, client, fake_auth):
        """Prevents advisor from toggling when dept is not configured for drop-in advising."""
        fake_auth.login(coe_advisor_uid)
        self._expect_unauthenticated(client)

    def test_toggle_drop_in_advising(self, client, fake_auth):
        """Allows advisor to disable and enable their drop-in advising membership."""
        dept_code = 'COENG'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(coe_advisor_uid)
            user = AuthorizedUser.find_by_uid(coe_advisor_uid)
            assert len(user.drop_in_departments) == 1

            response = self._api_toggle_drop_in_advising(
                client,
                dept_code='COENG',
                action='disable',
            )
            std_commit(allow_test_environment=True)
            user = AuthorizedUser.find_by_uid(coe_advisor_uid)
            assert len(user.drop_in_departments) == 0

            response = self._api_toggle_drop_in_advising(
                client,
                dept_code=dept_code,
                action='enable',
            )
            std_commit(allow_test_environment=True)
            assert response == {'deptCode': dept_code, 'available': False, 'status': None}
            user = AuthorizedUser.find_by_uid(coe_advisor_uid)
            assert len(user.drop_in_departments) == 1

    def disable_drop_in_advising_unassign_appointments(self, client, fake_auth):
        """When drop-in advisor with appointments cancels their drop-in membership, appointments become unassigned."""
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(l_s_college_advisor_uid)
            advisor = AuthorizedUser.find_by_uid(l_s_college_advisor_uid)
            advisor_attrs = {
                'id': advisor.id,
                'uid': l_s_college_advisor_uid,
                'name': 'Berta Blorp',
                'role': 'Advisor',
                'deptCodes': ['QCADV'],
            }
            appointment = Appointment.query.filter(status='waiting').first()
            Appointment.reserve(appointment.id, l_s_college_advisor_uid, advisor_attrs)
            assert appointment.status == 'reserved'
            assert appointment.advisor_uid == advisor_attrs['uid']
            assert appointment.advisor_name == advisor_attrs['name']
            assert appointment.advisor_role == advisor_attrs['role']
            assert appointment.advisor_dept_codes == advisor_attrs['deptCodes']

            self._api_toggle_drop_in_advising(
                client,
                dept_code=dept_code,
                action='disable',
            )
            appointment = Appointment.find_by_id(appointment.id)
            assert appointment.status == 'waiting'
            assert appointment.advisor_uid is None
            assert appointment.advisor_name is None
            assert appointment.advisor_role is None
            assert appointment.advisor_dept_codes is None

    def test_set_drop_in_status(self, client, fake_auth):
        """Allows advisor to set and unset drop-in advising status whether available or not."""
        dept_code = 'COENG'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(coe_advisor_uid)
            response = self._api_set_drop_in_status(
                client,
                dept_code='COENG',
                status='Badminton break',
                expected_status_code=200,
            )
            assert response == {'deptCode': dept_code, 'available': False, 'status': 'Badminton break'}

            response = client.post(f'/api/user/{coe_advisor_uid}/drop_in_advising/COENG/available').json
            assert response == {'deptCode': dept_code, 'available': True, 'status': 'Badminton break'}

            response = self._api_set_drop_in_status(
                client,
                dept_code='COENG',
                status='Coffee is for closers',
                expected_status_code=200,
            )
            assert response == {'deptCode': dept_code, 'available': True, 'status': 'Coffee is for closers'}

            response = self._api_set_drop_in_status(
                client,
                dept_code='COENG',
                status=None,
                expected_status_code=200,
            )
            assert response == {'deptCode': dept_code, 'available': True, 'status': None}

            response = client.post(f'/api/user/{coe_advisor_uid}/drop_in_advising/COENG/unavailable').json
            assert response == {'deptCode': dept_code, 'available': False, 'status': None}

    def test_cannot_set_drop_in_status_when_drop_in_advising_disabled(self, client, fake_auth):
        dept_code = 'COENG'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(coe_advisor_uid)
            user = AuthorizedUser.find_by_uid(coe_advisor_uid)
            assert len(user.drop_in_departments) == 1
            self._api_toggle_drop_in_advising(
                client,
                dept_code='COENG',
                action='disable',
            )
            std_commit(allow_test_environment=True)
            self._api_set_drop_in_status(
                client,
                dept_code='COENG',
                status='Coffee is for closers',
                expected_status_code=404,
            )
            self._api_toggle_drop_in_advising(
                client,
                dept_code='COENG',
                action='enable',
            )
            std_commit(allow_test_environment=True)

    def test_status_too_long(self, client, fake_auth):
        dept_code = 'COENG'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(coe_advisor_uid)
            self._api_set_drop_in_status(
                client,
                dept_code='COENG',
                status='The story had held us, round the fire, sufficiently breathless, but except the obvious remark that it was gruesome, as,\
                    on Christmas Eve in an old house, a strange tale should essentially be, I remember no comment uttered till somebody happened\
                    to say that it was the only case he had met in which such a visitation had fallen on a child.',
                expected_status_code=400,
            )

    def test_no_status_param_sent(self, client, fake_auth):
        dept_code = 'COENG'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(coe_advisor_uid)
            response = client.post(
                f'/api/user/drop_in_advising/{dept_code}/status',
                content_type='application/json',
                data=json.dumps({}),
            )
            assert response.status_code == 400
