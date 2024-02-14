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


from boac.merged.advising_appointment import get_advising_appointments, search_advising_appointments


student_sid = '11667051'


class TestMergedAdvisingAppointment:
    """Advising appointment data, merged."""

    def test_get_advising_appointments(self):
        """Returns all legacy appointments for a given SID."""
        appointments = get_advising_appointments(student_sid)
        assert len(appointments) == 3

        # Legacy SIS appointments
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
        assert appointments[0]['topics'] == ['Ofscéaw']
        assert appointments[0]['updatedAt'] is None
        assert appointments[0]['updatedBy'] is None
        assert appointments[0]['cancelReason'] is None
        assert appointments[0]['status'] in [None, 'cancelled']
        assert 'cancelReasonExplained' not in appointments[0]
        assert 'statusBy' not in appointments[0]
        assert 'statusDate' not in appointments[0]

    def test_search(self):
        """Finds legacy appointments matching the criteria, ordered by rank."""
        results = search_advising_appointments(search_phrase='life')
        assert len(results) == 1
        assert results[0]['advisorName'] == 'Loramps Glub'
        assert results[0]['advisorRole'] is None
        assert results[0]['advisorUid'] == '1081940'
        assert results[0]['advisorDeptCodes'] == ['UWASC']
        assert 'deptCode' not in results[0]
        assert results[0]['details'] == 'Art imitates life.'
        assert results[0]['detailsSnippet'] == 'Art imitates <strong>life</strong>.'
        assert 'cancelReason' not in results[0]
        assert 'cancelReasonExplained' not in results[0]
        assert 'status' not in results[0]
        assert results[0]['studentSid'] == '9100000000'
        assert results[0]['student']['uid'] == '300848'
        assert results[0]['student']['firstName'] == 'Nora Stanton'
        assert results[0]['student']['lastName'] == 'Barney'
        assert results[0]['createdAt']
        assert results[0]['updatedAt'] is None
