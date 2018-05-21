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


from boac.api.util import canvas_courses_api_feed
from boac.externals import data_loch
from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.models.alert import Alert
import pytest


@pytest.mark.usefixtures('db_session')
class TestMergedSisEnrollments:

    def test_creates_alert_for_midterm_grade(self, app):
        feed = merge_sis_enrollments_for_term([], '11667051', app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])
        assert '2178' == feed['termId']
        enrollments = feed['enrollments']
        assert 3 == len(enrollments)
        assert 'D+' == enrollments[0]['midtermGrade']
        assert 'BURMESE 1A' == enrollments[0]['displayName']
        assert 90100 == enrollments[0]['sections'][0]['ccn']
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')['shown']
        assert 1 == len(alerts)
        assert 0 < alerts[0]['id']
        assert 'midterm' == alerts[0]['alertType']
        assert '2178_90100' == alerts[0]['key']
        assert 'BURMESE 1A midterm grade of D+.' == alerts[0]['message']

    def test_includes_course_site_section_mappings(self, app):
        """Maps Canvas sites to SIS courses and sections."""
        canvas_site_feed = canvas_courses_api_feed(data_loch.get_student_canvas_courses('61889'))
        feed = merge_sis_enrollments_for_term(canvas_site_feed, '11667051', app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])
        enrollments = feed['enrollments']
        assert len(enrollments[0]['canvasSites']) == 1
        assert enrollments[0]['canvasSites'][0]['canvasCourseId'] == 7654320
        assert enrollments[0]['sections'][0]['canvasCourseIds'] == [7654320]
        assert len(enrollments[1]['canvasSites']) == 1
        assert enrollments[1]['canvasSites'][0]['canvasCourseId'] == 7654321
        assert enrollments[1]['sections'][0]['canvasCourseIds'] == [7654321]
        assert len(enrollments[2]['canvasSites']) == 2
        assert enrollments[2]['canvasSites'][0]['canvasCourseId'] == 7654323
        assert enrollments[2]['canvasSites'][1]['canvasCourseId'] == 7654330
        assert (enrollments[2]['sections'][0]['canvasCourseIds']) == [7654323, 7654330]
        assert (enrollments[2]['sections'][1]['canvasCourseIds']) == []
