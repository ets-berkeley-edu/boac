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

from boac.merged import admitted_student


class TestMergedAdmittedStudent:
    """Admitted student data, merged."""

    def test_get_admitted_student_by_sid(self):
        admit = admitted_student.get_admitted_student_by_sid('00005852')
        assert admit['applyucCpid'] == '19938035'
        assert admit['sid'] == '00005852'
        assert admit['uid'] == '123'
        assert admit['studentUid'] is None
        assert admit['updatedAt'] == '2017-10-31T12:00:00+00:00'

    def test_get_admit_with_student_record(self):
        """When there is a corresponding student record, student uid is populated."""
        admit = admitted_student.get_admitted_student_by_sid('11667051')
        assert admit['applyucCpid'] == '44631475'
        assert admit['sid'] == '11667051'
        assert admit['uid'] == '61889'
        assert admit['studentUid'] == '61889'
        assert admit['updatedAt'] == '2017-10-31T12:00:00+00:00'
