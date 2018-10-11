"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


from decimal import Decimal
import io

from boac.externals import data_loch
from boac.lib.mockingdata import MockRows, register_mock
import pytest


@pytest.mark.usefixtures('db_session')
class TestDataLoch:

    def test_sis_enrollments(self, app):
        enrollments = data_loch.get_sis_enrollments(61889, 2178)

        assert len(enrollments) == 5

        assert enrollments[0]['sis_course_name'] == 'BURMESE 1A'
        assert enrollments[0]['sis_section_num'] == '001'
        assert enrollments[0]['sis_enrollment_status'] == 'E'
        assert enrollments[0]['units'] == 4
        assert enrollments[0]['grading_basis'] == 'GRD'

        assert enrollments[1]['sis_course_name'] == 'MED ST 205'
        assert enrollments[1]['sis_section_num'] == '001'
        assert enrollments[1]['sis_enrollment_status'] == 'E'
        assert enrollments[1]['units'] == 5
        assert enrollments[1]['grading_basis'] == 'GRD'

        assert enrollments[2]['sis_course_name'] == 'NUC ENG 124'
        assert enrollments[2]['sis_section_num'] == '201'
        assert enrollments[2]['sis_enrollment_status'] == 'E'
        assert enrollments[2]['units'] == 0
        assert enrollments[2]['grading_basis'] == 'NON'
        assert not enrollments[2]['grade']

        assert enrollments[3]['sis_course_name'] == 'NUC ENG 124'
        assert enrollments[3]['sis_section_num'] == '002'
        assert enrollments[3]['sis_enrollment_status'] == 'E'
        assert enrollments[3]['units'] == 3
        assert enrollments[3]['grading_basis'] == 'PNP'
        assert enrollments[3]['grade'] == 'P'

        assert enrollments[4]['sis_course_name'] == 'PHYSED 11'
        assert enrollments[4]['sis_section_num'] == '001'
        assert enrollments[4]['sis_enrollment_status'] == 'E'
        assert enrollments[4]['units'] == 0.5
        assert enrollments[4]['grading_basis'] == 'PNP'
        assert enrollments[4]['grade'] == 'P'

    def test_get_term_gpas(self, app):
        term_gpas = data_loch.get_term_gpas(['11667051'])
        assert len(term_gpas) == 4
        assert term_gpas[0]['term_id'] == '2182'
        assert term_gpas[0]['sid'] == '11667051'
        assert term_gpas[0]['gpa'] == Decimal('2.900')
        assert term_gpas[0]['units_taken_for_gpa'] == 14
        assert term_gpas[3]['term_id'] == '2162'
        assert term_gpas[3]['sid'] == '11667051'
        assert term_gpas[3]['gpa'] == Decimal('3.800')
        assert term_gpas[3]['units_taken_for_gpa'] == 15

    def test_override_fixture(self, app):
        mr = MockRows(io.StringIO('sid,first_name,last_name\n20000000,Martin,Van Buren'))
        with register_mock(data_loch.get_sis_section_enrollments, mr):
            data = data_loch.get_sis_section_enrollments(2178, 12345)
        assert len(data) == 1
        assert {'sid': 20000000, 'first_name': 'Martin', 'last_name': 'Van Buren'} == data[0]

    def test_fixture_not_found(self, app):
        no_db = data_loch.get_sis_section_enrollments(0, 0)
        # TODO Real data_loch queries will return an empty list if the course is not found.
        assert no_db is None
