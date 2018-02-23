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


from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.models.alert import Alert
from boac.models.normalized_cache_course_sections import NormalizedCacheCourseSection
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

    def test_populates_normalized_cache(self, app):
        """Populates the normalized cache."""
        merge_sis_enrollments_for_term([], '11667051', app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])
        section = NormalizedCacheCourseSection.query.first()
        assert section.term_id
        assert section.section_id
        assert section.dept_name
        assert section.dept_code
        assert section.catalog_id
        assert section.display_name
        assert section.title
        assert section.instruction_format
        assert section.section_num
        assert section.units
        assert len(section.meeting_days)
        assert len(section.meeting_times)
        assert len(section.locations)
        assert len(section.instructors)
