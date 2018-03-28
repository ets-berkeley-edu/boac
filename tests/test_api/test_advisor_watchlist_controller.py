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


import pytest
import simplejson as json

test_uid = '6446'


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


@pytest.fixture()
def authenticated_session_empty_watchlist(fake_auth):
    fake_auth.login('2040')


class TestAdvisorWatchlist:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/groups/my').status_code == 401

    def test_my_watchlist(self, authenticated_session, client):
        """Returns current_user's watchlist."""
        response = client.get('/api/groups/my')
        assert response.status_code == 200
        groups = response.json
        assert len(groups) == 1
        students = groups[0]['students']
        names = [student['firstName'] + ' ' + student['lastName'] for student in students]
        assert ['Brigitte Lin', 'Paul Farestveit', 'Paul Kerschen', 'Sandeep Jayaprakash'] == names

    def test_empty_watchlist(self, authenticated_session_empty_watchlist, client):
        """Returns current_user's watchlist."""
        response = client.get('/api/watchlist/my')
        assert response.status_code == 200
        assert response.json == []

    def test_watchlist_includes_alert_counts(self, create_alerts, authenticated_session, client):
        groups = client.get('/api/groups/my').json
        students = groups[0]['students']
        assert students[0]['alertCount'] == 2
        assert 'alertCount' not in students[1]
        assert 'alertCount' not in students[2]
        assert 'alertCount' not in students[3]

        alert_to_dismiss = client.get('/api/alerts/current/11667051').json['shown'][0]['id']
        client.get('/api/alerts/' + str(alert_to_dismiss) + '/dismiss')
        groups = client.get('/api/groups/my').json
        assert groups[0]['students'][0]['alertCount'] == 1

    def test_create_add_remove_and_delete(self, authenticated_session, client):
        """Add student to current_user's watchlist and then remove him."""
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
        groups = client.get('/api/groups/my').json
        assert len(groups)
        assert groups[0]['name'] == name
        assert groups[0]['students'][0]['sid'] == sid
        # Remove student
        response = client.get(f'/api/group/{group_id}/remove_student/{sid}')
        assert response.status_code == 200
        group = client.get(f'/api/group/{group_id}').json
        assert group['name'] == name
        assert not len(group['students'])
        # Delete group
        response = client.delete(f'/api/group/delete/{group_id}')
        assert response.status_code == 200
        # Verify
        response = client.get(f'/api/group/{group_id}')
        assert response.status_code == 404
