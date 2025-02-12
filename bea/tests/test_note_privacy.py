"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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
from datetime import datetime
import random
import time

from bea.config.bea_test_config import BEATestConfig
from bea.models.advisor_role import AdvisorRole
from bea.models.department import Department
from bea.models.department_membership import DepartmentMembership
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.note_batch import NoteBatch
from bea.models.notes_and_appts.note_template import NoteTemplate
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.models.notes_and_appts.topic import Topic, Topics
from bea.test_utils import boa_utils
from bea.test_utils import nessie_timeline_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest

test = BEATestConfig()
test.user_role_advisor()
random.shuffle(test.students)

# L&S config
test_ls = BEATestConfig()
test_ls.user_role_l_and_s(test)
ls_cohorts = boa_utils.get_everyone_filtered_cohorts(test_ls.dept)
ls_groups = boa_utils.get_everyone_curated_groups(test_ls.dept)

# CE3 config
test_ce3 = BEATestConfig()
test_ce3.user_role_ce3(test)

student = test.students[-1]
topics = [Topic(Topics.COURSE_ADD.value), Topic(Topics.COURSE_DROP.value)]
attachments = test.attachments[0:2]

note_1 = Note({
    'advisor': test_ce3.advisor,
    'body': f'Note 1 body {test.test_id}',
    'student': student,
    'subject': f'Note 1 {test.test_id}',
})
note_2 = Note({
    'advisor': test_ce3.advisor,
    'body': f'Note 2 body {test.test_id}',
    'student': student,
    'subject': f'Note 2 {test.test_id}',
})
note_3 = Note({
    'advisor': test_ls.advisor,
    'body': f'Note 3 body {test.test_id}',
    'student': student,
    'subject': f'Note 3 {test.test_id}',
})

batch_1 = NoteBatch({
    'advisor': test_ce3.advisor,
    'is_private': True,
    'subject': f'Batch 1 {test.test_id}',
})
batch_2 = NoteBatch({
    'advisor': test_ce3.advisor,
    'is_private': False,
    'subject': f'Batch 2 {test.test_id}',
})

ce3_template = NoteTemplate({'title': f'CE3 template {test.test_id}'})

eop_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.EOP, eop_private=True)
eop_student = [s for s in test.students if s.sid in eop_sids][0]
eop_student_notes = nessie_timeline_utils.get_eop_notes(eop_student)
eop_note = next(filter(lambda n: n.is_private and n.attachments, eop_student_notes))
app.logger.info(f'EOP UID {eop_student.uid}, note id {eop_note.record_id}')


