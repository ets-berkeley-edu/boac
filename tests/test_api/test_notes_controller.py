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

coe_advisor = '1133399'


class TestGetNotes:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/notes/student/11667051').status_code == 401

    def test_notes_for_sid(self, fake_auth, client):
        """Returns advising notes per SID."""
        fake_auth.login(coe_advisor)
        response = client.get('/api/notes/student/11667051')
        assert response.status_code == 200
        notes = response.json
        assert len(notes) == 2
        assert notes[0]['sid'] == '11667051'
        assert notes[0]['topic'] == 'Good show'
        assert notes[0]['createdAt'] == 1509451200
        assert notes[1]['sid'] == '11667051'
        assert notes[1]['topic'] == 'Bad show'
        assert notes[1]['createdAt'] == 1509537600

    def test_get_note_by_id(self, fake_auth, client):
        """Returns advising note by ID."""
        fake_auth.login(coe_advisor)
        response = client.get('/api/notes/11667051-00001')
        assert response.status_code == 200
        note = response.json
        assert note['sid'] == '11667051'
        assert note['topic'] == 'Good show'
        assert note['body'] == 'Brigitte is making athletic and moral progress'


class TestUpdateNotes:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.post('/api/notes/11667051-00001/mark_read').status_code == 401

    def test_mark_note_read(self, fake_auth, client):
        """Marks a note as read."""
        fake_auth.login(coe_advisor)

        all_notes_unread = client.get('/api/notes/student/11667051').json
        assert len(all_notes_unread) == 2
        for note in all_notes_unread:
            assert note['read'] is False
        individual_note_unread = client.get('/api/notes/11667051-00001').json
        assert individual_note_unread['read'] is False

        response = client.post('/api/notes/11667051-00001/mark_read')
        assert response.status_code == 201

        all_notes_one_read = client.get('/api/notes/student/11667051').json
        assert len(all_notes_one_read) == 2
        assert all_notes_one_read[0]['read'] is True
        assert all_notes_one_read[1]['read'] is False
        individual_note_read = client.get('/api/notes/11667051-00001').json
        assert individual_note_read['read'] is True
        unread_note_after = client.get('/api/notes/11667051-00002').json
        assert unread_note_after['read'] is False
