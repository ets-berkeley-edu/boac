"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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


from boac.merged.advising_appointment import get_advising_appointments, search_advising_appointments


coe_advisor_uid = '1133399'
student_sid = '11667051'


class TestMergedAdvisingAppointment:
    """Advising appointment data, merged."""

    def test_get_advising_appointments(self, app, fake_auth):
        """Returns all legacy and BOA appointments for a given SID."""
        appointments = get_advising_appointments(student_sid)
        assert len(appointments) == 5

        # Legacy SIS appointments
        advisor_user_id = appointments[0]['advisor']['id']
        assert appointments[0]['id'] == '11667051-00010'
        assert appointments[0]['advisor']
        assert appointments[0]['advisor']['name'] == 'Milicent Balthazar'
        assert appointments[0]['advisor']['sid'] == '53791'
        assert appointments[0]['advisor']['title'] is None
        assert appointments[0]['advisor']['uid'] == '53791'
        assert appointments[0]['advisor']['departments'] == []
        assert appointments[0]['appointmentType'] is None
        assert len(appointments[0]['attachments']) == 1
        assert appointments[0]['createdAt'] == '2017-10-31T12:00:00+00:00'
        assert appointments[0]['createdBy'] in [None, 'YCBM']
        assert appointments[0]['deptCode'] is None
        assert appointments[0]['details'] == 'To my people who keep an impressive wingspan even when the cubicle shrink: \
you got to pull up the intruder by the root of the weed; N.Y. Chew through the machine'
        assert appointments[0]['legacySource'] == 'SIS'
        assert appointments[0]['student']
        assert appointments[0]['student']['sid'] == student_sid
        assert appointments[0]['topics'] is None
        assert appointments[0]['updatedAt'] is None
        assert appointments[0]['updatedBy'] is None
        assert appointments[0]['cancelReason'] is None
        assert appointments[0]['status'] in [None, 'cancelled']
        assert 'cancelReasonExplained' not in appointments[0]
        assert 'statusBy' not in appointments[0]
        assert 'statusDate' not in appointments[0]

        # Non-legacy appointments
        assert appointments[3]['id'] == 5
        assert appointments[3]['advisor']
        assert appointments[3]['advisor']['name'] == 'Milicent Balthazar'
        assert appointments[3]['advisor']['title'] == 'Advisor'
        assert appointments[3]['advisor']['uid'] == '53791'
        assert appointments[3]['advisor']['departments'] == [
            {'code': 'QCADV', 'name': 'L&S College Advising'},
            {'code': 'QCADVMAJ', 'name': 'L&S Major Advising'},
        ]
        assert appointments[3]['appointmentType'] == 'Drop-in'
        assert appointments[3]['attachments'] is None
        assert appointments[3]['createdAt']
        assert appointments[3]['createdBy'] == advisor_user_id
        assert appointments[3]['deptCode'] == 'QCADV'
        assert appointments[3]['details'] == 'It is not the length of life, but depth of life.'
        assert 'legacySource' not in appointments[3]
        assert appointments[3]['student']
        assert appointments[3]['student']['sid'] == student_sid
        assert appointments[3]['topics'] == ['Topic for appointments, 1']
        assert appointments[3]['updatedBy'] == advisor_user_id
        assert appointments[3]['cancelReason'] is None
        assert appointments[3]['cancelReasonExplained'] is None
        assert appointments[3]['status'] == 'checked_in'
        assert appointments[3]['statusBy']
        assert appointments[3]['statusBy']['id'] == advisor_user_id
        assert appointments[3]['statusBy']['uid'] == '53791'
        assert appointments[3]['statusBy']['csid'] == '53791'
        assert appointments[3]['statusBy']['name'] == 'Milicent Balthazar'
        assert appointments[3]['statusBy']['lastName'] == 'Balthazar'
        assert appointments[3]['statusBy']['firstName'] == 'Milicent'
        assert appointments[3]['statusDate']

        assert appointments[4]['id'] == 10
        assert appointments[4]['advisor']
        assert appointments[4]['advisor']['id'] is None
        assert appointments[4]['advisor']['name'] == ''
        assert appointments[4]['advisor']['title'] is None
        assert appointments[4]['advisor']['uid'] is None
        assert appointments[4]['advisor']['departments'] == []
        assert appointments[4]['appointmentType'] == 'Drop-in'
        assert appointments[4]['attachments'] is None
        assert appointments[4]['createdAt']
        assert appointments[4]['createdBy'] == advisor_user_id
        assert appointments[4]['deptCode'] == 'QCADV'
        assert appointments[4]['details'] == 'You be you.'
        assert 'legacySource' not in appointments[4]
        assert appointments[4]['student']
        assert appointments[4]['student']['sid'] == student_sid
        assert appointments[4]['topics'] == ['Topic for appointments, 1']
        assert appointments[4]['updatedAt'] is None
        assert appointments[4]['updatedBy'] == advisor_user_id
        assert appointments[4]['cancelReason'] is None
        assert appointments[4]['cancelReasonExplained'] is None
        assert appointments[4]['status'] == 'waiting'
        assert appointments[4]['statusBy']
        assert appointments[4]['statusBy']['id'] == advisor_user_id
        assert appointments[4]['statusBy']['uid'] == '53791'
        assert appointments[4]['statusBy']['csid'] == '53791'
        assert appointments[4]['statusBy']['name'] == 'Milicent Balthazar'
        assert appointments[4]['statusBy']['lastName'] == 'Balthazar'
        assert appointments[4]['statusBy']['firstName'] == 'Milicent'
        assert appointments[4]['statusDate']

    def test_search(self, fake_auth):
        """Finds new and legacy appointments matching the criteria, ordered by rank."""
        fake_auth.login(coe_advisor_uid)
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
