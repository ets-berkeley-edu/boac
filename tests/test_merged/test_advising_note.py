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

import io
from zipfile import ZipFile

from dateutil.parser import parse

from boac.merged.advising_note import get_advising_notes, get_zip_stream
from tests.util import mock_eop_note_attachment, mock_sis_note_attachment

asc_advisor = '6446'
ce3_advisor_uid = '2525'
coe_advisor = '1133399'


class TestMergedAdvisingNote:
    """Advising note data, merged."""

    def test_get_advising_notes(self, mock_advising_note, fake_auth):  # noqa: PLR0915
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('11667051')

        # Legacy SIS notes
        assert notes[0]['id'] == '11667051-00001'
        assert notes[0]['sid'] == '11667051'
        assert notes[0]['body'] == 'Brigitte is making athletic and moral progress'
        assert notes[0]['category'] == 'Quick Question'
        assert notes[0]['subcategory'] == 'Hangouts'
        assert notes[0]['appointmentId'] is None
        assert notes[0]['createdBy'] is None
        assert parse(notes[0]['createdAt']) == parse('2017-10-31T12:00:00+00:00')
        assert notes[0]['updatedBy'] is None
        assert notes[0]['updatedAt'] is None
        assert notes[0]['contactType'] is None
        assert notes[0]['setDate'] is None
        assert notes[0]['read'] is False
        assert notes[0]['topics'] == ['God Scéaw']
        assert notes[0]['legacySource'] == 'SIS'
        assert notes[1]['id'] == '11667051-00002'
        assert notes[1]['sid'] == '11667051'
        assert notes[1]['body'] == 'Brigitte demonstrates a cavalier attitude toward university requirements'
        assert notes[1]['category'] == 'Evaluation'
        assert notes[1]['subcategory'] == ''
        assert notes[1]['appointmentId'] is None
        assert notes[1]['createdBy'] is None
        assert parse(notes[1]['createdAt']) == parse('2017-11-01T12:00:00+00')
        assert notes[1]['updatedBy'] is None
        assert notes[1]['updatedAt'] is None
        assert notes[1]['read'] is False
        assert notes[1]['topics'] == ['Earg Scéaw', 'Ofscéaw']
        assert notes[1]['legacySource'] == 'SIS'

        # Legacy ASC note without subject/body
        assert notes[4]['id'] == '11667051-139362'
        assert notes[4]['sid'] == '11667051'
        assert notes[4]['subject'] is None
        assert notes[4]['body'] is None
        assert notes[4]['author']['uid'] == '1133399'
        assert notes[4]['author']['name'] == 'Lemmy Kilmister'
        assert notes[4]['topics'] == ['Academic', 'Other']
        assert notes[4]['createdAt']
        assert notes[4]['updatedAt'] is None
        assert notes[4]['read'] is False
        assert notes[4]['legacySource'] == 'ASC'

        # Legacy ASC note with subject/body
        assert notes[5]['id'] == '11667051-139379'
        assert notes[5]['sid'] == '11667051'
        assert notes[5]['subject'] == 'Ginger Baker\'s Air Force'
        assert notes[5]['body'] == '<p>Bands led by drummers</p><p>tend to leave a lot of space for drum solos</p>'
        assert notes[5]['author']['uid'] == '90412'
        assert notes[5]['author']['name'] == 'Ginger Baker'
        assert notes[5]['topics'] is None
        assert notes[5]['createdAt']
        assert notes[5]['updatedAt'] is None
        assert notes[5]['read'] is False
        assert notes[5]['legacySource'] == 'ASC'

        # Legacy Data Science notes
        assert notes[6]['id'] == '11667051-20181003051208'
        assert notes[6]['sid'] == '11667051'
        assert notes[6]['body'] == 'Data that is loved tends to survive.'
        assert notes[6]['author']['email'] == '33333@berkeley.edu'
        assert notes[6]['createdAt'] == '2018-10-04T00:12:08+00:00'
        assert notes[6]['topics'] == ['Declaring the major', 'Course planning', 'Domain Emphasis']
        assert notes[6]['legacySource'] == 'Data Science'

        # Legacy E&I notes
        assert notes[8]['id'] == '11667051-151620'
        assert notes[8]['sid'] == '11667051'
        assert notes[8]['body'] is None
        assert notes[8]['author']['uid'] == '1133398'
        assert notes[8]['author']['name'] == 'Charlie Christian'
        assert notes[8]['topics'] == ['Course Planning', 'Personal']
        assert notes[8]['createdAt']
        assert notes[8]['updatedAt'] is None
        assert notes[8]['read'] is False
        assert notes[8]['legacySource'] == 'CE3'

        # Legacy EOP note
        assert notes[9]['id'] == 'eop_advising_note_100'
        assert notes[9]['sid'] == '11667051'
        assert notes[9]['body'] == 'An EOP note'
        assert notes[9]['subject'] == 'TBB Check In'
        assert notes[9]['author']['uid'] == '211159'
        assert notes[9]['author']['name'] == 'Roland Bestwestern'
        assert notes[9]['topics'] == ['Post-Graduation', 'Cool Podcasts', 'Instagrammable Restaurants']
        assert notes[9]['createdBy'] == '211159'
        assert notes[9]['createdAt']
        assert notes[9]['updatedAt'] is None
        assert notes[9]['contactType'] == 'Online scheduled'
        assert notes[9]['read'] is False
        assert notes[9]['isPrivate'] is False
        assert notes[9]['legacySource'] == 'EOP'

        # Non-legacy note
        boa_created_note = next((n for n in notes if n['id'] == mock_advising_note.id), None)
        assert boa_created_note['id']
        assert boa_created_note['author']['uid'] == mock_advising_note.author_uid
        assert boa_created_note['sid'] == '11667051'
        assert boa_created_note['subject'] == 'In France they kiss on main street'
        assert 'My darling dime store thief' in boa_created_note['body']
        assert boa_created_note['category'] is None
        assert boa_created_note['subcategory'] is None
        assert boa_created_note['appointmentId'] is None
        assert boa_created_note['createdBy'] is None
        assert boa_created_note['createdAt']
        assert boa_created_note['contactType'] is None
        assert boa_created_note['setDate'] is None
        assert boa_created_note['updatedBy'] is None
        assert boa_created_note['updatedAt'] is None
        assert boa_created_note['read'] is False
        assert len(boa_created_note['topics']) == 4
        assert len(boa_created_note['attachments']) == 1
        assert 'legacySource' not in boa_created_note

    def test_get_advising_notes_ucbconversion_attachment(self, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('11667051')
        assert notes[0]['attachments'] == [
            {
                'displayName': '11667051_00001_1.pdf',
                'id': '11667051_00001_1.pdf',
                'sisFilename': '11667051_00001_1.pdf',
            },
        ]

    def test_get_advising_notes_cs_attachment(self, mock_advising_note, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('11667051')
        assert notes[1]['attachments'] == [
            {
                'id': '11667051_00002_2.jpeg',
                'sisFilename': '11667051_00002_2.jpeg',
                'displayName': 'brigitte_photo.jpeg',
            },
        ]
        boa_created_note = next((n for n in notes if n['id'] == mock_advising_note.id), None)
        assert boa_created_note
        assert boa_created_note['attachments'][0]['uploadedBy'] == mock_advising_note.author_uid

    def test_private_eop_note_attachment(self, app, fake_auth):
        with mock_eop_note_attachment(app):
            fake_auth.login(ce3_advisor_uid)
            notes = get_advising_notes('890127492')
            assert notes[0]['isPrivate'] is True
            assert notes[0]['attachments'] == [
                {
                    'id': 'eop_advising_note_101',
                    'displayName': 'i am attached.txt',
                    'fileName': 'eop_advising_note_101_i am attached.txt',
                },
            ]

    def test_private_eop_note_attachment_unauthorized(self, app, fake_auth):
        with mock_eop_note_attachment(app):
            fake_auth.login(coe_advisor)
            notes = get_advising_notes('890127492')
            assert notes[0]['isPrivate'] is True
            assert notes[0]['attachments'] is None
            assert notes[0]['body'] is None

    def test_get_advising_notes_timestamp_format(self, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('9000000000')
        ucbconversion_note = notes[0]
        cs_note = notes[1]
        assert parse(ucbconversion_note['createdAt']) == parse('2017-11-02')
        assert ucbconversion_note['updatedAt'] is None
        assert parse(cs_note['createdAt']) == parse('2017-11-02T12:00:00+00')
        assert parse(cs_note['updatedAt']) == parse('2017-11-02T13:00:00+00')

    def test_stream_zipped_bundle(self, app):
        with mock_sis_note_attachment(app):
            sid = '9000000000'
            filename = 'advising_notes'
            stream = get_zip_stream(
                download_type='note',
                filename=filename,
                notes=get_advising_notes(sid),
                student={
                    'first_name': 'Wolfgang',
                    'last_name': 'Pauli-O\'Rourke',
                    'sid': sid,
                },
            )
            body = b''
            for chunk in stream:
                body += chunk
            zipfile = ZipFile(io.BytesIO(body), 'r')
            contents = {}
            for name in zipfile.namelist():
                contents[name] = zipfile.read(name)

            csv_rows = contents[f'{filename}.csv'].decode('utf-8').strip().split('\r\n')
            assert len(contents) == 2
            assert len(csv_rows) == 3
            assert contents['dog_eaten_homework.pdf'] == b'When in the course of human events, it becomes necessarf arf woof woof woof'
            assert csv_rows[0] == """
                date_created,student_sid,student_name,author_uid,author_csid,author_name,subject,body,topics,attachments,is_private
            """.strip()
            assert csv_rows[1] == """
                2017-11-02,9000000000,Wolfgang Pauli-O'Rourke,,700600500,,,I am confounded by this confounding student,,dog_eaten_homework.pdf,False
            """.strip()
            assert csv_rows[2] == """
                2017-11-02,9000000000,Wolfgang Pauli-O'Rourke,,600500400,,,Is this student even on campus?,Ne Scéaw,,False
            """.strip()
