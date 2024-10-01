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

from bea.config.bea_test_config import BEATestConfig
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.note_batch import NoteBatch
from bea.models.notes_and_appts.note_template import NoteTemplate
from bea.models.notes_and_appts.topic import Topic, Topics
from bea.test_utils import boa_utils
from flask import current_app as app
import pytest


@pytest.mark.usefixtures('page_objects')
class TestNoteTemplate:

    test = BEATestConfig()
    test.note_template()

    user_templates = boa_utils.get_user_note_templates(test.advisor)
    app.logger.info(f'UID {test.advisor.uid} template ids are {list(map(lambda t: t.record_id, user_templates))}')
    template_1 = NoteTemplate({'title': f'Template {test.test_id}'})
    template_2 = NoteTemplate({'title': f'Batch Template {test.test_id}'})
    attachments = list(filter(lambda a: a.file_size < 20000000, test.attachments))

    student = test.students[-1]
    batch_students = test.students[0:1]

    group_members = test.students[-50:]
    group = Cohort({'name': f'Group {test.test_id}'})

    note_create = Note({
        'subject': f'Note student-page-create {test.test_id}',
        'advisor': test.advisor,
    })
    note_edit = Note({
        'subject': f'Note student-page-edit {test.test_id}',
        'advisor': test.advisor,
    })
    note_batch_create = NoteBatch({
        'subject': f'Note batch-create {test.test_id}',
        'body': f'Body {test.test_id}',
        'advisor': test.advisor,
    })
    note_batch_edit = NoteBatch({
        'subject': f'Note batch-edit {test.test_id}',
        'advisor': test.advisor,
    })

    def test_delete_existing_templates(self):
        self.homepage.load_page()
        self.homepage.dev_auth(self.test.advisor)
        if self.user_templates:
            self.homepage.click_create_note_batch()
            for template in self.user_templates:
                self.homepage.delete_template(template)
        else:
            app.logger.info(f'UID {self.test.advisor.uid} has no existing templates to delete')

    def test_no_templates(self):
        self.student_page.load_page(self.student)
        self.student_page.click_create_new_note()
        self.student_page.click_templates_button()
        self.student_page.wait_for_no_templates_msg()

    # Student page template creation

    def test_cancel_template(self):
        self.student_page.enter_new_note_subject(self.note_create)
        self.student_page.click_save_as_template()
        self.student_page.click_cancel_template()

    def test_create_template(self):
        topics = [Topic(Topics.ACADEMIC_PROGRESS_RPT.value), Topic(Topics.DEGREE_CHECK.value)]
        self.student_page.enter_note_body(self.note_create)
        self.student_page.add_topics(self.note_create, topics)
        self.student_page.add_attachments_to_new_note(self.note_create, self.attachments[0:5])
        self.student_page.create_template(self.template_1, self.note_create)
        self.student_page.wait_for_new_note_modal_not_present()

    def test_new_template_added(self):
        self.student_page.click_create_new_note()
        self.student_page.click_templates_button()
        self.student_page.wait_for_template_option(self.template_1)

    def test_template_title_required(self):
        self.student_page.enter_new_note_subject(self.note_create)
        self.student_page.click_save_as_template()
        assert not self.student_page.is_create_template_enabled()

    def test_template_no_dupe_title_allowed(self):
        self.student_page.enter_template_title(self.template_1)
        self.student_page.click_create_template()
        self.student_page.wait_for_dupe_template_title_msg()

    def test_apply_template_to_new_note(self):
        self.student_page.click_cancel_template()
        self.student_page.select_and_apply_template(self.template_1, self.note_create)
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(self.note_create, self.student)
        self.student_page.verify_note(self.note_create, self.test.advisor)

    # Student page template edits

    def test_cancel_template_edit(self):
        self.student_page.load_page(self.student)
        self.student_page.click_create_new_note()
        self.student_page.click_edit_template(self.template_1)
        self.student_page.click_cancel_new_note()
        self.student_page.wait_for_template_edit_not_present()

    def test_edit_template(self):
        self.template_1.subject = f'Template {self.test.test_id} - edited'
        new_topics = [Topic(Topics.ACADEMIC_PROGRESS_RPT.value), Topic(Topics.EAP.value)]
        topics_to_remove = list(set(self.template_1.topics) - set(new_topics))
        topics_to_add = list(set(new_topics) - set(self.template_1.topics))
        # TODO - uncomment the following when attachments can be edited
        # attachments_to_remove = self.template_1.attachments
        # attachments_to_add = self.attachments[6:9]

        self.student_page.click_create_new_note()
        self.student_page.click_edit_template(self.template_1)
        self.student_page.enter_new_note_subject(self.template_1)
        self.student_page.enter_note_body(self.template_1)
        self.student_page.remove_topics(self.template_1, topics_to_remove)
        self.student_page.add_topics(self.template_1, topics_to_add)
        # TODO - uncomment the following when attachments can be edited
        # self.student_page.remove_attachments_from_new_note(self.template_1, attachments_to_remove)
        # self.student_page.add_attachments_to_new_note(self.template_1, attachments_to_add)
        self.student_page.click_update_template()
        self.student_page.wait_for_new_note_modal_not_present()

    def test_apply_edited_template(self):
        self.student_page.click_create_new_note()
        self.student_page.select_and_apply_template(self.template_1, self.note_edit)
        self.student_page.click_save_new_note()
        self.student_page.set_new_note_id(self.note_edit, self.student)
        self.student_page.verify_note(self.note_edit, self.test.advisor)

    def test_cancel_rename(self):
        self.student_page.click_create_new_note()
        self.student_page.click_rename_template(self.template_1)
        self.student_page.click_cancel_template_rename()

    def test_rename_template(self):
        self.template_1.title = f'S T {self.test.test_id}'
        self.student_page.rename_template(self.template_1)
        self.student_page.click_templates_button()
        self.student_page.wait_for_template_option(self.template_1)

    # Student page template deletion

    def test_cancel_deletion(self):
        self.student_page.click_templates_button()
        self.student_page.click_delete_template(self.template_1)
        self.student_page.cancel_delete_or_discard()

    def test_deletion(self):
        self.student_page.delete_template(self.template_1)
        self.student_page.click_templates_button()
        assert self.template_1.title not in self.student_page.template_options()

    # Batch note template creation

    def test_batch_cancel_template(self):
        self.homepage.load_page()

        # Create cohort to add
        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(self.test.default_cohort)
        self.filtered_students_page.create_new_cohort(self.test.default_cohort)

        # Create group to add
        self.homepage.click_sidebar_create_student_group()
        self.curated_students_page.create_group_with_bulk_sids(self.group, self.group_members)

        self.homepage.click_create_note_batch()
        self.homepage.enter_new_note_subject(self.note_batch_create)
        self.homepage.click_save_as_template()
        self.homepage.click_cancel_template()

    def test_batch_create_template(self):
        topics = [Topic(Topics.ACADEMIC_PROGRESS_RPT.value), Topic(Topics.DEGREE_CHECK.value)]
        self.homepage.enter_note_body(self.note_batch_create)
        self.homepage.add_topics(self.note_batch_create, topics)
        self.homepage.add_attachments_to_new_note(self.note_batch_create, self.attachments[0:5])
        self.homepage.create_template(self.template_2, self.note_batch_create)
        self.homepage.wait_for_new_note_modal_not_present()

    def test_batch_template_added(self):
        self.homepage.click_create_note_batch()
        self.homepage.click_templates_button()
        self.homepage.wait_for_template_option(self.template_2)

    def test_batch_template_title_required(self):
        self.homepage.enter_new_note_subject(self.note_batch_create)
        self.homepage.click_save_as_template()
        assert not self.homepage.is_create_template_enabled()

    def test_batch_template_no_dupe_title_allowed(self):
        self.homepage.enter_template_title(self.template_2)
        self.homepage.click_create_template()
        self.homepage.wait_for_dupe_template_title_msg()

    def test_batch_apply_template(self):
        self.homepage.click_cancel_template()
        # TODO - remove the following once the auto-suggest behaves itself
        self.homepage.add_space_sep_sids_to_batch(self.batch_students)
        for student in self.batch_students:
            self.homepage.append_student_to_batch(self.note_batch_create, student)
        # TODO - use the following once the auto-suggest behaves itself
        # self.homepage.add_students_to_batch(self.note_batch_create, self.batch_students)
        self.homepage.add_cohorts_to_batch(self.note_batch_create, [self.test.default_cohort])
        self.homepage.add_groups_to_batch(self.note_batch_create, [self.group])
        self.homepage.select_and_apply_template(self.template_2, self.note_batch_create)
        self.homepage.click_save_new_note()
        batch_student = self.batch_students[0]
        self.student_page.set_new_note_id(self.note_batch_create, batch_student)
        self.student_page.load_page(batch_student)
        self.student_page.verify_note(self.note_batch_create, self.test.advisor)

    # Batch note template edits

    def test_batch_cancel_template_edit(self):
        self.homepage.load_page()
        self.homepage.click_create_note_batch()
        self.homepage.click_edit_template(self.template_2)
        self.homepage.click_cancel_new_note()
        self.homepage.wait_for_template_edit_not_present()

    def test_batch_edit_template(self):
        self.template_2.subject = f'Template {self.test.test_id} - edited'
        new_topics = [Topic(Topics.ACADEMIC_PROGRESS_RPT.value), Topic(Topics.EAP.value)]
        topics_to_remove = list(set(self.template_2.topics) - set(new_topics))
        topics_to_add = list(set(new_topics) - set(self.template_2.topics))
        # TODO - uncomment the following when attachments can be edited
        # attachments_to_remove = self.template_2.attachments
        # attachments_to_add = self.attachments[6:9]

        self.homepage.click_create_note_batch()
        self.homepage.click_edit_template(self.template_2)
        self.homepage.enter_new_note_subject(self.template_2)
        self.homepage.enter_note_body(self.template_2)
        self.homepage.remove_topics(self.template_2, topics_to_remove)
        self.homepage.add_topics(self.template_2, topics_to_add)
        # TODO - uncomment the following when attachments can be edited
        # self.homepage.remove_attachments_from_new_note(self.template_2, attachments_to_remove)
        # self.homepage.add_attachments_to_new_note(self.template_2, attachments_to_add)
        self.homepage.click_update_template()
        self.homepage.wait_for_new_note_modal_not_present()

    def test_batch_apply_edited_template(self):
        self.homepage.click_create_note_batch()
        # TODO - remove the following once the auto-suggest behaves itself
        self.homepage.add_space_sep_sids_to_batch(self.batch_students)
        for student in self.batch_students:
            self.homepage.append_student_to_batch(self.note_batch_edit, student)
        # TODO - use the following once the auto-suggest behaves itself
        # self.homepage.add_students_to_batch(self.note_batch_edit, self.batch_students)
        self.homepage.add_cohorts_to_batch(self.note_batch_edit, [self.test.default_cohort])
        self.homepage.add_groups_to_batch(self.note_batch_edit, [self.group])
        self.homepage.select_and_apply_template(self.template_2, self.note_batch_edit)
        self.homepage.click_save_new_note()
        batch_student = self.batch_students[0]
        self.student_page.set_new_note_id(self.note_batch_edit, batch_student)
        self.student_page.load_page(batch_student)
        self.student_page.verify_note(self.note_batch_edit, self.test.advisor)

    def test_batch_cancel_rename(self):
        self.homepage.click_create_note_batch()
        self.homepage.click_rename_template(self.template_2)
        self.homepage.click_cancel_template_rename()

    def test_batch_rename_template(self):
        self.template_2.title = f'B T {self.test.test_id}'
        self.homepage.rename_template(self.template_2)
        self.homepage.click_templates_button()
        self.homepage.wait_for_template_option(self.template_2)

    # Batch note template deletion

    def test_batch_cancel_deletion(self):
        self.homepage.click_templates_button()
        self.homepage.click_delete_template(self.template_2)
        self.homepage.cancel_delete_or_discard()

    def test_batch_deletion(self):
        self.homepage.delete_template(self.template_2)
        self.homepage.click_templates_button()
        assert self.template_2.title not in self.homepage.template_options()
