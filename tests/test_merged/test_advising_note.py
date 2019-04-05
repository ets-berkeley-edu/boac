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

from boac.merged.advising_note import get_advising_notes, get_attachment_stream, search_advising_notes
from boac.models.note import Note
from dateutil.parser import parse
from tests.util import mock_advising_note_attachment


asc_advisor = '6446'
coe_advisor = '1133399'


class TestMergedAdvisingNote:
    """Advising note data, merged."""

    def test_get_advising_notes(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('11667051')

        assert len(notes) == 4
        assert notes[0]['id'] == '11667051-00001'
        assert notes[0]['sid'] == '11667051'
        assert notes[0]['body'] == 'Brigitte is making athletic and moral progress'
        assert notes[0]['category'] == 'Quick Question'
        assert notes[0]['subcategory'] == 'Hangouts'
        assert notes[0]['appointmentId'] is None
        assert notes[0]['createdBy'] is None
        assert parse(notes[0]['createdAt']) == parse('2017-10-31T12:00:00+00:00')
        assert notes[0]['updatedBy'] is None
        assert parse(notes[0]['updatedAt']) == parse('2017-10-31T12:00:00+00:00')
        assert notes[0]['read'] is False
        assert notes[0]['topics'] == ['Good show']
        assert notes[1]['id'] == '11667051-00002'
        assert notes[1]['sid'] == '11667051'
        assert notes[1]['body'] == 'Brigitte demonstrates a cavalier attitude toward university requirements'
        assert notes[1]['category'] == 'Evaluation'
        assert notes[1]['subcategory'] == ''
        assert notes[1]['appointmentId'] is None
        assert notes[1]['createdBy'] is None
        assert parse(notes[1]['createdAt']) == parse('2017-11-01T12:00:00+00')
        assert notes[1]['updatedBy'] is None
        assert parse(notes[1]['updatedAt']) == parse('2017-11-01T12:00:00+00')
        assert notes[1]['read'] is False
        assert notes[1]['topics'] == ['Bad show', 'Show off']
        # Non-legacy note
        assert notes[3]['id']
        assert notes[3]['author']['uid'] == '6446'
        assert notes[3]['sid'] == '11667051'
        assert notes[3]['subject'] == 'In France they kiss on main street'
        assert 'My darling dime store thief' in notes[3]['body']
        assert notes[3]['category'] is None
        assert notes[3]['subcategory'] is None
        assert notes[3]['appointmentId'] is None
        assert notes[3]['createdBy'] is None
        assert notes[3]['createdAt']
        assert notes[3]['updatedBy'] is None
        assert notes[3]['updatedAt']
        assert notes[3]['read'] is False
        assert notes[3]['topics'] is None
        assert notes[3]['attachments'] is None

    def test_get_advising_notes_ucbconversion_attachment(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('11667051')
        assert notes[0]['attachments'] == [
            {
                'sisFilename': '11667051_00001_1.pdf',
            },
        ]

    def test_get_advising_notes_cs_attachment(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('11667051')
        assert notes[1]['attachments'] == [
            {
                'sisFilename': '11667051_00002_2.jpeg',
                'userFilename': 'brigitte_photo.jpeg',
            },
        ]

    def test_get_advising_notes_timestamp_format(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('9000000000')
        ucbconversion_note = notes[0]
        cs_note = notes[1]
        assert parse(ucbconversion_note['createdAt']) == parse('2017-11-02')
        assert ucbconversion_note['updatedAt'] is None
        assert parse(cs_note['createdAt']) == parse('2017-11-02T12:00:00+00')
        assert parse(cs_note['updatedAt']) == parse('2017-11-02T13:00:00+00')

    def test_search_advising_notes(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        notes = search_advising_notes(search_phrase='herostratus')
        assert len(notes) == 1
        assert '<strong>Herostratus</strong> lives' in notes[0]['noteSnippet']
        assert notes[0]['noteSnippet'].startswith('...iniquity of oblivion blindely scattereth her poppy')
        assert notes[0]['noteSnippet'].endswith('confounded that of himself. In vain we...')
        assert notes[0]['studentSid'] == '11667051'
        assert notes[0]['studentUid'] == '61889'
        assert notes[0]['studentName'] == 'Deborah Davies'
        assert notes[0]['advisorSid'] == '600500400'
        assert notes[0]['id'] == '11667051-00003'
        assert parse(notes[0]['createdAt']) == parse('2017-11-05T12:00:00+00')
        assert parse(notes[0]['updatedAt']) == parse('2017-11-06T12:00:00+00')

    def test_search_advising_notes_stemming(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='spare')
        assert len(response) == 1
        assert '<strong>spared</strong>' in response[0]['noteSnippet']
        response = search_advising_notes(search_phrase='felicity')
        assert len(response) == 1
        assert '<strong>felicities</strong>' in response[0]['noteSnippet']

    def test_search_advising_notes_too_short_to_snippet(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='campus')
        assert len(response) == 1
        assert response[0]['noteSnippet'] == 'Is this student even on <strong>campus</strong>?'

    def test_search_advising_notes_ordered_by_relevance(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='confound')
        assert len(response) == 2
        assert response[0]['noteSnippet'] == 'I am <strong>confounded</strong> by this <strong>confounding</strong> student'
        assert '<strong>confounded</strong> that of himself' in response[1]['noteSnippet']

    def test_search_advising_notes_multiple_terms(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='burnt diana temple')
        assert len(response) == 1
        assert 'Herostratus lives that <strong>burnt</strong> the <strong>Temple</strong> of <strong>Diana</strong>' in response[0]['noteSnippet']

    def test_search_advising_notes_no_match(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='pyramid octopus')
        assert len(response) == 0

    def test_search_advising_notes_funny_characters(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='horse; <- epitaph? ->')
        assert len(response) == 1
        assert 'Time hath spared the <strong>Epitaph</strong> of Adrians <strong>horse</strong>' in response[0]['noteSnippet']

    def test_search_dates(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='2/1/2019 1:30')
        assert len(response) == 1
        assert 'next appt. <strong>2/1/2019</strong> @ <strong>1:30</strong>. Student continued' in response[0]['noteSnippet']
        response = search_advising_notes(search_phrase='1-24-19')
        assert len(response) == 1
        assert 'drop Eng. 123 by <strong>1-24-19</strong>' in response[0]['noteSnippet']

    def test_search_decimals(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='2.0')
        assert len(response) == 1
        assert "Student continued on <strong>2.0</strong> prob (COP) until Sp '19." in response[0]['noteSnippet']

    def test_search_email_address(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='E-mailed test@berkeley.edu')
        assert len(response) == 1
        assert "until Sp '19. <strong>E-mailed</strong> <strong>test@berkeley.edu</strong>: told her she'll need to drop Eng. 123" \
            in response[0]['noteSnippet']

    def test_search_advising_notes_timestamp_format(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='confound')
        ucbconversion_note = response[0]
        cs_note = response[1]
        assert ucbconversion_note['createdAt']
        assert ucbconversion_note['updatedAt'] is None
        assert cs_note['createdAt'] and cs_note['updatedAt']

    def test_search_advising_notes_includes_newly_created(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        Note.create(
            author_uid=coe_advisor,
            author_name='Balloon Man',
            author_role='Spherical',
            author_dept_codes='COENG',
            sid='11667051',
            subject='Confound this note',
            body='and its successors and assigns',
        )
        response = search_advising_notes(search_phrase='confound')
        assert len(response) == 3
        assert response[0]['noteSnippet'] == '<strong>Confound</strong> this note - and its successors and assigns'
        assert response[1]['noteSnippet'].startswith('I am <strong>confounded</strong>')
        assert response[2]['noteSnippet'].startswith('...pity the founder')

    def test_search_advising_notes_paginates_new_and_old(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        for i in range(0, 5):
            Note.create(
                author_uid=coe_advisor,
                author_name='Balloon Man',
                author_role='Spherical',
                author_dept_codes='COENG',
                sid='11667051',
                subject='Planned redundancy',
                body=f'Confounded note {i + 1}',
            )
        response = search_advising_notes(search_phrase='confound', offset=0, limit=4)
        assert len(response) == 4
        assert response[0]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 1'
        assert response[1]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 2'
        assert response[2]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 3'
        assert response[3]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 4'
        response = search_advising_notes(search_phrase='confound', offset=4, limit=4)
        assert len(response) == 3
        assert response[0]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 5'
        assert response[1]['noteSnippet'].startswith('I am <strong>confounded</strong>')
        assert response[2]['noteSnippet'].startswith('...pity the founder')

    def test_stream_attachment(self, app, fake_auth):
        with mock_advising_note_attachment(app):
            fake_auth.login(coe_advisor)
            stream = get_attachment_stream('9000000000_00002_1.pdf')['stream']
            body = b''
            for chunk in stream:
                body += chunk
            assert body == b'When in the course of human events, it becomes necessarf arf woof woof woof'

    def test_stream_attachment_respects_scope_constraints(self, app, fake_auth):
        with mock_advising_note_attachment(app):
            fake_auth.login(asc_advisor)
            assert get_attachment_stream('9000000000_00002_1.pdf') is None

    def test_stream_attachment_handles_malformed_filename(self, app):
        with mock_advising_note_attachment(app):
            assert get_attachment_stream('h0ax.lol') is None

    def test_stream_attachment_handles_file_not_in_database(self, app, fake_auth, caplog):
        with mock_advising_note_attachment(app):
            fake_auth.login(coe_advisor)
            assert get_attachment_stream('11667051_00002_1.pdf') is None

    def test_stream_attachment_handles_file_not_in_s3(self, app, fake_auth, caplog):
        with mock_advising_note_attachment(app):
            fake_auth.login(coe_advisor)
            assert get_attachment_stream('11667051_00001_1.pdf')['stream'] is None
            assert "the s3 key 'attachment-path/11667051/11667051_00001_1.pdf' does not exist, or is forbidden" in caplog.text
