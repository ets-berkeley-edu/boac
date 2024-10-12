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

import re

from bea.config.bea_test_config import BEATestConfig
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest

test = BEATestConfig()
test.note_content()
list_tcs = [tc for tc in test.test_cases if isinstance(tc.note, list)]
detail_tcs = [tc for tc in test.test_cases if not isinstance(tc.note, list)]


@pytest.mark.usefixtures('page_objects')
class TestAdvisorLogin:

    def test_log_in(self):
        self.homepage.load_page()
        self.homepage.dev_auth(test.advisor)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=list_tcs,
                         ids=[tc.test_case_id for tc in list_tcs],
                         scope='class')
class TestNoteList:

    def test_load_student_notes(self, tc):
        self.student_page.load_page(tc.student)
        self.student_page.show_notes()

    def test_notes_all_present(self, tc):
        visible = self.student_page.visible_collapsed_note_ids()
        visible.sort()
        expected = [n.record_id for n in tc.note]
        expected.sort()
        utils.assert_equivalence(visible, expected)

    def test_order(self, tc):
        visible = self.student_page.visible_collapsed_note_ids()
        expected = self.student_page.expected_note_id_sort_order(tc.note)
        utils.assert_equivalence(visible, expected)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=detail_tcs,
                         ids=[tc.test_case_id for tc in detail_tcs],
                         scope='class')
class TestNoteDetail:

    def test_load_student_note(self, tc):
        if tc.student.uid not in self.driver.current_url:
            self.student_page.load_page(tc.student)
        self.student_page.show_notes()

    def test_collapsed_date(self, tc):
        show_update_date = self.student_page.is_updated_date_expected(tc.note)
        expected_date = tc.note.set_date or (tc.note.updated_date if show_update_date else tc.note.created_date)
        expected = self.student_page.expected_item_short_date_format(expected_date)
        visible = self.student_page.collapsed_note_date(tc.note)
        utils.assert_equivalence(visible, expected)

    def test_collapsed_subject(self, tc):
        visible = self.student_page.collapsed_note_subject(tc.note).strip()
        if tc.note.subject:
            utils.assert_equivalence(visible, tc.note.subject)
        elif tc.note.source in [TimelineRecordSource.ASC, TimelineRecordSource.DATA, TimelineRecordSource.HISTORY,
                                TimelineRecordSource.SIS] and tc.note.body:
            assert visible
        elif tc.note.source == TimelineRecordSource.ASC:
            utils.assert_actual_includes_expected(visible, 'Athletic Study Center advisor')
        else:
            assert not visible

    def test_expanded_body(self, tc):
        self.student_page.expand_item(tc.note)
        visible = self.student_page.expanded_note_body(tc.note)
        if tc.note.subject and tc.note.body and not tc.note.is_private:
            assert visible
        if tc.note.source == TimelineRecordSource.E_AND_I or tc.note.is_private:
            assert not visible

    def test_expanded_source(self, tc):
        visible = self.student_page.expanded_note_source(tc.note)
        if tc.note.source:
            utils.assert_equivalence(visible, f"(note imported from {tc.note.source.value['name']})")
        else:
            assert not visible

    def test_expanded_topics(self, tc):
        visible = self.student_page.expanded_note_topics(tc.note)
        if tc.note.topics:
            app.logger.info(f'TOPICS: {tc.note.topics}')
            topics = list(set([t.upper() for t in tc.note.topics]))
            topics.sort()
            utils.assert_equivalence(visible, topics)
        else:
            assert not visible

    def test_expanded_updated_date(self, tc):
        visible = self.student_page.expanded_note_updated_date(tc.note)
        if self.student_page.is_updated_date_expected(tc.note):
            expected = self.student_page.expected_item_long_date_format(tc.note.updated_date)
            utils.assert_equivalence(visible, expected)
        else:
            assert not visible

    def test_expanded_created_date(self, tc):
        visible = self.student_page.expanded_note_created_date(tc.note)
        if tc.note.advisor and tc.note.advisor.uid == 'UCBCONVERSION':
            expected = self.student_page.expected_item_short_date_format(tc.note.created_date)
        else:
            expected = self.student_page.expected_item_long_date_format(tc.note.created_date)
        utils.assert_equivalence(visible, expected)

    def test_expanded_attachment_files(self, tc):
        visible = self.student_page.expanded_note_attachments(tc.note)
        visible.sort()
        if tc.note.attachments:
            if tc.note.is_private:
                assert not visible
            else:
                non_deleted = [a for a in tc.note.attachments if not a.deleted_at]
                expected = [re.sub(r'\s+', ' ', a.file_name) for a in non_deleted]
                expected.sort()
                utils.assert_equivalence(visible, expected)
                for attach in non_deleted:
                    if attach.sis_file_name:
                        assert not self.student_page.is_present(
                            self.student_page.existing_note_attachment_delete_button(tc.note, attach))

    def test_timeline_note_search(self, tc):
        query = boa_utils.generate_note_search_query(tc.note)
        if query:
            self.student_page.search_within_timeline_notes(query)
            visible = self.student_page.visible_collapsed_note_ids()
            utils.assert_actual_includes_expected(visible, tc.note.record_id)

    def test_permalink(self, tc):
        url = self.student_page.expanded_note_permalink_url(tc.note)
        assert url
        if url:
            self.homepage.load_page()
            self.student_page.hit_note_permalink(tc.note, url)

    def test_expanded_attachment_downloads(self, tc):
        if tc.note.attachments and not tc.note.is_private:
            non_deleted = [a for a in tc.note.attachments if not a.deleted_at]
            for attach in non_deleted:
                self.student_page.download_attachment(tc.note, attach, tc.student)
