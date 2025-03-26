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

import json

from boac import std_commit
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from tests.util import mock_advising_note_s3_bucket

admin_uid = '2040'
asc_advisor_uid = '6446'
ce3_advisor_uid = '2525'
ce3_navcal_peer_advisor_uid = '1133400'
ce3_navcal_peer_advisor_manager_uid = '2525'
coe_advisor_no_advising_data_uid = '1022796'
coe_mech_peer_advisor_uid = '1913062'
coe_student = {
    'sid': '9000000000',
    'uid': '300847',
}
qcadv_advisor_uid = '53791'


class TestCreatePeerAdvisingNote:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    def test_not_authorized(self, app, client, fake_auth):
        """Returns 401 if not authorized."""
        for uid in (None, ce3_navcal_peer_advisor_manager_uid, qcadv_advisor_uid):
            fake_auth.login(uid)
            assert _api_create_peer_advising_note(
                body='Yes, you are not authorized.',
                client=client,
                expected_status_code=401,
                peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
                sid=coe_student['sid'],
            )

    def test_not_authorized_to_add_attachments(self, app, client, fake_auth):
        fake_auth.login(ce3_navcal_peer_advisor_manager_uid)
        with mock_advising_note_s3_bucket(app):
            base_dir = app.config['BASE_DIR']
            attachment = f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt'
            with open(attachment, 'r') as file:
                note = Note.create(
                    attachments=[
                        {
                            'name': attachment.rsplit('/', 1)[-1],
                            'byte_stream': file.read(),
                        },
                    ],
                    author_uid=ce3_navcal_peer_advisor_uid,
                    author_name='CE3 Peer Advisor',
                    author_role='Peer Advisor',
                    author_dept_codes=['ZCEEE'],
                    body='Rock \'n Roll rang sweet as victory, under neon signs',
                    sid='11667051',
                    subject='',
                )
                std_commit(allow_test_environment=True)
                _api_note_attachments_upload(
                    app=app,
                    attachments=[f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt'],
                    client=client,
                    expected_status_code=401,
                    note_id=note.id,
                )

    def test_invalid_peer_advising_department_id(self, client, fake_auth):
        coe_mech_peer_advisor = AuthorizedUser.find_by_uid(coe_mech_peer_advisor_uid)
        user_id = coe_mech_peer_advisor.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        # CoE peer advising dept
        coe_mech_peer_advising_department_id = memberships[0]['peer_advising_department_id']
        # Log in as CE3 peer_advisor
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        _api_create_peer_advising_note(
            body='Yes, you are not authorized.',
            client=client,
            expected_status_code=403,
            peer_advising_department_id=coe_mech_peer_advising_department_id,
            sid=coe_student['sid'],
        )

    def test_authorized(self, app, client, fake_auth):
        """Create a note."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        note = _api_create_peer_advising_note(
            body='CE3 NAVCAL note created by Peer Advisor',
            client=client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
            sid=coe_student['sid'],
        )
        note_id = note['id']
        base_dir = app.config['BASE_DIR']
        note = _api_note_attachments_upload(
            app=app,
            attachments=[
                f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt',
                f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt',
            ],
            client=client,
            note_id=note_id,
        )
        assert note_id
        assert note['author']['uid'] == ce3_navcal_peer_advisor_uid
        assert note['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        assert note['read'] is True
        assert len(note.get('attachments')) == 2


class TestGetNotesAuthoredBy:

    @classmethod
    def _api_notes_authored_by(cls, client, peer_advising_department_id, uid, expected_status_code=200):
        response = client.get(f'/api/peer_advising/{peer_advising_department_id}/note_author/{uid}')
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized(self, app, client, fake_auth):
        """Returns 401 if not authenticated."""
        for uid in [None, coe_advisor_no_advising_data_uid, coe_student['uid']]:
            if uid:
                fake_auth.login(uid)
        self._api_notes_authored_by(
            client=client,
            expected_status_code=401,
            peer_advising_department_id=1,
            uid=uid,
        )

    def test_authorized(self, app, client, fake_auth):
        """Advisor can view notes created by another Advisor or Peer Advisor user."""
        fake_auth.login(ce3_navcal_peer_advisor_manager_uid)
        peer_advisor = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        peer_advising_department_id = PeerAdvisingDepartmentMember.get_peer_advising_department_membership(
            role_type='peer_advisor',
            user_id=peer_advisor.id,
        ).peer_advising_department_id
        note = Note.create(
            author_uid=peer_advisor.uid,
            peer_advising_department_id=peer_advising_department_id,
            author_name='CE3 Peer Advisor',
            author_role='Peer Advisor',
            author_dept_codes=['ZCEEE'],
            body='He spattered me with tomatoes, Hummus, chick peas',
            sid=coe_student['sid'],
            subject='',
        )
        api_json = self._api_notes_authored_by(
            client=client,
            peer_advising_department_id=peer_advising_department_id,
            uid=peer_advisor.uid,
        )
        assert len(api_json)
        assert next((n for n in api_json if n['id'] == note.id), None)


class TestGetPeerAdvisingNotes:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    @classmethod
    def _api_get_notes_for_peer_advisor(cls, client, uid, include_students=False, expected_status_code=200):
        response = client.get(f'/api/peer_advisor/{uid}/notes?includeStudents={include_students}')
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 unless user is a Peer Advisor."""
        peer_advisor_uid = coe_mech_peer_advisor_uid
        for uid in [None, qcadv_advisor_uid]:
            if uid:
                fake_auth.login(uid)
            self._api_get_notes_for_peer_advisor(
                client,
                expected_status_code=401,
                uid=peer_advisor_uid,
            )

    def test_authorized(self, client, fake_auth):
        """Delivers notes per peer_advising_department of Peer Advisor."""
        uid = ce3_navcal_peer_advisor_uid
        fake_auth.login(uid)
        # Create a note...
        note = _api_create_peer_advising_note(
            body='CE3 NAVCAL note created by Peer Advisor',
            client=client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
            sid=coe_student['sid'],
        )
        assert note['id']
        assert note['author']['uid'] == ce3_navcal_peer_advisor_uid
        assert note['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        # Fetch that note, without student.
        api_json = self._api_get_notes_for_peer_advisor(client, uid=uid)
        notes = api_json['notes']
        assert len(notes) > 0
        assert len(notes) == api_json['totalNoteCount']
        assert notes[0]['id'] == note['id']
        assert 'student' not in notes[0]
        # Fetch that note, with student.
        api_json = self._api_get_notes_for_peer_advisor(client, include_students=True, uid=uid)
        notes = api_json['notes']
        assert notes[0]['student']['sid'] == coe_student['sid']
        # Verify with BOA Admin
        fake_auth.login(admin_uid)
        self._api_get_notes_for_peer_advisor(client, uid=uid)


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


class TestGetStudentEnrollments:

    @classmethod
    def _api_get_student_enrollments(cls, client, sid, expected_status_code=200):
        response = client.get(f'/api/peer_advising/{sid}/enrollments')
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized(self, client, fake_auth):
        """Only Peer Advisors can reach this API."""
        for uid in [None, qcadv_advisor_uid]:
            if uid:
                fake_auth.login(uid)
            self._api_get_student_enrollments(
                client,
                expected_status_code=401,
                sid='11667051',
            )

    def test_authorized(self, client, fake_auth):
        """Peer Advisors get minimal access to student enrollment data."""
        fake_auth.login(coe_mech_peer_advisor_uid)
        api_json = self._api_get_student_enrollments(client, sid='11667051')
        # Verify term info
        assert len(api_json)
        previous_academic_calendar = None
        for academic_year_label, enrollments_by_term_id in api_json.items():
            if previous_academic_calendar:
                assert academic_year_label < previous_academic_calendar
            previous_academic_calendar = academic_year_label
            assert len(enrollments_by_term_id) == 3
            previous_term_id = None
            for term_id, enrollments in enrollments_by_term_id.items():
                if previous_term_id:
                    assert int(term_id) > int(previous_term_id)
                # Verify limited enrollment data
                previous_display_name = None
                for enrollment in enrollments:
                    assert set(enrollment.keys()) == {'displayName', 'sections', 'title', 'units'}
                    display_name = enrollment['displayName']
                    if previous_display_name:
                        assert display_name > previous_display_name
                    sections = enrollment['sections']
                    assert len(sections)
                    assert set(sections[0]) == {'component', 'enrollmentStatus', 'isUncompletedPerGrade', 'primary', 'sectionId', 'sectionNumber'}
                    previous_display_name = display_name
                previous_term_id = term_id


class TestUpdateNotes:

    @classmethod
    def setup_class(cls):
        author_uid = ce3_navcal_peer_advisor_uid
        peer_advisor_user_id = AuthorizedUser.get_id_per_uid(author_uid)
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(peer_advisor_user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']
        cls.mock_ce3_navcal_peer_advising_note = None
        cls.student_sid_of_note = '11667051'
        # Create mock note
        note = Note.create(
            author_uid=author_uid,
            author_name='Davey Jones',
            author_role='peer_advisor',
            author_dept_codes=[],
            body="""
                I bought you a pair of shoes, a trumpet you can blow
                And a book of rules on what to say to people
                When they pick on you
                'Cause if you stay with us, you're gonna be pretty kooky, too.
            """,
            peer_advising_department_id=cls.ce3_navcal_peer_advising_department_id,
            sid=cls.student_sid_of_note,
            subject='Kooks',
            contact_type=None,
            topics=['collaborative synergies', 'vertical solutions'],
        )
        std_commit(allow_test_environment=True)
        cls.peer_advising_note_id = note.id

    @classmethod
    def _api_peer_advising_note_update(
            cls,
            body,
            client,
            note_id,
            subject,
            expected_status_code=200,
            contact_type=None,
            topics=(),
    ):
        data = {
            'id': note_id,
            'body': body,
            'contactType': contact_type,
            'subject': subject,
            'topics': ','.join(topics),
        }
        response = client.post(
            '/api/peer_advising/note/update',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized_peer_advising_note_update(self, app, client, fake_auth):
        """Unauthorized user cannot update Peer Advising note."""
        for uid in [None, coe_advisor_no_advising_data_uid, qcadv_advisor_uid]:
            if uid:
                fake_auth.login(uid)
            self._api_peer_advising_note_update(
                body='Hack the body!',
                client=client,
                expected_status_code=401,
                note_id=self.peer_advising_note_id,
                subject='Hack the subject!',
            )

    def test_authorized_peer_advising_note_update(self, app, client, fake_auth):
        """Update Peer Advising note topics."""
        body = """
            Don't pick fights with the bullies or the cads
            'Cause I'm not much cop at punching other people's dads
            And if the homework brings you down
            Then we'll throw it on the fire and take the car downtown
        """
        subject = 'Cause we believe in you'
        topics = ['One', 'two', 'three', 'four']
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        api_json = self._api_peer_advising_note_update(
            body=body,
            client=client,
            contact_type='Email',
            note_id=self.peer_advising_note_id,
            subject=subject,
            topics=topics,
        )
        assert api_json['body'].strip().replace(' ', '') == body.strip().replace(' ', '')
        assert api_json['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        assert api_json['subject'] == subject
        assert api_json['sid'] == self.student_sid_of_note
        for topic in topics:
            assert topic in api_json['topics']

    def test_remove_note_topics(self, app, client, fake_auth):
        """Delete note topics."""
        note = Note.find_by_id(self.peer_advising_note_id)
        assert len(note.topics) > 0
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        api_json = self._api_peer_advising_note_update(
            body=note.body,
            client=client,
            contact_type='Email',
            note_id=note.id,
            subject=note.subject,
            topics=[],
        )
        assert len(api_json['topics']) == 0
        # Put those topics back
        fresh_topics = ['One', 'two', 'three', 'four']
        api_json = self._api_peer_advising_note_update(
            body=note.body,
            client=client,
            contact_type='Email',
            note_id=note.id,
            subject=note.subject,
            topics=fresh_topics,
        )
        assert set(api_json['topics']) == set(fresh_topics)


def _api_create_peer_advising_note(
        client,
        body,
        peer_advising_department_id,
        sid,
        subject='',
        contact_type=None,
        expected_status_code=200,
        topics=(),
):
    data = {
        'body': body,
        'contactType': contact_type,
        'peerAdvisingDepartmentId': peer_advising_department_id,
        'sid': sid,
        'subject': subject,
        'topics': ','.join(topics),
    }
    response = client.post(
        '/api/peer_advising/note/create',
        content_type='application/json',
        data=json.dumps(data),
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_note_attachments_upload(
    app,
    attachments,
    client,
    note_id,
    expected_status_code=200,
):
    with mock_advising_note_s3_bucket(app):
        data = {}
        for index, path in enumerate(attachments):
            data[f'attachment[{index}]'] = open(path, 'rb')
        response = client.post(
            f'/api/peer_advisor/note/{note_id}/attachments',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json
