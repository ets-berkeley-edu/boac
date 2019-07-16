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

from datetime import datetime, timedelta

from boac.merged.advising_note import get_advising_notes, get_legacy_attachment_stream, search_advising_notes
from boac.models.note import Note
from dateutil.parser import parse
import pytz
from tests.util import mock_legacy_note_attachment


asc_advisor = '6446'
coe_advisor = '1133399'


class TestMergedAdvisingNote:
    """Advising note data, merged."""

    def test_get_advising_notes(self, app, coe_advising_note_with_attachment, fake_auth):
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
        assert notes[0]['read'] is False
        assert notes[0]['topics'] == ['God Scéaw']
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

        # Legacy ASC notes
        assert notes[4]['id'] == '11667051-139362'
        assert notes[4]['sid'] == '11667051'
        assert notes[4]['body'] is None
        assert notes[4]['author']['uid'] == '1133399'
        assert notes[4]['author']['name'] == 'Lemmy Kilmister'
        assert notes[4]['topics'] == ['Academic', 'Other']
        assert notes[4]['createdAt']
        assert notes[4]['updatedAt'] is None
        assert notes[4]['read'] is False
        assert notes[5]['id'] == '11667051-139379'
        assert notes[5]['sid'] == '11667051'
        assert notes[5]['body'] is None
        assert notes[5]['author']['uid'] == '90412'
        assert notes[5]['author']['name'] == 'Ginger Baker'
        assert notes[5]['topics'] is None
        assert notes[5]['createdAt']
        assert notes[5]['updatedAt'] is None
        assert notes[5]['read'] is False

        # Non-legacy note
        boa_created_note = next((n for n in notes if n['id'] == coe_advising_note_with_attachment.id), None)
        assert boa_created_note['id']
        assert boa_created_note['author']['uid'] == coe_advising_note_with_attachment.author_uid
        assert boa_created_note['sid'] == '11667051'
        assert boa_created_note['subject'] == 'In France they kiss on main street'
        assert 'My darling dime store thief' in boa_created_note['body']
        assert boa_created_note['category'] is None
        assert boa_created_note['subcategory'] is None
        assert boa_created_note['appointmentId'] is None
        assert boa_created_note['createdBy'] is None
        assert boa_created_note['createdAt']
        assert boa_created_note['updatedBy'] is None
        assert boa_created_note['updatedAt'] is None
        assert boa_created_note['read'] is False
        assert boa_created_note['topics'] == []
        assert len(boa_created_note['attachments']) == 1

    def test_get_advising_notes_ucbconversion_attachment(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('11667051')
        assert notes[0]['attachments'] == [
            {
                'displayName': '11667051_00001_1.pdf',
                'id': '11667051_00001_1.pdf',
                'sisFilename': '11667051_00001_1.pdf',
            },
        ]

    def test_get_advising_notes_cs_attachment(self, app, coe_advising_note_with_attachment, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('11667051')
        assert notes[1]['attachments'] == [
            {
                'id': '11667051_00002_2.jpeg',
                'sisFilename': '11667051_00002_2.jpeg',
                'displayName': 'brigitte_photo.jpeg',
            },
        ]
        boa_created_note = next((n for n in notes if n['id'] == coe_advising_note_with_attachment.id), None)
        assert boa_created_note
        assert boa_created_note['attachments'][0]['uploadedBy'] == coe_advising_note_with_attachment.author_uid

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
        assert notes[0]['updatedAt'] is None

    def test_search_advising_notes_by_category(self, app, fake_auth):
        """Matches legacy category/subcategory for SIS advising notes only if body is blank."""
        fake_auth.login(coe_advisor)
        notes = search_advising_notes(search_phrase='Quick Question')
        assert len(notes) == 1
        assert notes[0]['noteSnippet'] == '<strong>Quick</strong> <strong>Question</strong>, Unanswered'

    def test_search_for_asc_advising_notes(self, app, fake_auth):
        fake_auth.login(asc_advisor)
        response = search_advising_notes(search_phrase='kilmister')
        assert len(response) == 1
        assert response[0]['noteSnippet'] == ''
        assert response[0]['advisorName'] == 'Lemmy Kilmister'
        assert parse(response[0]['createdAt']) == parse('2014-01-03T20:30:00+00')
        assert response[0]['updatedAt'] is None
        response = search_advising_notes(search_phrase='academic')
        assert len(response) == 1
        assert response[0]['noteSnippet'] == ''
        assert response[0]['advisorName'] == 'Lemmy Kilmister'
        assert parse(response[0]['createdAt']) == parse('2014-01-03T20:30:00+00')
        assert response[0]['updatedAt'] is None

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
        assert cs_note['createdAt']
        assert cs_note['updatedAt'] is None

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

    def test_search_advising_notes_narrowed_by_author(self, app, fake_auth):
        """Narrows results for both new and legacy advising notes by author SID."""
        joni = {
            'name': 'Joni Mitchell',
            'uid': '1133399',
            'sid': '800700600',
        }
        not_joni = {
            'name': 'Oliver Heyer',
            'uid': '2040',
        }
        for author in [joni, not_joni]:
            Note.create(
                author_uid=author['uid'],
                author_name=author['name'],
                author_role='Advisor',
                author_dept_codes='COENG',
                sid='11667051',
                subject='Futher on France',
                body='Brigitte has been molded to middle class circumstance',
            )
        fake_auth.login(coe_advisor)
        wide_response = search_advising_notes(search_phrase='Brigitte')
        assert len(wide_response) == 4
        narrow_response = search_advising_notes(search_phrase='Brigitte', author_csid=joni['sid'])
        assert len(narrow_response) == 2
        new_note, legacy_note = narrow_response[0], narrow_response[1]
        assert new_note['advisorUid'] == joni['uid']
        assert legacy_note['advisorSid'] == joni['sid']

    def test_search_advising_notes_narrowed_by_student(self, app, fake_auth):
        """Narrows results for both new and legacy advising notes by student SID."""
        for sid in ['9100000000', '9100000001']:
            Note.create(
                author_uid='1133399',
                author_name='Joni Mitchell',
                author_role='Advisor',
                author_dept_codes='COENG',
                sid=sid,
                subject='Case load',
                body='Another day, another student',
            )
        fake_auth.login(coe_advisor)
        wide_response = search_advising_notes(search_phrase='student')
        assert len(wide_response) == 5
        narrow_response = search_advising_notes(search_phrase='student', student_csid='9100000000')
        assert len(narrow_response) == 2
        new_note, legacy_note = narrow_response[0], narrow_response[1]
        assert new_note['studentSid'] == '9100000000'
        assert legacy_note['studentSid'] == '9100000000'

    def test_search_advising_notes_narrowed_by_topic(self, app, fake_auth):
        for topic in ['Good Show', 'Bad Show']:
            Note.create(
                author_uid='1133399',
                author_name='Joni Mitchell',
                author_role='Advisor',
                author_dept_codes='COENG',
                sid='11667051',
                topics=[topic],
                subject='Brigitte',
                body='',
            )
        fake_auth.login(coe_advisor)
        wide_response = search_advising_notes(search_phrase='Brigitte')
        assert len(wide_response) == 4
        narrow_response = search_advising_notes(search_phrase='Brigitte', topic='Good Show')
        assert len(narrow_response) == 2

    def test_search_legacy_advising_notes_narrowed_by_date(self, app, fake_auth):
        halloween_2017 = datetime(2017, 10, 31, tzinfo=pytz.timezone(app.config['TIMEZONE'])).astimezone(pytz.utc)
        days = [
            halloween_2017 - timedelta(days=1),
            halloween_2017,
            halloween_2017 + timedelta(days=1),
            halloween_2017 + timedelta(days=2),
            halloween_2017 + timedelta(days=3),
        ]
        fake_auth.login(coe_advisor)

        unbounded = search_advising_notes(search_phrase='Brigitte')
        assert len(unbounded) == 2
        lower_bound = search_advising_notes(search_phrase='Brigitte', datetime_from=days[2])
        assert len(lower_bound) == 1
        upper_bound = search_advising_notes(search_phrase='Brigitte', datetime_to=days[2])
        assert len(upper_bound) == 1
        closed_1 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[0], datetime_to=days[2])
        assert len(closed_1) == 1
        closed_2 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[2], datetime_to=days[3])
        assert len(closed_2) == 1
        closed_3 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[0], datetime_to=days[3])
        assert len(closed_3) == 2
        closed_4 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[3], datetime_to=days[4])
        assert len(closed_4) == 0

    def test_search_new_advising_notes_narrowed_by_date(self, app, fake_auth):
        today = datetime.now().replace(hour=0, minute=0, second=0, tzinfo=pytz.timezone(app.config['TIMEZONE'])).astimezone(pytz.utc)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        fake_auth.login(coe_advisor)
        Note.create(
            author_uid=coe_advisor,
            author_name='Balloon Man',
            author_role='Spherical',
            author_dept_codes='COENG',
            sid='11667051',
            subject='Bryant Park',
            body='There were loads of them',
        )
        assert len(search_advising_notes(search_phrase='Bryant')) == 1

        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday)) == 1
        assert len(search_advising_notes(search_phrase='Bryant', datetime_to=yesterday)) == 0
        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday, datetime_to=yesterday)) == 0

        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=tomorrow)) == 0
        assert len(search_advising_notes(search_phrase='Bryant', datetime_to=tomorrow)) == 1
        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=tomorrow, datetime_to=tomorrow)) == 0

        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday, datetime_to=tomorrow)) == 1

    def test_stream_attachment(self, app, fake_auth):
        with mock_legacy_note_attachment(app):
            fake_auth.login(coe_advisor)
            stream = get_legacy_attachment_stream('9000000000_00002_1.pdf')['stream']
            body = b''
            for chunk in stream:
                body += chunk
            assert body == b'When in the course of human events, it becomes necessarf arf woof woof woof'

    def test_stream_attachment_handles_malformed_filename(self, app):
        with mock_legacy_note_attachment(app):
            assert get_legacy_attachment_stream('h0ax.lol') is None

    def test_stream_attachment_handles_file_not_in_database(self, app, fake_auth, caplog):
        with mock_legacy_note_attachment(app):
            fake_auth.login(coe_advisor)
            assert get_legacy_attachment_stream('11667051_00002_1.pdf') is None

    def test_stream_attachment_handles_file_not_in_s3(self, app, fake_auth, caplog):
        with mock_legacy_note_attachment(app):
            fake_auth.login(coe_advisor)
            assert get_legacy_attachment_stream('11667051_00001_1.pdf')['stream'] is None
            assert "the s3 key 'attachment-path/11667051/11667051_00001_1.pdf' does not exist, or is forbidden" in caplog.text
