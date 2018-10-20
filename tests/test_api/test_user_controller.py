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


from boac.models import development_db
from boac.models.cohort_filter import CohortFilter
import pytest

asc_advisor_uid = '1081940'


@pytest.fixture()
def asc_advisor_session(fake_auth):
    fake_auth.login(asc_advisor_uid)


class TestUserProfile:
    """User Profile API."""

    def test_profile_not_authenticated(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        assert not response.json['uid']

    def test_includes_canvas_profile_if_available(self, client, fake_auth):
        """Includes user profile info from Canvas."""
        test_uid = '2040'
        fake_auth.login(test_uid)
        response = client.get('/api/profile/my')
        assert response.json['uid'] == test_uid
        assert 'firstName' in response.json
        assert 'lastName' in response.json

    def test_user_with_no_dept_membership(self, client, fake_auth):
        """Returns zero or more departments."""
        fake_auth.login('2040')
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        user = response.json
        assert user['isAdmin'] is True
        assert not len(user['departments'])

    def test_department_beyond_asc(self, client, fake_auth):
        """Returns COENG director."""
        fake_auth.login('1022796')
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        user = response.json
        assert user['isAdmin'] is False
        assert len(user['departments']) == 1
        assert 'COENG' in user['departments']
        assert user['departments']['COENG']['isAdvisor'] is False
        assert user['departments']['COENG']['isDirector'] is True

    def test_athletic_study_center_user(self, client, fake_auth):
        """Returns Athletic Study Center advisor."""
        test_uid = '1081940'
        fake_auth.login(test_uid)
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        user = response.json
        assert 'UWASC' in user['departments']
        assert user['departments']['UWASC']['isAdvisor'] is True
        assert user['departments']['UWASC']['isDirector'] is False

    def test_other_user_profile(self, client, fake_auth):
        fake_auth.login('2040')
        response = client.get('/api/profile/6446')
        assert response.json['uid'] == '6446'
        assert 'firstName' in response.json
        assert 'lastName' in response.json

    def test_other_user_profile_not_found(self, client, fake_auth):
        fake_auth.login('2040')
        response = client.get('/api/profile/2549')
        assert response.status_code == 404


class TestMyCohorts:
    """User Profile API."""

    def test_my_cohorts(self, asc_advisor_session, client):
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        cohorts = response.json['myFilteredCohorts']
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

    def test_cohort_ordering(self, client, asc_advisor_session):
        """Order alphabetically."""
        CohortFilter.create(uid=asc_advisor_uid, name='Zebra Zealots', group_codes=['MTE', 'WWP'])
        CohortFilter.create(uid=asc_advisor_uid, name='Aardvark Admirers', group_codes=['MWP', 'WTE'])
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        cohorts = response.json['myFilteredCohorts']
        assert cohorts[0]['name'] == 'Aardvark Admirers'
        assert cohorts[-1]['name'] == 'Zebra Zealots'

    def test_my_curated_cohorts(self, client, fake_auth):
        """Returns user's student curated cohorts."""
        fake_auth.login('6446')
        response = client.get('/api/profile/my')
        assert response.status_code == 200
        cohorts = response.json['myCuratedCohorts']
        assert len(cohorts) == 2
        assert 'name' in cohorts[0]
        assert 'studentCount' in cohorts[0]


class TestAllUserProfiles:
    """User Profiles API."""

    admin_uid = '2040'
    coe_advisor_uid = '1133399'

    def test_not_authenticated(self, client):
        """Returns 'unauthorized' response status if user is not authenticated."""
        response = client.get('/api/profiles/all')
        assert response.status_code == 401

    def test_disabled(self, app, client, fake_auth):
        """Blocks access unless enabled."""
        fake_auth.login(self.admin_uid)
        app.config['DEVELOPER_AUTH_ENABLED'] = False
        response = client.get('/api/profiles/all')
        assert response.status_code == 404

    def test_unauthorized(self, client, fake_auth):
        """Returns 'unauthorized' response status if user is not admin."""
        fake_auth.login(self.coe_advisor_uid)
        response = client.get('/api/profiles/all')
        assert response.status_code == 401

    def test_authorized(self, client, fake_auth):
        """Returns a well-formed response."""
        fake_auth.login(self.admin_uid)
        response = client.get('/api/profiles/all')
        assert response.status_code == 200
        assert len(response.json) == len(development_db._test_users)
