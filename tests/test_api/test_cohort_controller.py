import pytest


@pytest.fixture()
def authenticated_session(fake_auth):
    test_uid = '1133399'
    fake_auth.login(test_uid)


class TestCohortsList:
    """Cohorts list API"""

    api_path = '/api/cohorts'

    def test_not_authenticated(self, client, fixture_cohorts):
        """returns 401 if not authenticated"""
        response = client.get(TestCohortsList.api_path)
        assert response.status_code == 401

    def test_authenticated(self, authenticated_session, client, fixture_cohorts):
        """returns a well-formed response if authenticated"""
        response = client.get(TestCohortsList.api_path)
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['code'] == 'FHW'
        assert response.json[0]['name'] == 'Field Hockey - Women'
        assert response.json[0]['memberCount'] == 1


class TestCohortDetail:
    """Team detail API"""

    valid_api_path = '/api/cohort/FHW'
    invalid_api_path = '/api/cohort/XYZ'

    def test_not_authenticated(self, client, fixture_cohorts):
        """returns 401 if not authenticated"""
        response = client.get(TestCohortDetail.valid_api_path)
        assert response.status_code == 401

    def test_path_without_translation(self, authenticated_session, client, fixture_cohorts):
        """returns code as name when no code-to-name translation exists"""
        response = client.get(TestCohortDetail.invalid_api_path)
        assert response.status_code == 200
        assert response.json['code'] == 'XYZ'
        assert response.json['name'] == 'XYZ'
        assert len(response.json['members']) == 0

    def test_valid_path(self, authenticated_session, client, fixture_cohorts):
        """returns a well-formed response on a valid code if authenticated"""
        response = client.get(TestCohortDetail.valid_api_path)
        assert response.status_code == 200
        assert response.json['code'] == 'FHW'
        assert response.json['name'] == 'Field Hockey - Women'
        assert len(response.json['members']) == 1
        assert response.json['members'][0]['name'] == 'Brigitte Lin'
        assert response.json['members'][0]['uid'] == '61889'
        assert response.json['members'][0]['avatar_url'] == 'https://calspirit.berkeley.edu/oski/images/oskibio.jpg'
