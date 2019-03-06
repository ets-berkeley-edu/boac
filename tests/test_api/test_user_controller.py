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
from boac.models.cohort_filter import CohortFilter
import simplejson as json

admin_uid = '2040'
asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'


class TestUserStatusController:
    """Status API."""

    def test_anonymous_status(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/user/status')
        assert response.status_code == 200
        assert response.json['isAuthenticated'] is False

    def test_when_authenticated(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        response = client.get('/api/user/status')
        assert response.status_code == 200
        assert response.json['isAuthenticated'] is True
        assert response.json['uid'] == coe_advisor_uid
        assert isinstance(response.json['inDemoMode'], bool)


class TestUserProfile:
    """User Profile API."""

    def test_profile_not_authenticated(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        assert response.json['isAuthenticated'] is False
        assert not response.json['uid']

    def test_includes_canvas_profile_if_available(self, client, fake_auth):
        """Includes user profile info from Canvas."""
        fake_auth.login(admin_uid)
        response = client.get('/api/profile/my')
        assert response.json['isAuthenticated'] is True
        assert response.json['uid'] == admin_uid
        assert 'csid' in response.json
        assert 'firstName' in response.json
        assert 'lastName' in response.json

    def test_user_with_no_dept_membership(self, client, fake_auth):
        """Returns zero or more departments."""
        fake_auth.login(admin_uid)
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        user = response.json
        assert 'myFilteredCohorts' in user
        assert 'myCuratedCohorts' in user
        assert user['isAdmin'] is True
        assert user['isAsc'] is False
        assert user['isCoe'] is False
        assert not len(user['departments'])

    def test_department_beyond_asc(self, client, fake_auth):
        """Returns COENG director."""
        fake_auth.login('1022796')
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        user = response.json
        assert user['isAdmin'] is False
        assert user['isCoe'] is True
        assert len(user['departments']) == 1
        assert 'COENG' in user['departments']
        assert user['departments']['COENG']['isAdvisor'] is False
        assert user['departments']['COENG']['isDirector'] is True

    def test_asc_advisor_exclude_cohorts(self, client, fake_auth):
        """Returns Athletic Study Center advisor."""
        fake_auth.login(asc_advisor_uid)
        response = client.get('/api/profile/my?excludeCohorts=true')
        assert response.status_code == 200
        user = response.json
        assert 'myFilteredCohorts' not in user
        assert 'myCuratedCohorts' not in user
        assert user['isAsc'] is True
        assert 'UWASC' in user['departments']
        assert user['departments']['UWASC']['isAdvisor'] is True
        assert user['departments']['UWASC']['isDirector'] is False

    def test_other_user_profile(self, client, fake_auth):
        fake_auth.login(admin_uid)
        response = client.get('/api/profile/6446')
        assert response.json['uid'] == '6446'
        assert 'firstName' in response.json
        assert 'lastName' in response.json

    def test_other_user_profile_not_found(self, client, fake_auth):
        fake_auth.login(admin_uid)
        response = client.get('/api/profile/2549')
        assert response.status_code == 404


class TestUserById:
    """User Profile API."""

    def test_user_by_uid_not_authenticated(self, client):
        """Returns 401 when not authenticated."""
        user = AuthorizedUser.find_by_uid(asc_advisor_uid)
        response = client.get(f'/api/user/by_uid/{user.uid}')
        assert response.status_code == 401

    def test_user_by_uid(self, client, fake_auth):
        """Delivers CalNet profile."""
        fake_auth.login(admin_uid)
        user = AuthorizedUser.find_by_uid(asc_advisor_uid)
        response = client.get(f'/api/user/by_uid/{user.uid}')
        assert response.status_code == 200
        assert response.json['uid'] == asc_advisor_uid

    def test_user_by_csid_not_authenticated(self, client):
        """Returns 401 when not authenticated."""
        response = client.get(f'/api/user/by_csid/{81067873}')
        assert response.status_code == 401

    def test_user_by_csid(self, client, fake_auth):
        """Delivers CalNet profile."""
        fake_auth.login(admin_uid)
        response = client.get(f'/api/user/by_csid/{81067873}')
        assert response.status_code == 200
        assert response.json['csid'] == '81067873'


class TestMyCohorts:
    """User Profile API."""

    def test_my_cohorts(self, client, fake_auth):
        fake_auth.login(asc_advisor_uid)
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        user = response.json
        cohorts = user['myFilteredCohorts']
        assert [cohort['name'] for cohort in cohorts] == [
            'All sports',
            'Defense Backs, Active',
            'Defense Backs, All',
            'Defense Backs, Inactive',
            'Undeclared students',
        ]
        cohort = cohorts[0]
        assert cohort['isOwnedByCurrentUser'] is True
        assert 'alertCount' in cohort
        assert 'totalStudentCount' in cohort

    def test_cohort_ordering(self, client, fake_auth):
        """Order alphabetically."""
        fake_auth.login(asc_advisor_uid)
        CohortFilter.create(
            uid=asc_advisor_uid,
            name='Zebra Zealots',
            filter_criteria={
                'groupCodes': ['MTE', 'WWP'],
            },
        )
        CohortFilter.create(
            uid=asc_advisor_uid,
            name='Aardvark Admirers',
            filter_criteria={
                'groupCodes': ['MWP', 'WTE'],
            },
        )
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        cohorts = response.json['myFilteredCohorts']
        assert cohorts[0]['name'] == 'Aardvark Admirers'
        assert cohorts[-1]['name'] == 'Zebra Zealots'


class TestUserGroups:
    """User API."""

    def test_not_authenticated(self, client):
        """Returns 'unauthorized' response status if user is not authenticated."""
        response = client.get('/api/users/authorized_groups')
        assert response.status_code == 401

    def test_unauthorized(self, client, fake_auth):
        """Returns 'unauthorized' response status if user is not admin."""
        fake_auth.login(coe_advisor_uid)
        response = client.get('/api/users/authorized_groups')
        assert response.status_code == 401

    def test_authorized(self, client, fake_auth):
        """Returns a well-formed response."""
        fake_auth.login(admin_uid)
        response = client.get('/api/users/authorized_groups')
        assert response.status_code == 200
        user_groups = sorted(response.json, key=lambda g: g['code'])
        assert len(user_groups) == 4
        assert user_groups[0]['name'] == 'Admins'
        assert len(user_groups[0]['users']) == 8
        assert user_groups[1]['name'] == 'College of Engineering'
        assert len(user_groups[1]['users']) == 3
        assert user_groups[2]['name'] == 'Department of Physics'
        assert len(user_groups[2]['users']) == 1
        assert user_groups[3]['name'] == 'Athletic Study Center'
        assert len(user_groups[3]['users']) == 2


class TestDemoMode:

    def test_set_demo_mode_not_authenticated(self, client):
        """Require authentication."""
        assert client.post('/api/user/demo_mode').status_code == 401

    def test_demo_mode_unavailable(self, app, client, fake_auth):
        """Return 404 when dev_auth is not enabled."""
        fake_auth.login(admin_uid)
        app.config['DEVELOPER_AUTH_ENABLED'] = False
        response = client.post('/api/user/demo_mode')
        assert response.status_code == 404

    def test_set_demo_mode(self, client, fake_auth):
        """Both admin and advisor can toggle demo mode."""
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
