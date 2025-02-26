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

ce3_navcal_peer_advisor_uid = '1133400'
qcadv_advisor_uid = '53791'


class TestGetPeerAdvisingTopics:

    @classmethod
    def _api_get_peer_advising_topics(cls, client, expected_status_code=200):
        response = client.get('/api/peer_advising/note_topics')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        self._api_get_peer_advising_topics(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 if user is neither admin nor Peer Advising Manager."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_peer_advising_topics(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Delivers peer_advising_department data to authorized user."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        api_json = self._api_get_peer_advising_topics(client)
        assert len(api_json)
        assert 'Probation' in [topic['topic'] for topic in api_json]
