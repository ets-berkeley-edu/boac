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
from boac.models.note_template import NoteTemplate

advisor_uid = '242881'


class TestGetNoteTemplate:

    @classmethod
    def _api_note_template(cls, client, note_template_id, expected_status_code=200):
        response = client.get(f'/api/note_template/{note_template_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        creator_id = AuthorizedUser.get_id_per_uid(advisor_uid)
        note_template = NoteTemplate.create(creator_id=creator_id, title='Lost cause', subject='Expect 401')
        self._api_note_template(client=client, note_template_id=note_template.id, expected_status_code=401)

    def test_unauthorized(self, app, client, fake_auth):
        """Returns 403 if user did not create the requested note template."""
        creator_id = AuthorizedUser.get_id_per_uid(advisor_uid)
        note_template = NoteTemplate.create(creator_id=creator_id, title='Leggo my eggo', subject='I, me, mine.')
        fake_auth.login('2040')
        self._api_note_template(client=client, note_template_id=note_template.id, expected_status_code=403)

    def test_get_note_template_by_id(self, app, client, fake_auth):
        """Returns note template in JSON."""
        creator_id = AuthorizedUser.get_id_per_uid(advisor_uid)
        fake_auth.login(advisor_uid)
        title = 'Template for success'
        subject = 'Winning!'
        note_template = NoteTemplate.create(creator_id=creator_id, title=title, subject=subject)
        api_json = self._api_note_template(client=client, note_template_id=note_template.id)
        assert api_json.get('id') == note_template.id
        assert api_json.get('title') == title
        assert api_json.get('subject') == subject
        for key in ('attachments', 'body', 'topics', 'createdAt', 'updatedAt'):
            assert key in api_json
