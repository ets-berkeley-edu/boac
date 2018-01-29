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
