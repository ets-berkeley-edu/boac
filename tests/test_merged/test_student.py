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

from boac.merged.student import get_advising_notes, get_course_student_profiles, search_advising_notes


coe_advisor = '1133399'


class TestStudent:
    """Student."""

    def test_get_course_student_profiles(self, app):
        profiles = get_course_student_profiles('2178', '90100')

        assert len(profiles['students']) == 1
        assert profiles['students'][0]['cumulativeUnits'] == 101.3
        assert profiles['students'][0]['currentTerm']['unitsMaxOverride'] == 25
        assert profiles['students'][0]['currentTerm']['unitsMinOverride'] == 0

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
        assert notes[3]['authorId']
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
        assert notes[0]['updatedAt'] == '2017-11-05 12:00:00'
