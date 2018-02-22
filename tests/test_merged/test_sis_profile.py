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
from boac.externals import sis_student_api
from boac.lib.mockingbird import MockResponse, register_mock
from boac.merged.sis_profile import merge_sis_profile
from boac.models import json_cache
from boac.models.normalized_cache_student import NormalizedCacheStudent
from boac.models.normalized_cache_student_major import NormalizedCacheStudentMajor
import pytest


@pytest.mark.usefixtures('db_session')
class TestSisProfile:
    """Test SIS profile."""

    def test_populates_normalized_cache(self, app):
        """Populates the normalized cache."""
        merge_sis_profile('11667051')

        student_rows = NormalizedCacheStudent.query.all()
        assert student_rows[-1].sid == '11667051'
        assert student_rows[-1].level == 'Junior'
        assert student_rows[-1].units == Decimal('101.3')
        assert student_rows[-1].gpa == Decimal('3.8')

        student_major_rows = NormalizedCacheStudentMajor.query.all()
        majors = [row.major for row in student_major_rows]
        assert 'English BA' in majors
        assert 'Astrophysics BS' in majors

    def test_updates_normalized_cache(self, app):
        """Updates the normalized cache."""
        # Load default fixture data, clear the JSON cache.
        merge_sis_profile('11667051')
        json_cache.clear('merged_sis_profile_11667051')
        json_cache.clear('sis_student_api_11667051')

        # Our student levels up and changes a major.
        with open(app.config['BASE_DIR'] + '/fixtures/sis_student_api_11667051.json') as file:
            modified_response_body = file.read().replace('Junior', 'Senior').replace('Astrophysics BS', 'Hungarian BA')
            modified_response = MockResponse(200, {}, modified_response_body)
            with register_mock(sis_student_api._get_student, modified_response):

                # The normalized cache keeps pace.
                merge_sis_profile('11667051')

                student_rows = NormalizedCacheStudent.query.all()
                assert student_rows[-1].sid == '11667051'
                assert student_rows[-1].level == 'Senior'

                student_major_rows = NormalizedCacheStudentMajor.query.all()
                majors = [row.major for row in student_major_rows]
                assert 'English BA' in majors
                assert 'Hungarian BA' in majors

    def test_skips_concurrent_academic_status(self, app):
        """Skips concurrent academic status."""
        profile = merge_sis_profile('11667051')
        assert profile['academicCareer'] == 'UGRD'
