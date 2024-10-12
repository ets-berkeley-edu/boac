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

import datetime
import re

from bea.config.bea_test_config import BEATestConfig
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.test_utils import boa_utils
from bea.test_utils import nessie_timeline_utils
from bea.test_utils import utils
import pytest


test = BEATestConfig()
test.appts_content()


@pytest.mark.usefixtures('page_objects')
class TestAdvisorLogin:

    def test_advisor_login(self):
        self.homepage.load_page()
        self.homepage.dev_auth(test.advisor)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='student',
                         argvalues=test.test_students,
                         ids=[f'UID {student.uid}' for student in test.test_students],
                         scope='class')
class TestApptsList:

    def test_load_student_page(self, student):
        self.student_page.load_page(student)
        self.student_page.show_appts()

    def test_appt_sort_order(self, student):
        appts = nessie_timeline_utils.get_sis_appts(student)
        appts.extend(nessie_timeline_utils.get_ycbm_appts(student))
        appts.sort(key=lambda ap: [ap.created_date, ap.record_id], reverse=True)
        expected_ids = [a.record_id for a in appts]
        visible_ids = self.student_page.visible_appt_ids()
        utils.assert_equivalence(visible_ids, expected_ids)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=test.test_cases,
                         ids=[f'UID {tc.student.uid} {tc.appt.record_id}' for tc in test.test_cases],
                         scope='class')
class TestApptContent:

    def test_load_student_page(self, tc):
        self.student_page.load_page(tc.student)
        self.student_page.show_appts()

    def test_collapsed_detail(self, tc):
        visible = self.student_page.collapsed_appt_detail(tc.appt)
        if tc.appt.source == TimelineRecordSource.YCBM:
            assert tc.appt.title
            utils.assert_equivalence(visible, tc.appt.title)
        elif tc.appt.source == TimelineRecordSource.SIS:
            if tc.appt.detail:
                assert visible
            else:
                placeholder = 'Imported SIS Appt'
                utils.assert_actual_includes_expected(visible, placeholder)

    def test_collapsed_status(self, tc):
        if tc.appt.status == 'Canceled':
            utils.assert_equivalence(self.student_page.collapsed_appt_status(tc.appt), 'CANCELED')

    def test_collapsed_date(self, tc):
        if tc.appt.source == TimelineRecordSource.SIS:
            assert tc.appt.updated_date
            expected = self.student_page.expected_item_short_date_format(tc.appt.updated_date)
        else:
            expected = self.student_page.expected_item_short_date_format(tc.appt.created_date)
        utils.assert_actual_includes_expected(self.student_page.collapsed_appt_date(tc.appt), expected)

    def test_expanded_details(self, tc):
        self.student_page.expand_item(tc.appt)
        if tc.appt.detail:
            assert self.student_page.expanded_appt_details(tc.appt)

    def test_expanded_date(self, tc):
        assert tc.appt.created_date
        expected = self.student_page.expected_item_short_date_format(tc.appt.created_date)
        utils.assert_equivalence(self.student_page.expanded_appt_date(tc.appt), expected)

    def test_expanded_times(self, tc):
        if tc.appt.source == TimelineRecordSource.YCBM:
            assert tc.appt.start_time
            assert tc.appt.end_time
            start = datetime.datetime.strftime(tc.appt.start_time, '%-l:%M %p')
            end = datetime.datetime.strftime(tc.appt.end_time, '%-l:%M %p')
            utils.assert_equivalence(self.student_page.expanded_appt_time_range(tc.appt), f'{start} - {end}')
        else:
            assert not tc.appt.start_time
            assert not tc.appt.end_time

    def test_expanded_advisor(self, tc):
        # Appts have varying amounts of advisor info, just verify something's there
        visible = self.student_page.expanded_appt_advisor_name(tc.appt)
        if tc.appt.advisor.full_name:
            utils.assert_equivalence(visible, tc.appt.advisor.full_name)
        elif tc.appt.advisor.last_name:
            assert visible

    def test_expanded_cancellation(self, tc):
        visible = self.student_page.expanded_appt_cancel_reason(tc.appt)
        if tc.appt.status == 'Canceled' and tc.appt.cancel_reason:
            actual = re.sub(r'\W', '', visible)
            expected = re.sub(r'\W', '', tc.appt.cancel_reason)
            utils.assert_equivalence(actual, expected)
        else:
            assert not visible

    def test_expanded_contact_type(self, tc):
        visible = self.student_page.expanded_appt_type(tc.appt)
        if tc.appt.contact_type and tc.appt.contact_type != 'None':
            utils.assert_equivalence(visible, tc.appt.contact_type)
        else:
            assert not visible

    def test_expanded_topics(self, tc):
        visible = self.student_page.expanded_appt_topics(tc.appt)
        if tc.appt.topics:
            topics = [t.upper() for t in tc.appt.topics]
            topics.sort()
            utils.assert_equivalence(visible, topics)
        else:
            assert not visible

    def test_expanded_attachments(self, tc):
        visible = self.student_page.expanded_appt_attachments(tc.appt)
        visible.sort()
        if tc.appt.attachments:
            non_deleted = [a for a in tc.appt.attachments if not a.deleted_at]
            file_names = [a.file_name for a in non_deleted]
            file_names.sort()
            utils.assert_equivalence(visible, file_names)

            for attach in non_deleted:
                if self.student_page.item_attachment_el(tc.appt, attach.file_name).tag_name == 'a':
                    self.student_page.download_attachment(tc.appt, attach, tc.student)

    def test_appt_search(self, tc):
        search_string = boa_utils.generate_appt_search_query(tc)
        if search_string:
            self.student_page.show_appts()
            self.student_page.clear_timeline_appt_search()
            appt_count = len(self.student_page.visible_appt_ids())
            self.student_page.search_within_timeline_appts(search_string)
            results = self.student_page.visible_appt_ids()
            utils.assert_actual_includes_expected(results, tc.appt.record_id)
            if appt_count > 1:
                assert len(results) < appt_count