@pytest.mark.usefixtures('page_objects')
class TestNoteImportedFromEOP:

    def test_shows_private_data_to_ce3_advisor(self):
        self.homepage.load_page()
        self.homepage.dev_auth(test_ce3.advisor)
        self.student_page.load_page(eop_student)
        self.student_page.show_notes()
        self.student_page.verify_note(eop_note, test_ce3.advisor)

    def test_allows_attachment_downloads_for_ce3_advisor(self):
        for attach in eop_note.attachments:
            self.student_page.download_attachment(eop_note, attach, eop_student)

    def test_hides_private_data_from_non_ce3_advisor(self):
        self.student_page.log_out()
        self.homepage.dev_auth(test_ls.advisor)
        self.student_page.load_page(eop_student)
        self.student_page.show_notes()
        self.student_page.verify_note(eop_note, test_ls.advisor)

    def test_blocks_body_and_attachments_access_via_api_for_non_ce3_advisor(self):
        notes = self.api_student_page.student_notes(eop_student)
        note = next(filter(lambda n: n['id'] == eop_note.record_id, notes))
        assert not note['body']
        assert not note['attachments']

    def test_blocks_note_attachment_download_via_api_for_non_ce3_advisor(self):
        utils.prepare_download_dir()
        self.api_notes_page.load_attachment_page(eop_note.attachments[0].file_name)
        self.api_notes_page.when_present(self.api_notes_page.ATTACH_NOT_FOUND_MSG, utils.get_short_timeout())
        assert utils.is_download_dir_empty()

    def test_blocks_search_by_body_for_all(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(test_ce3.advisor)
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.set_notes_student(eop_student)
        self.homepage.enter_adv_search_and_hit_enter(eop_note.body)
        self.search_results_page.assert_note_result_not_present(eop_note)


@pytest.mark.usefixtures('page_objects')
class TestNoteCreatedByCE3Advisor:

    def test_note_can_be_private(self):
        self.student_page.load_page(student)
        note_1.is_private = True
        self.student_page.create_note(note_1, topics, [attachments[0]])
        assert boa_utils.is_note_private(note_1)

    def test_note_can_be_non_private(self):
        note_2.is_private = False
        self.student_page.create_note(note_2, topics, [])
        assert not boa_utils.is_note_private(note_2)

    def test_note_batch_can_be_private(self):
        students = test.students[0:2]
        self.homepage.create_note_batch(batch_1, students, cohorts=[], groups=[], topics=[], attachments=[])
        for stud in students:
            note_id = self.student_page.set_new_note_id(batch_1, stud)
            note = Note({'record_id': note_id})
            assert boa_utils.is_note_private(note)

    def test_note_batch_can_be_non_private(self):
        students = test.students[3:5]
        self.homepage.create_note_batch(batch_2, students, cohorts=[], groups=[], topics=[], attachments=[])
        for stud in students:
            note_id = self.student_page.set_new_note_id(batch_2, stud)
            note = Note({'record_id': note_id})
            assert not boa_utils.is_note_private(note)

    def test_note_template_can_be_private(self):
        note = Note({
            'advisor': test_ce3.advisor,
            'is_private': True,
            'subject': f'CE3 template subject {test.test_id}',
        })
        self.student_page.load_page(test.students[0])
        self.student_page.click_create_new_note()
        self.student_page.enter_new_note_subject(note)
        self.student_page.set_note_privacy(note)
        self.student_page.create_template(ce3_template, note)

    def test_note_from_private_template_can_be_private(self):
        note = Note({})
        self.student_page.load_page(test.students[0])
        self.student_page.click_create_new_note()
        self.student_page.select_and_apply_template(ce3_template, note)
        note.subject = f'{note.subject} {int(time.time())}'
        self.student_page.enter_new_note_subject(note)
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(note, test.students[0])
        assert boa_utils.is_note_private(note)

    def test_note_from_private_template_can_be_non_private(self):
        note = Note({})
        self.student_page.load_page(test.students[0])
        self.student_page.click_create_new_note()
        self.student_page.select_and_apply_template(ce3_template, note)
        note.subject = f'{note.subject} {int(time.time())}'
        note.is_private = False
        self.student_page.enter_new_note_subject(note)
        self.student_page.set_note_privacy(note)
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(note, test.students[0])
        assert not boa_utils.is_note_private(note)

    def test_note_template_can_be_changed_to_non_private(self):
        self.student_page.load_page(test.students[2])
        self.student_page.click_create_new_note()
        self.student_page.click_edit_template(ce3_template)
        ce3_template.is_private = False
        self.student_page.set_note_privacy(ce3_template)
        self.student_page.click_update_template()

    def test_note_from_non_private_template_can_be_private(self):
        note = Note({})
        self.student_page.click_create_new_note()
        self.student_page.select_and_apply_template(ce3_template, note)
        note.subject = f'{note.subject} {int(time.time())}'
        note.is_private = True
        self.student_page.enter_new_note_subject(note)
        self.student_page.set_note_privacy(note)
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(note, test.students[2])
        assert boa_utils.is_note_private(note)

    def test_note_from_non_private_template_can_be_non_private(self):
        note = Note({})
        self.student_page.load_page(test.students[3])
        self.student_page.click_create_new_note()
        self.student_page.select_and_apply_template(ce3_template, note)
        note.subject = f'{note.subject} {int(time.time())}'
        self.student_page.enter_new_note_subject(note)
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(note, test.students[3])
        assert not boa_utils.is_note_private(note)


@pytest.mark.usefixtures('page_objects')
class TestNoteCreatedByNonCE3Advisor:

    def test_note_is_not_private(self):
        self.homepage.log_out()
        self.homepage.dev_auth(test_ls.advisor)
        self.student_page.load_page(test.students[4])
        self.student_page.create_note(note_3, topics, attachments=[])
        assert not boa_utils.is_note_private(note_3)

    def test_note_from_template_is_not_private(self):
        non_ce3_template = NoteTemplate({'title': f'Non-CE3 template {test.test_id}'})
        non_ce3_note = Note({
            'advisor': test_ls.advisor,
            'subject': f'Non-CE3 template subject {test.test_id}',
        })
        self.student_page.load_page(test.students[5])
        self.student_page.click_create_new_note()
        self.student_page.enter_new_note_subject(non_ce3_note)
        self.student_page.create_template(non_ce3_template, non_ce3_note)
        self.student_page.click_create_new_note()
        self.student_page.select_and_apply_template(non_ce3_template, non_ce3_note)
        self.student_page.when_present(self.student_page.NEW_NOTE_SAVE_BUTTON, 2)
        assert not self.student_page.is_present(self.student_page.PRIVATE_RADIO)
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(non_ce3_note, test.students[5])
        assert not boa_utils.is_note_private(non_ce3_note)


@pytest.mark.usefixtures('page_objects')
class TestPrivateBoaNote:

    def test_ce3_advisor_sees_private_data(self):
        self.homepage.log_out()
        self.homepage.dev_auth(test_ce3.advisor)
        self.student_page.load_page(student)
        self.student_page.verify_note(note_1, test_ce3.advisor)

    def test_ce3_advisor_can_download_attachments(self):
        for attach in note_1.attachments:
            self.student_page.download_attachment(note_1, attach)

    def test_non_ce3_advisor_sees_no_private_data(self):
        self.homepage.log_out()
        self.homepage.dev_auth(test_ls.advisor)
        self.student_page.load_page(student)
        self.student_page.verify_note(note_1, test_ls.advisor)

    def test_blocks_body_and_attachments_access_via_api_for_non_ce3_advisor(self):
        notes = self.api_student_page.student_notes(student)
        note = next(filter(lambda n: str(n['id']) == str(note_1.record_id), notes))
        assert not note['body']
        assert not note['attachments']

    def test_blocks_note_attachment_download_via_api_for_non_ce3_advisor(self):
        utils.prepare_download_dir()
        self.api_notes_page.load_attachment_page(note_1.attachments[0].file_name)
        self.api_notes_page.when_present(self.api_notes_page.ATTACH_NOT_FOUND_MSG, utils.get_short_timeout())
        assert utils.is_download_dir_empty()

    def test_cannot_be_searched_by_subject(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth()
        self.api_admin_page.reindex_notes()
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(test_ce3.advisor)
        self.homepage.enter_simple_search_and_hit_enter(note_1.subject)
        self.search_results_page.assert_note_result_not_present(note_1)

    def test_cannot_be_searched_by_body(self):
        self.homepage.enter_simple_search_and_hit_enter(note_1.body)
        self.search_results_page.assert_note_result_not_present(note_1)

    def test_cannot_be_searched_by_date(self):
        self.homepage.open_adv_search()
        self.homepage.set_notes_student(student)
        self.homepage.set_notes_date_from(datetime.today())
        self.homepage.click_adv_search_button()
        self.search_results_page.assert_note_result_not_present(note_1)

    def test_excludes_note_body_from_note_exports(self):
        self.homepage.log_out()
        self.homepage.dev_auth()
        test_ls.advisor.dept_memberships = [
            DepartmentMembership(advisor_role=AdvisorRole.DIRECTOR,
                                 dept=Department.L_AND_S,
                                 is_automated=True),
        ]
        self.pax_manifest_page.load_page()
        self.pax_manifest_page.search_for_advisor(test_ls.advisor)
        self.pax_manifest_page.edit_user(test_ls.advisor)
        self.homepage.log_out()

        self.homepage.dev_auth(test_ls.advisor)
        self.student_page.load_page(student)
        self.student_page.show_notes()
        self.student_page.download_notes(student)
        self.student_page.verify_note_in_export_csv(student, note_1, test_ls.advisor)

    def test_excludes_note_attachment_files(self):
        private_file_names = [a.file_name for a in note_1.attachments]
        downloaded_file_names = self.student_page.note_export_file_names(student)
        for name in private_file_names:
            assert name not in downloaded_file_names

    def test_can_be_edited_to_set_privacy(self):
        self.homepage.log_out()
        self.homepage.dev_auth(test_ce3.advisor)
        self.student_page.load_page(student)
        note_2.is_private = True
        self.student_page.expand_item(note_2)
        self.student_page.click_edit_note_button(note_2)
        self.student_page.set_note_privacy(note_2)
        self.student_page.save_note_edit(note_2)
        assert boa_utils.is_note_private(note_2)

    def test_can_be_edited_to_set_non_privacy(self):
        note_1.is_private = False
        self.student_page.expand_item(note_1)
        self.student_page.click_edit_note_button(note_1)
        self.student_page.set_note_privacy(note_1)
        self.student_page.save_note_edit(note_1)
        assert not boa_utils.is_note_private(note_1)

    def test_cannot_edit_own_private_note_when_lose_access_to_private_notes(self):
        self.homepage.log_out()
        self.homepage.dev_auth()
        test_ce3.advisor.dept_memberships = [
            DepartmentMembership(advisor_role=AdvisorRole.ADVISOR, dept=Department.L_AND_S, is_automated=True),
        ]
        self.pax_manifest_page.load_page()
        self.pax_manifest_page.search_for_advisor(test_ce3.advisor)
        self.pax_manifest_page.edit_user(test_ce3.advisor)
        self.pax_manifest_page.log_out()

        self.homepage.dev_auth(test_ce3.advisor)
        self.student_page.load_page(student)
        self.student_page.show_notes()
        self.student_page.expand_item(note_2)
        assert not self.student_page.is_present(self.student_page.edit_note_button_loc(note_2))

    def test_tear_down(self):
        self.homepage.log_out()
        self.homepage.dev_auth()
        test_ce3.advisor.dept_memberships = [
            DepartmentMembership(advisor_role=AdvisorRole.ADVISOR, dept=Department.ZCEEE, is_automated=True),
        ]
        self.pax_manifest_page.load_page()
        self.pax_manifest_page.search_for_advisor(test_ce3.advisor)
        self.pax_manifest_page.edit_user(test_ce3.advisor)
