"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.merged.student import get_course_student_profiles, get_distilled_student_profiles


coe_advisor = '1133399'


class TestMergedStudent:
    """Student data, merged."""

    def test_get_course_student_profiles(self):
        profiles = get_course_student_profiles('2178', '90100')

        assert len(profiles['students']) == 1
        assert profiles['students'][0]['sid'] == '11667051'

    def test_get_distilled_student_profiles(self):
        """Returns basic profiles of both current and non-current students."""
        profiles = get_distilled_student_profiles(['11667051', '2718281828'])
        assert len(profiles) == 2
        assert profiles[0]['firstName'] == 'Deborah'
        assert profiles[0]['gender'] == 'Different Identity'
        assert profiles[0]['lastName'] == 'Davies'
        assert profiles[0]['name'] == 'Deborah Davies'
        assert 'https://photo-bucket.s3.amazonaws.com/photo-path' in profiles[0]['photoUrl']
        assert profiles[0]['sid'] == '11667051'
        assert profiles[0]['uid'] == '61889'
        assert profiles[0]['underrepresented'] is False
        assert profiles[0]['athleticsProfile']

        assert profiles[1]['firstName'] == 'Ernest'
        assert profiles[1]['gender'] is None
        assert profiles[1]['lastName'] == 'Pontifex'
        assert profiles[1]['name'] == 'Ernest Pontifex'
        assert 'https://photo-bucket.s3.amazonaws.com/photo-path' in profiles[1]['photoUrl']
        assert profiles[1]['sid'] == '2718281828'
        assert profiles[1]['uid'] == '27182'
        assert profiles[1]['underrepresented'] is None
