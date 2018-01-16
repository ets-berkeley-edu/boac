import re


class TestCasAuth:
    """CAS login URL generation and redirects."""

    def test_cas_login_url(self, client):
        """Fails if the chosen UID does not match an authorized user."""
        response = client.get('/cas/login_url')
        assert response.status_code == 200
        assert re.compile('.*berkeley.edu/cas/login').match(str(response.data)) is not None

    def test_cas_callback_with_invalid_ticket(self, client):
        """Fails if CAS can not verify the ticket."""
        response = client.get('/cas/callback?ticket=is_invalid')
        assert response.status_code == 403
