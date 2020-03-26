"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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


from boac.merged.advising_appointment import get_appointment_advisors, search_advising_appointments


coe_advisor = '1133399'


class TestMergedAdvisingAppointment:
    """Advising appointment data, merged."""

    def test_get_appointment_advisors(self, fake_auth):
        """Returns a combined list of appointment advisors past and present."""
        fake_auth.login(coe_advisor)
        advisors = get_appointment_advisors(['CO'])
        assert len(advisors) == 1

        advisors = get_appointment_advisors(['C'])
        assert len(advisors) == 3

        advisors = get_appointment_advisors(['MI', 'BA'])
        assert len(advisors) == 1

    def test_search(self, fake_auth, app):
        """Finds new and legacy appointments matching the criteria, ordered by rank."""
        fake_auth.login(coe_advisor)
        results = search_advising_appointments(search_phrase='life')
        assert len(results) == 3
        assert results[0]['advisorName'] == 'Milicent Balthazar'
        assert results[0]['advisorRole'] == 'Advisor'
        assert results[0]['advisorUid'] == '53791'
        assert results[0]['advisorDeptCodes'] == ['QCADV', 'QCADVMAJ']
        assert results[0]['deptCode'] == 'QCADV'
        assert results[0]['details'] == 'It is not the length of life, but depth of life.'
        assert results[0]['detailsSnippet'] == 'It is not the length of <strong>life</strong>, but depth of <strong>life</strong>.'
        assert results[0]['cancelReason'] is None
        assert results[0]['cancelReasonExplained'] is None
        assert results[0]['status'] == 'checked_in'
        assert results[0]['studentSid'] == '11667051'
        assert results[0]['student']['uid'] == '61889'
        assert results[0]['student']['firstName'] == 'Deborah'
        assert results[0]['student']['lastName'] == 'Davies'
        assert results[0]['createdAt']
        assert results[0]['updatedAt']

        assert results[1]['advisorName'] is None
        assert results[1]['advisorRole'] is None
        assert results[1]['advisorUid'] is None
        assert results[1]['advisorDeptCodes'] is None
        assert results[1]['deptCode'] == 'COENG'
        assert results[1]['details'] == 'Life is what happens while you\'re making appointments.'
        assert results[1]['detailsSnippet'] == '<strong>Life</strong> is what happens while you\'re making appointments.'
        assert results[1]['cancelReason'] is None
        assert results[1]['cancelReasonExplained'] is None
        assert results[1]['status'] == 'waiting'
        assert results[1]['studentSid'] == '5678901234'
        assert results[1]['student']['uid'] == '9933311'
        assert results[1]['student']['firstName'] == 'Sandeep'
        assert results[1]['student']['lastName'] == 'Jayaprakash'
        assert results[1]['createdAt']
        assert results[1]['updatedAt']

        assert results[2]['advisorName'] == 'Loramps Glub'
        assert results[2]['advisorRole'] is None
        assert results[2]['advisorUid'] == '1081940'
        assert results[2]['advisorDeptCodes'] == ['UWASC']
        assert 'deptCode' not in results[2]
        assert results[2]['details'] == 'Art imitates life.'
        assert results[2]['detailsSnippet'] == 'Art imitates <strong>life</strong>.'
        assert 'cancelReason' not in results[2]
        assert 'cancelReasonExplained' not in results[2]
        assert 'status' not in results[2]
        assert results[2]['studentSid'] == '9100000000'
        assert results[2]['student']['uid'] == '300848'
        assert results[2]['student']['firstName'] == 'Nora Stanton'
        assert results[2]['student']['lastName'] == 'Barney'
        assert results[2]['createdAt']
        assert results[2]['updatedAt'] is None
