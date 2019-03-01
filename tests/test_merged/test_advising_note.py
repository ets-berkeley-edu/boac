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

from boac.merged.advising_note import get_advising_notes, search_advising_notes


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
        assert notes[0]['createdAt'] == '2017-10-31 12:00:00'
        assert notes[0]['updatedBy'] is None
        assert notes[0]['updatedAt'] == '2017-10-31 12:00:00'
        assert notes[0]['read'] is False
        assert notes[0]['topics'] == ['Good show']
        assert notes[0]['attachments'] == ['form.pdf']
        assert notes[1]['id'] == '11667051-00002'
        assert notes[1]['sid'] == '11667051'
        assert notes[1]['body'] == 'Brigitte demonstrates a cavalier attitude toward university requirements'
        assert notes[1]['category'] == 'Evaluation'
        assert notes[1]['subcategory'] == ''
        assert notes[1]['appointmentId'] is None
        assert notes[1]['createdBy'] is None
        assert notes[1]['createdAt'] == '2017-11-01 12:00:00'
        assert notes[1]['updatedBy'] is None
        assert notes[1]['updatedAt'] == '2017-11-01 12:00:00'
        assert notes[1]['read'] is False
        assert notes[1]['topics'] == ['Bad show']
        assert notes[1]['attachments'] == ['photo.jpeg']
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

    def test_get_advising_notes_timestamp_format(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        notes = get_advising_notes('9000000000')
        ucbconversion_note = notes[0]
        cs_note = notes[1]
        assert ucbconversion_note['createdAt'] == '2017-11-02'
        assert ucbconversion_note['updatedAt'] is None
        assert cs_note['createdAt'] == '2017-11-02 12:00:00'
        assert cs_note['updatedAt'] == '2017-11-02 13:00:00'

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
        assert notes[0]['noteId'] == '11667051-00003'
        assert notes[0]['createdAt'] == '2017-11-05 12:00:00'
        assert notes[0]['updatedAt'] == '2017-11-06 12:00:00'

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

    def test_search_advising_notes_timestamp_format(self, app, fake_auth):
        fake_auth.login(coe_advisor)
        response = search_advising_notes(search_phrase='confound')
        ucbconversion_note = response[0]
        cs_note = response[1]
        assert ucbconversion_note['createdAt'] == '2017-11-02'
        assert ucbconversion_note['updatedAt'] is None
        assert cs_note['createdAt'] == '2017-11-05 12:00:00'
        assert cs_note['updatedAt'] == '2017-11-06 12:00:00'
