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


import json


class TestDevAuth:
    """DevAuth handling."""

    authorized_uid = '2040'

    def test_disabled(self, app, client):
        """Blocks access unless enabled."""
        app.config['DEVELOPER_AUTH_ENABLED'] = False
        response = client.post('/devauth/login')
        assert response.status_code == 404
        params = {'uid': self.authorized_uid, 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 404

    def test_password_fail(self, app, client):
        """Fails if no match on developer password."""
        app.config['DEVELOPER_AUTH_ENABLED'] = True
        params = {'uid': self.authorized_uid, 'password': 'Born 2 Lose'}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 403

    def test_authorized_user_fail(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        app.config['DEVELOPER_AUTH_ENABLED'] = True
        params = {'uid': 'A Bad Sort', 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 403

    def test_unauthorized_user(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        app.config['DEVELOPER_AUTH_ENABLED'] = True
        params = {'uid': '1015674', 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 403

    def test_known_user_with_correct_password_logs_in(self, app, client):
        """There is a happy path."""
        app.config['DEVELOPER_AUTH_ENABLED'] = True
        params = {'uid': self.authorized_uid, 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 302
        response = client.get('/api/status')
        assert response.status_code == 200
        assert response.json['uid'] == self.authorized_uid
        response = client.get('/logout')
        assert response.status_code == 200
        response = client.get('/api/status')
        assert response.status_code == 200
        assert response.json['isAnonymous']
