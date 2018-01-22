from boac.models.authorized_user import AuthorizedUser
import pytest

test_uid = '6446'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


class TestAdvisorWatchlist:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/watchlist/my').status_code == 401

    def test_my_watchlist(self, authenticated_session, client):
        """Returns current_user's watchlist."""
        response = client.get('/api/watchlist/my')
        assert response.status_code == 200
        watchlist = response.json
        assert len(watchlist) == 4
        names = [student['firstName'] + ' ' + student['lastName'] for student in response.json]
        assert ['Brigitte Lin', 'Paul Farestveit', 'Paul Kerschen', 'Sandeep Jayaprakash'] == names

    def test_watchlist_add_and_remove(self, authenticated_session, client):
        """Add student to current_user's watchlist and then remove him."""
        sid = '2345678901'
        response = client.get(f'/api/watchlist/add/{sid}')
        assert response.status_code == 200
        current_user = AuthorizedUser.find_by_uid(test_uid)
        watchlist = current_user.watchlist
        assert len(watchlist) == 5
        assert sid in [s.sid for s in watchlist]

        # Next, remove from watchlist
        client.get(f'/api/watchlist/remove/{sid}')
        current_user = AuthorizedUser.find_by_uid(test_uid)
        watchlist = current_user.watchlist
        assert len(watchlist) == 4
        assert sid not in [s.sid for s in watchlist]
