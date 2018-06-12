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
from boac.lib.berkeley import current_term_id
from boac.lib.mockingbird import MockResponse, register_mock
from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.models import json_cache
from boac.models.alert import Alert
from boac.models.normalized_cache_student import NormalizedCacheStudent
from boac.models.normalized_cache_student_major import NormalizedCacheStudentMajor
import pytest


@pytest.mark.usefixtures('db_session')
class TestCacheUtils:
    """Test cache utils."""

    def test_populates_normalized_cache(self, app, db):
        from boac.api.cache_utils import load_normalized_cache
        load_normalized_cache(current_term_id())

        brigitte = NormalizedCacheStudent.query.filter_by(sid='11667051').first()
        assert brigitte.level == 'Junior'
        assert brigitte.units == Decimal('101.3')
        assert brigitte.gpa == Decimal('3.8')

        student_major_rows = NormalizedCacheStudentMajor.query.filter_by(sid='11667051').all()
        assert len(student_major_rows) == 2
        majors = [row.major for row in student_major_rows]
        assert 'English BA' in majors
        assert 'Astrophysics BS' in majors

    def test_updates_normalized_cache(self, app):
        # Load default fixture data, clear the JSON cache.
        from boac.api.cache_utils import load_normalized_cache
        load_normalized_cache(current_term_id())
        json_cache.clear('sis_student_api_11667051')
        json_cache.clear('merged_sis_profile_11667051')

        # Our student levels up and changes a major.
        with open(app.config['BASE_DIR'] + '/fixtures/sis_student_api_11667051.json') as file:
            modified_response_body = file.read().replace('Junior', 'Senior').replace('Astrophysics BS', 'Hungarian BA')
            modified_response = MockResponse(200, {}, modified_response_body)
            with register_mock(sis_student_api._get_student, modified_response):
                # Without re-merging the SIS profile, reload the normalized cache.
                load_normalized_cache(current_term_id())

                # Updated fixture data is loaded.
                brigitte = NormalizedCacheStudent.query.filter_by(sid='11667051').first()
                assert brigitte.level == 'Senior'

                student_major_rows = NormalizedCacheStudentMajor.query.filter_by(sid='11667051').all()
                majors = [row.major for row in student_major_rows]
                assert len(student_major_rows) == 2
                assert 'English BA' in majors
                assert 'Hungarian BA' in majors

    def test_creates_alert_for_midterm_grade(self, app):
        merge_sis_enrollments_for_term([], '61889', '11667051', app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])
        from boac.api.cache_utils import load_alerts
        load_alerts(2178)
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')['shown']
        assert 1 == len(alerts)
        assert 0 < alerts[0]['id']
        assert 'midterm' == alerts[0]['alertType']
        assert '2178_90100' == alerts[0]['key']
        assert 'BURMESE 1A midterm grade of D+.' == alerts[0]['message']
