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
import simplejson as json

advisor_uid = '1133399'
student = {
    'sid': '11667051',
    'uid': '61889',
}


class TestCreateNotes:

    @classmethod
    def _api_note_create(cls, client, author_id, sid, subject, body, expected_status_code=200):
        data = {
            'authorId': author_id,
            'sid': sid,
            'subject': subject,
            'body': body,
        }
        response = client.post('/api/notes/create', data=json.dumps(data), content_type='application/json')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        advisor = AuthorizedUser.find_by_uid(advisor_uid)
        assert self._api_note_create(
            client,
            author_id=advisor.id,
            sid=student['sid'],
            subject='Rusholme Ruffians',
            body='This is the last night of the fair, And the grease in the hair',
            expected_status_code=401,
        )

    def test_feature_flag_false(self, app, client, fake_auth):
        """Returns 404 if feature flag is false."""
        app.config['FEATURE_FLAG_CREATE_NOTES'] = False
        fake_auth.login(advisor_uid)
        advisor = AuthorizedUser.find_by_uid(advisor_uid)
        assert self._api_note_create(
            client,
            author_id=advisor.id,
            sid=student['sid'],
            subject='Reel Around the Fountain',
            body='You took a child and you made him old',
            expected_status_code=404,
        )

    def test_create_note(self, app, client, fake_auth):
        """Marks a note as read."""
        app.config['FEATURE_FLAG_CREATE_NOTES'] = True
        fake_auth.login(advisor_uid)
        advisor = AuthorizedUser.find_by_uid(advisor_uid)
        subject = 'Vicar in a Tutu'
        new_note = self._api_note_create(
            client,
            author_id=advisor.id,
            sid=student['sid'],
            subject=subject,
            body='A scanty bit of a thing with a decorative ring',
        )
        note_id = new_note.get('id')
        assert new_note['read'] is False
        assert isinstance(note_id, int) and note_id > 0
        assert new_note['author']['uid'] == advisor_uid
        assert 'name' in new_note['author']
        assert new_note['author']['role'] == 'Advisor'
        assert new_note['author']['depts'] == ['College of Engineering']
        # Get notes per SID and compare
        notes = _get_notes(client, student['uid'])
        match = next((n for n in notes if n['id'] == note_id), None)
        assert match and match['subject'] == subject


class TestUpdateNotes:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.post('/api/notes/11667051-00001/mark_read').status_code == 401

    def test_mark_note_read(self, app, client, fake_auth):
        """Marks a note as read, ignoring FEATURE_FLAG_CREATE_NOTES."""
        app.config['FEATURE_FLAG_CREATE_NOTES'] = False
        fake_auth.login(advisor_uid)
        all_notes_unread = _get_notes(client, 61889)
        assert len(all_notes_unread) == 4
        for note in all_notes_unread:
            assert note['read'] is False
            if note['id'] == '11667051-00001':
                isinstance(note['author']['depts'], list)
        response = client.post('/api/notes/11667051-00001/mark_read')
        assert response.status_code == 201

        non_legacy_note_id = all_notes_unread[3]['id']
        response = client.post(f'/api/notes/{non_legacy_note_id}/mark_read')
        assert response.status_code == 201

        all_notes_one_read = _get_notes(client, 61889)
        assert len(all_notes_one_read) == 4
        assert all_notes_one_read[0]['id'] == '11667051-00001'
        assert all_notes_one_read[0]['read'] is True
        assert all_notes_one_read[1]['id'] == '11667051-00002'
        assert all_notes_one_read[1]['read'] is False
        assert all_notes_one_read[3]['id'] == non_legacy_note_id
        assert all_notes_one_read[3]['read'] is True


def _get_notes(client, uid):
    response = client.get(f'/api/student/{uid}')
    assert response.status_code == 200
    return response.json['notifications']['note']
