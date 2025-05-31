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


from boac.merged.advising_appointment import get_advising_appointments, search_advising_appointments


student_sid = '11667051'


class TestMergedAdvisingAppointment:
    """Advising appointment data, merged."""

    def test_get_advising_appointments(self):
        """Returns all legacy appointments for a given SID."""
        appointments = get_advising_appointments(student_sid)
        assert len(appointments) == 4

        # Verify Calendly appointment
        calendly_appointment = next((a for a in appointments if a['createdBy'] == 'Calendly'), None)
        assert calendly_appointment
        assert calendly_appointment['advisor']['name'] == 'Edwin Land'
        assert 'Can you picture this?' in calendly_appointment['details']
        assert calendly_appointment['appointmentTitle'] == 'Shake it like a Polaroid'

        # Verify YCBM appointment
        ycbm_appointment = next((a for a in appointments if a['createdBy'] == 'YCBM'), None)
        assert ycbm_appointment
        assert ycbm_appointment['id'] == '11667051-00010'
        assert ycbm_appointment['advisor']
        assert ycbm_appointment['advisor']['name'] == 'Milicent Balthazar'
        assert ycbm_appointment['advisor']['sid'] == '53791'
        assert ycbm_appointment['advisor']['title'] is None
        assert ycbm_appointment['advisor']['uid'] == '53791'
        assert ycbm_appointment['advisor']['departments'] == []
        assert ycbm_appointment['appointmentType'] is None
        assert len(ycbm_appointment['attachments']) == 1
        assert ycbm_appointment['createdAt'] == '2017-10-31T12:00:00+00:00'
        assert ycbm_appointment['createdBy'] == 'YCBM'
        assert ycbm_appointment['deptCode'] is None
        assert ycbm_appointment['details'] == 'To my people who keep an impressive wingspan even when the cubicle shrink: \
you got to pull up the intruder by the root of the weed; N.Y. Chew through the machine'
        assert ycbm_appointment['legacySource'] == 'SIS'
        assert ycbm_appointment['student']
        assert ycbm_appointment['student']['sid'] == student_sid
        assert ycbm_appointment['topics'] == ['Ofscéaw']
        assert ycbm_appointment['updatedAt'] is None
        assert ycbm_appointment['updatedBy'] is None
        assert ycbm_appointment['cancelReason'] is None
        assert ycbm_appointment['status'] in [None, 'cancelled']
        assert 'cancelReasonExplained' not in ycbm_appointment
        assert 'statusBy' not in ycbm_appointment
        assert 'statusDate' not in ycbm_appointment

    def test_search(self):
        """Finds legacy appointments matching the criteria, ordered by rank."""
        results = search_advising_appointments(search_phrase='life')
        appointments = results['appointments']
        assert len(appointments) == 1
        assert results['totalAppointmentCount'] == 1
        assert appointments[0]['advisorName'] == 'Loramps Glub'
        assert appointments[0]['advisorRole'] is None
        assert appointments[0]['advisorUid'] == '1081940'
        assert appointments[0]['advisorDeptCodes'] == ['UWASC']
        assert 'deptCode' not in appointments[0]
        assert appointments[0]['details'] == 'Art imitates life.'
        assert appointments[0]['detailsSnippet'] == 'Art imitates <strong>life</strong>.'
        assert 'cancelReason' not in appointments[0]
        assert 'cancelReasonExplained' not in appointments[0]
        assert 'status' not in appointments[0]
        assert appointments[0]['studentSid'] == '9100000000'
        assert appointments[0]['student']['uid'] == '300848'
        assert appointments[0]['student']['firstName'] == 'Nora Stanton'
        assert appointments[0]['student']['lastName'] == 'Barney'
        assert appointments[0]['createdAt']
        assert appointments[0]['updatedAt'] is None
