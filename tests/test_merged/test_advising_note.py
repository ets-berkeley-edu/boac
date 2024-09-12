"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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
import io
from zipfile import ZipFile

from boac.merged.advising_note import get_advising_notes, get_zip_stream, search_advising_notes
from boac.models.note import Note
from dateutil.parser import parse
import pytz
from tests.util import mock_eop_note_attachment, mock_sis_note_attachment


asc_advisor = '6446'
ce3_advisor_uid = '2525'
coe_advisor = '1133399'


class TestMergedAdvisingNote:
    """Advising note data, merged."""

    def test_get_advising_notes(self, app, mock_advising_note, fake_auth):
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

    def test_get_advising_notes_cs_attachment(self, app, mock_advising_note, fake_auth):
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
        results = search_advising_notes(search_phrase='herostratus')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
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

    def test_search_for_private_advising_notes(self, fake_auth, mock_private_advising_note):
        fake_auth.login(ce3_advisor_uid)
        results = search_advising_notes(search_phrase='neon', author_uid=ce3_advisor_uid)
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert total_note_count == 0
        assert notes == []

    def test_search_advising_notes_by_category(self, app, fake_auth):
        """Matches legacy category/subcategory for SIS advising notes only if body is blank."""
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='Quick Question')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert notes[0]['noteSnippet'] == '<strong>Quick</strong> <strong>Question</strong>, Unanswered'

    def test_search_for_asc_advising_notes(self, app, fake_auth):
        fake_auth.login(asc_advisor)
        results = search_advising_notes(search_phrase='kilmister')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 2
        assert len(notes) == 1
        assert notes[0]['noteSnippet'] == ''
        assert notes[0]['advisorName'] == 'Lemmy Kilmister'
        assert parse(notes[0]['createdAt']) == parse('2014-01-03T20:30:00+00')
        assert notes[0]['updatedAt'] is None
        results = search_advising_notes(search_phrase='academic')
        notes = results['notes']
        assert len(notes) == 1
        assert notes[0]['noteSnippet'] == ''
        assert notes[0]['advisorName'] == 'Lemmy Kilmister'
        assert parse(notes[0]['createdAt']) == parse('2014-01-03T20:30:00+00')
        assert notes[0]['updatedAt'] is None

    def test_search_advising_notes_stemming(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='spare')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1

        assert '<strong>spared</strong>' in notes[0]['noteSnippet']
        results = search_advising_notes(search_phrase='felicity')
        notes = results['notes']
        assert '<strong>felicities</strong>' in notes[0]['noteSnippet']

    def test_search_advising_notes_too_short_to_snippet(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='campus')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert notes[0]['noteSnippet'] == 'Is this student even on <strong>campus</strong>?'

    def test_search_advising_notes_ordered_by_relevance(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='confound')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 2
        assert total_note_count == 2
        assert notes[0]['noteSnippet'] == 'I am <strong>confounded</strong> by this <strong>confounding</strong> student'
        assert '<strong>confounded</strong> that of himself' in notes[1]['noteSnippet']

    def test_search_advising_notes_multiple_terms(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='burnt diana temple')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert 'Herostratus lives that <strong>burnt</strong> the <strong>Temple</strong> of <strong>Diana</strong>' in notes[0]['noteSnippet']

    def test_search_advising_notes_no_match(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='pyramid octopus')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 0
        assert total_note_count == 0

    def test_search_advising_notes_funny_characters(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='horse; <- epitaph? ->')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert 'Time hath spared the <strong>Epitaph</strong> of Adrians <strong>horse</strong>' in notes[0]['noteSnippet']

    def test_search_dates(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='2/1/2019 1:30')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert 'next appt. <strong>2/1/2019</strong> @ <strong>1:30</strong>. Student continued' in notes[0]['noteSnippet']
        results = search_advising_notes(search_phrase='1-24-19')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert 'drop Eng. 123 by <strong>1-24-19</strong>' in notes[0]['noteSnippet']

    def test_search_decimals(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='2.0')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert "Student continued on <strong>2.0</strong> prob (COP) until Sp '19." in notes[0]['noteSnippet']

    def test_search_email_address(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='E-mailed test@berkeley.edu')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 1
        assert total_note_count == 1
        assert "until Sp '19. <strong>E-mailed</strong> <strong>test@berkeley.edu</strong>: told her she'll need to drop Eng. 123" \
            in notes[0]['noteSnippet']

    def test_search_advising_notes_timestamp_format(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        results = search_advising_notes(search_phrase='confound')
        notes = results['notes']
        ucbconversion_note = notes[0]
        cs_note = notes[1]
        assert ucbconversion_note['createdAt']
        assert ucbconversion_note['updatedAt'] is None
        assert cs_note['createdAt']
        assert cs_note['updatedAt'] is None

    def test_search_advising_notes_includes_newly_created(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        _create_coe_advisor_note(
            sid='11667051',
            subject='Confound this note',
            body='and its successors and assigns',
        )
        results = search_advising_notes(search_phrase='confound')
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 3
        assert total_note_count == 3
        assert notes[0]['noteSnippet'] == '<strong>Confound</strong> this note - and its successors and assigns'
        assert notes[1]['noteSnippet'].startswith('I am <strong>confounded</strong>')
        assert notes[2]['noteSnippet'].startswith('...pity the founder')

    def test_search_advising_notes_paginates_new_and_old(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        for i in range(0, 5):
            _create_coe_advisor_note(
                sid='11667051',
                subject='Planned redundancy',
                body=f'Confounded note {i + 1}',
            )
        results = search_advising_notes(search_phrase='confound', offset=0, limit=4)
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 4
        assert total_note_count > 4
        assert notes[0]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 1'
        assert notes[1]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 2'
        assert notes[2]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 3'
        assert notes[3]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 4'
        results = search_advising_notes(search_phrase='confound', offset=4, limit=4)
        notes = results['notes']
        total_note_count = results['totalNoteCount']
        assert len(notes) == 3
        assert notes[0]['noteSnippet'] == 'Planned redundancy - <strong>Confounded</strong> note 5'
        assert notes[1]['noteSnippet'].startswith('I am <strong>confounded</strong>')
        assert notes[2]['noteSnippet'].startswith('...pity the founder')

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
            _create_coe_advisor_note(
                author_uid=author['uid'],
                author_name=author['name'],
                sid='11667051',
                subject='Futher on France',
                body='Brigitte has been molded to middle class circumstance',
            )
        fake_auth.login(coe_advisor)
        wide_response = search_advising_notes(search_phrase='Brigitte')
        notes = wide_response['notes']
        total_note_count = wide_response['totalNoteCount']
        assert len(notes) == 4
        assert total_note_count == 4
        narrow_response = search_advising_notes(search_phrase='Brigitte', author_csid=joni['sid'])
        notes = narrow_response['notes']
        total_note_count = narrow_response['totalNoteCount']
        assert len(notes) == 2
        assert total_note_count == 2
        new_note, legacy_note = notes[0], notes[1]
        assert new_note['advisorUid'] == joni['uid']
        assert legacy_note['advisorSid'] == joni['sid']

    def test_search_advising_notes_narrowed_by_student(self, app, fake_auth):
        """Narrows results for both new and legacy advising notes by student SID."""
        for sid in ['9000000000', '9100000000']:
            _create_coe_advisor_note(
                sid=sid,
                subject='Case load',
                body='Another day, another student',
            )
        fake_auth.login(coe_advisor)
        wide_response = search_advising_notes(search_phrase='student')
        notes = wide_response['notes']
        total_note_count = wide_response['totalNoteCount']
        assert len(notes) == 5
        assert total_note_count == 5
        narrow_response = search_advising_notes(search_phrase='student', student_csid='9100000000')
        notes = narrow_response['notes']
        assert len(notes) == 2
        new_note, legacy_note = notes[0], notes[1]
        assert new_note['studentSid'] == '9100000000'
        assert legacy_note['studentSid'] == '9100000000'

    def test_search_advising_notes_restricted_to_students_in_loch(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        _create_coe_advisor_note(
            sid='6767676767',
            subject='Who is this?',
            body="Not a student in the loch, that's for sure",
        )
        assert len(search_advising_notes(search_phrase='loch')['notes']) == 0
        _create_coe_advisor_note(
            sid='11667051',
            subject='A familiar face',
            body='Whereas this student is a most distinguished denizen of the loch',
        )
        assert len(search_advising_notes(search_phrase='loch')['notes']) == 1

    def test_search_advising_notes_narrowed_by_topic(self, app, fake_auth):
        for topic in ['Good Show', 'Bad Show']:
            _create_coe_advisor_note(
                sid='11667051',
                topics=[topic],
                subject='Brigitte',
            )
        fake_auth.login(coe_advisor)
        wide_response = search_advising_notes(search_phrase='Brigitte')
        notes = wide_response['notes']
        total_note_count = wide_response['totalNoteCount']
        assert len(notes) == 4
        assert total_note_count == 4
        narrow_response = search_advising_notes(search_phrase='Brigitte', topic='Good Show')
        notes = narrow_response['notes']
        total_note_count = narrow_response['totalNoteCount']
        assert len(notes) == 2
        assert total_note_count == 2

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
        notes = unbounded['notes']
        total_note_count = unbounded['totalNoteCount']
        assert len(notes) == 2
        assert total_note_count == 2
        lower_bound = search_advising_notes(search_phrase='Brigitte', datetime_from=days[2])
        assert len(lower_bound['notes']) == 1
        upper_bound = search_advising_notes(search_phrase='Brigitte', datetime_to=days[2])
        assert len(upper_bound['notes']) == 1
        closed_1 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[0], datetime_to=days[2])
        assert len(closed_1['notes']) == 1
        closed_2 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[2], datetime_to=days[3])
        assert len(closed_2['notes']) == 1
        closed_3 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[0], datetime_to=days[3])
        assert len(closed_3['notes']) == 2
        closed_4 = search_advising_notes(search_phrase='Brigitte', datetime_from=days[3], datetime_to=days[4])
        assert len(closed_4['notes']) == 0

    def test_search_new_advising_notes_narrowed_by_date(self, app, fake_auth):
        today = datetime.now().replace(hour=0, minute=0, second=0, tzinfo=pytz.timezone(app.config['TIMEZONE'])).astimezone(pytz.utc)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        fake_auth.login(coe_advisor)
        _create_coe_advisor_note(
            sid='11667051',
            subject='Bryant Park',
            body='There were loads of them',
        )
        assert len(search_advising_notes(search_phrase='Bryant')['notes']) == 1

        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday)['notes']) == 1
        assert len(search_advising_notes(search_phrase='Bryant', datetime_to=yesterday)['notes']) == 0
        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday, datetime_to=yesterday)['notes']) == 0

        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=tomorrow)['notes']) == 0
        assert len(search_advising_notes(search_phrase='Bryant', datetime_to=tomorrow)['notes']) == 1
        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=tomorrow, datetime_to=tomorrow)['notes']) == 0

        assert len(search_advising_notes(search_phrase='Bryant', datetime_from=yesterday, datetime_to=tomorrow)['notes']) == 1

    def test_stream_zipped_bundle(self, app):
        with mock_sis_note_attachment(app):
            for download_type in ('eForm', 'note'):
                sid = '9000000000'
                filename = 'advising_notes'
                stream = get_zip_stream(
                    download_type=download_type,
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
                if download_type == 'note':
                    assert len(contents) == 2
                    assert len(csv_rows) == 3
                    assert contents['dog_eaten_homework.pdf'] == b'When in the course of human events, it becomes necessarf arf woof woof woof'
                    assert csv_rows[0] == 'date_created,student_sid,student_name,author_uid,author_csid,author_name,' \
                                          'subject,body,topics,attachments,is_private'
                    assert csv_rows[1] == "2017-11-02,9000000000,Wolfgang Pauli-O'Rourke,,700600500,,," \
                                          'I am confounded by this confounding student,,dog_eaten_homework.pdf,False'
                    assert csv_rows[2] == "2017-11-02,9000000000,Wolfgang Pauli-O'Rourke,,600500400,,," \
                                          'Is this student even on campus?,Ne Scéaw,,False'
                else:
                    assert len(contents) == 1
                    assert len(csv_rows) == 2
                    assert csv_rows[0] == 'student_sid,student_name,eform_id,eform_type,requested_action,' \
                                          'grading_basis,requested_grading_basis,units_taken,requested_units_taken,' \
                                          'late_change_request_action,late_change_request_status,' \
                                          'late_change_request_term,late_change_request_course,date_created,updated_at'
                    assert csv_rows[1] == "9000000000,Wolfgang Pauli-O'Rourke,469118,SRLATEDROP," \
                                          'Late Grading Basis Change,Elective Pass/No Pass,Graded,3,0.00,' \
                                          'Late Grading Basis Change,In Error,Fall 2020,' \
                                          '24460 PSYCH 110 - INTROD BIOL PSYCH 001,2020-12-05,2020-12-04'


def _create_coe_advisor_note(
    sid,
    subject,
    body='',
    topics=(),
    author_uid=coe_advisor,
    author_name='Balloon Man',
    author_role='Spherical',
    author_dept_codes='COENG',
):
    Note.create(
        author_uid=author_uid,
        author_name=author_name,
        author_role=author_role,
        author_dept_codes=author_dept_codes,
        topics=topics,
        sid=sid,
        subject=subject,
        body=body,
    )
    Note.refresh_search_index()
