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

    def test_watchlist_includes_alert_counts(self, create_alerts, authenticated_session, client):
        watchlist = client.get('/api/watchlist/my').json
        assert watchlist[0]['alertCount'] == 2
        assert 'alertCount' not in watchlist[1]
        assert 'alertCount' not in watchlist[2]
        assert 'alertCount' not in watchlist[3]

        alert_to_dismiss = client.get('/api/alerts/current/11667051').json['shown'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        watchlist = client.get('/api/watchlist/my').json
        assert watchlist[0]['alertCount'] == 1

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
