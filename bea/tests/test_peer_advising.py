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

from bea.config.bea_test_config import BEATestConfig
from bea.models.department import Department
from bea.models.notes_and_appts.note import Note
from bea.models.notes_and_appts.note_template import NoteTemplate
from bea.models.notes_and_appts.topic import PeerTopics, Topic
from bea.test_utils import boa_utils
from bea.test_utils import utils
import pytest

# Test users L&S
test_ls = BEATestConfig()
test_ls.peer_advising(dept=Department.L_AND_S)
pam_in_ls = test_ls.advisor
peer_dept_ls = test_ls.get_peer_dept(pam_in_ls)
peer_dept_ls_id = boa_utils.get_peer_dept_id(peer_dept_ls)
peer_1_in_ls = test_ls.get_peer_advisor(test_ls.test_students[0])
peer_2_in_ls = test_ls.get_peer_advisor(test_ls.test_students[1])

# Test users CoE
test_coe = BEATestConfig()
test_coe.peer_advising(dept=Department.COE)
pam_in_coe = test_coe.advisor
peer_dept_coe = test_coe.get_peer_dept(pam_in_coe)
peer_dept_coe_id = boa_utils.get_peer_dept_id(peer_dept_coe)
peer_in_coe = test_coe.get_peer_advisor(test_ls.test_students[3])

# Test notes
pre_existing_peer_note_ids = boa_utils.get_peer_dept_note_ids(peer_dept_ls_id)
note_1_by_ls_peer = Note({'advisor': peer_1_in_ls})
note_2_by_ls_peer = Note({'advisor': peer_1_in_ls})
student_1_for_ls_peer_note = test_ls.test_students[4]
student_2_for_ls_peer_note = test_ls.test_students[5]
student_schedule_tcs = [tc for tc in test_ls.test_cases if tc.course and tc.student == student_1_for_ls_peer_note]

test_ls.attachments.sort(key=lambda a: a.file_size, reverse=True)
too_big_attachments = list(filter(lambda a: a.file_size > 20000000, test_ls.attachments))
valid_attachments = list(filter(lambda a: a.file_size < 20000000, test_ls.attachments))

peer_template_in_ls = NoteTemplate({
    'body': (f'LS body {test_ls.test_id} ' * 10).strip(),
    'is_peer_advising': True,
    'title': f'LS Template {test_ls.test_id}',
    'topics': [Topic(PeerTopics.DEGREE_REQTS.value)],
})
peer_template_in_coe = NoteTemplate({
    'body': (f'CoE body {test_coe.test_id} ' * 10).strip(),
    'is_peer_advising': True,
    'title': f'CoE Template {test_coe.test_id}',
    'topics': [],
})


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_blow_away_residual_test_peers(self):
        existing_peers = boa_utils.get_peer_advisors()
        student_uids = [s.uid for s in test_ls.students]
        for peer in existing_peers:
            if peer.uid in student_uids:
                boa_utils.hard_delete_user(peer)

    def test_create_pams(self):
        self.homepage.load_page()
        self.homepage.dev_auth()
        self.pax_manifest_page.load_page_and_find_user(pam_in_ls)
        self.pax_manifest_page.edit_user(pam_in_ls)

        self.pax_manifest_page.search_for_advisor(pam_in_coe)
        self.pax_manifest_page.wait_for_advisor_list()
        self.pax_manifest_page.edit_user(pam_in_coe)

    def test_create_peers_and_templates(self):
        self.homepage.switch_user(pam_in_ls)
        self.homepage.click_pam_link()
        self.pam_page.add_peer(peer_1_in_ls)
        self.pam_page.add_peer(peer_2_in_ls)
        self.pam_page.click_note_templates_tab()
        self.pam_page.create_peer_template(peer_template_in_ls)

        self.homepage.switch_user(pam_in_coe)
        self.homepage.click_pam_link()
        self.pam_page.add_peer(peer_in_coe)
        self.pam_page.click_note_templates_tab()
        self.pam_page.create_peer_template(peer_template_in_coe)


@pytest.mark.usefixtures('page_objects')
class TestNoteStudentLookup:

    def test_peer_advisor_page(self):
        self.homepage.switch_user(peer_1_in_ls, 'Peer Advising')
        self.peer_page.when_visible(self.peer_page.PEER_NEW_NOTE_BTN, utils.get_short_timeout())

    def test_visible_peer_dept_notes(self):
        utils.assert_equivalence(self.peer_page.visible_peer_note_ids(), pre_existing_peer_note_ids)

    def test_search_student_by_name(self):
        self.peer_page.click_new_peer_note_button()
        self.peer_page.search_peer_note_student_by_name(student_2_for_ls_peer_note)

    def test_search_student_by_sid(self):
        self.peer_page.search_peer_note_student_by_sid(student_2_for_ls_peer_note)

    def test_search_student_by_email(self):
        self.peer_page.search_peer_note_student_by_email(student_2_for_ls_peer_note)

    def test_add_and_remove_student(self):
        self.peer_page.add_student_to_peer_note(student_2_for_ls_peer_note)
        self.peer_page.remove_student_from_peer_note(student_2_for_ls_peer_note)

    def test_show_student_schedule(self):
        self.peer_page.add_student_to_peer_note(student_1_for_ls_peer_note)
        self.peer_page.expand_student_schedule()


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=student_schedule_tcs,
                         ids=[tc.test_case_id for tc in student_schedule_tcs],
                         scope='class')
class TestExpandedStudentSchedule:

    def test_course_code(self, tc):
        term_name = tc.student.enrollment_data.term_name(tc.term)
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_code = tc.student.enrollment_data.course_code(tc.course)
        visible_course_code = self.peer_page.course_code(term_name, idx)
        utils.assert_equivalence(visible_course_code, course_code)

    def test_course_units(self, tc):
        term_name = tc.student.enrollment_data.term_name(tc.term)
        idx = tc.student.enrollment_data.course_idx(tc.term, tc.course)
        course_units = utils.formatted_units(tc.student.enrollment_data.course_units(tc.course))
        visible_course_units = self.peer_page.course_units(term_name, idx)
        utils.assert_equivalence(visible_course_units, course_units)


@pytest.mark.usefixtures('page_objects')
class TestNoteCreation:

    def test_hide_student_schedule(self):
        self.peer_page.collapse_student_schedule()

    def test_note_body_required(self):
        assert not self.peer_page.is_save_note_button_enabled()
        note_1_by_ls_peer.body = 'This is my body'
        self.peer_page.enter_note_body(note_1_by_ls_peer)
        assert self.peer_page.is_save_note_button_enabled()

    def test_note_add_attachments(self):
        self.peer_page.add_attachments_to_peer_note(note_1_by_ls_peer, valid_attachments[0:2])

    def test_note_remove_attachments(self):
        self.peer_page.remove_attachments_from_new_note(note_1_by_ls_peer, valid_attachments[0:2])

    def test_cancel_new_note(self):
        self.peer_page.click_cancel_new_note()
        self.peer_page.cancel_delete_or_discard()
        self.peer_page.click_cancel_new_note()
        self.peer_page.confirm_delete_or_discard()
        self.peer_page.when_not_present(self.peer_page.PEER_NOTE_STUDENT_INPUT, 2)

    def test_create_note_max_attachments(self):
        self.peer_page.click_new_peer_note_button()
        self.peer_page.enter_peer_note_attachments(test_ls.attachments)
        self.peer_page.when_visible(self.peer_page.NOTE_ATTACHMENT_COUNT_MSG, utils.get_short_timeout())

    def test_create_note_attachment_too_big(self):
        self.peer_page.click_cancel_new_note()
        self.peer_page.click_new_peer_note_button()
        self.peer_page.enter_peer_note_attachments([too_big_attachments[0]])
        self.peer_page.when_visible(self.peer_page.NOTE_ATTACHMENT_SIZE_MSG, utils.get_short_timeout())

    def test_create_note(self):
        note_1_by_ls_peer.body = (f'Test Note 1 {test_ls.test_id} ' * 20).strip()
        note_1_by_ls_peer.contact_type = 'Phone'
        note_1_by_ls_peer.student = student_1_for_ls_peer_note
        note_1_by_ls_peer.topics = [Topic(PeerTopics.LATE_CHANGE.value), Topic(PeerTopics.INCOMPLETES.value)]
        self.peer_page.click_cancel_new_note()
        self.peer_page.click_new_peer_note_button()
        self.peer_page.create_peer_note(note_1_by_ls_peer, valid_attachments[0:3])

    def test_note_template_options(self):
        self.peer_page.click_new_peer_note_button()
        self.peer_page.add_student_to_peer_note(student_1_for_ls_peer_note)
        self.peer_page.click_templates_button()
        visible_opts = self.peer_page.template_options()
        assert peer_template_in_ls.title in visible_opts
        assert peer_template_in_coe.title not in visible_opts

    def test_create_note_from_template(self):
        self.peer_page.click_templates_button()
        note_2_by_ls_peer.student = student_1_for_ls_peer_note
        self.peer_page.select_and_apply_template(peer_template_in_ls, note_2_by_ls_peer)
        self.peer_page.save_and_wait_for_peer_note(note_2_by_ls_peer)


@pytest.mark.usefixtures('page_objects')
class TestListView:

    def test_index_notes(self):
        self.peer_page.log_out()
        self.homepage.dev_auth()
        self.api_admin_page.reindex_notes()
        self.homepage.switch_user(peer_1_in_ls, 'Peer Advising')
        self.peer_page.wait_for_peer_note(note_1_by_ls_peer)

    def test_collapsed_note_student(self):
        utils.assert_equivalence(self.peer_page.peer_note_student(note_1_by_ls_peer), note_1_by_ls_peer.student.full_name)

    def test_collapsed_note_body(self):
        utils.assert_equivalence(self.peer_page.peer_note_body(note_1_by_ls_peer), note_1_by_ls_peer.body)

    def test_collapsed_note_topics(self):
        for topic in note_1_by_ls_peer.topics:
            utils.assert_actual_includes_expected(self.peer_page.peer_note_topics(note_1_by_ls_peer), topic.name)

    def test_collapsed_note_date(self):
        utils.assert_equivalence(self.peer_page.peer_note_date(note_1_by_ls_peer),
                                 self.peer_page.peer_note_date_format(note_1_by_ls_peer))

    def test_expand_note(self):
        self.peer_page.expand_peer_note(note_1_by_ls_peer)

    def test_expanded_note_author(self):
        visible = self.peer_page.expanded_note_advisor(note_1_by_ls_peer)
        utils.assert_actual_includes_expected(visible, peer_1_in_ls.first_name)
        utils.assert_actual_includes_expected(visible, peer_1_in_ls.last_name)

    def test_expanded_note_topics(self):
        expected = [t.name.upper() for t in note_1_by_ls_peer.topics]
        expected.sort()
        utils.assert_equivalence(self.peer_page.expanded_note_topics(note_1_by_ls_peer), expected)

    def test_expanded_note_contact_type(self):
        utils.assert_equivalence(self.peer_page.expanded_note_contact_type(note_1_by_ls_peer), note_1_by_ls_peer.contact_type)

    def test_expanded_note_attachments(self):
        attachment_files = [a.file_name for a in note_1_by_ls_peer.attachments]
        attachment_files.sort()
        visible_attachments = self.peer_page.expanded_note_attachments(note_1_by_ls_peer)
        visible_attachments.sort()
        utils.assert_equivalence(visible_attachments, attachment_files)

    def test_download_attachments(self):
        for attach in note_1_by_ls_peer.attachments:
            self.peer_page.download_attachment(note_1_by_ls_peer, attach)

    def test_collapse_note(self):
        self.peer_page.collapse_item(note_1_by_ls_peer)

    def test_search_note_student(self):
        self.peer_page.enter_simple_search_and_hit_enter(note_1_by_ls_peer.student.last_name)
        self.peer_page.wait_for_peer_note(note_1_by_ls_peer)
        self.peer_page.wait_for_peer_note(note_2_by_ls_peer)

    def test_search_note_student_no_result(self):
        string = note_1_by_ls_peer.student.full_name[::-1]
        self.peer_page.enter_simple_search_and_hit_enter(string)
        self.peer_page.when_visible(self.peer_page.PEER_NOTE_NO_RESULTS, utils.get_short_timeout())

    def test_search_note_body(self):
        self.peer_page.enter_simple_search_and_hit_enter(test_ls.test_id)
        self.peer_page.wait_for_peer_note(note_1_by_ls_peer)
        self.peer_page.wait_for_peer_note(note_2_by_ls_peer)

    def test_foreign_pa_cannot_see_note(self):
        self.peer_page.log_out()
        self.homepage.dev_auth(peer_in_coe, 'Peer Advising')
        self.peer_page.when_visible(self.peer_page.PEER_NEW_NOTE_BTN, utils.get_short_timeout())
        assert not self.peer_page.is_present(self.peer_page.peer_note_row(note_1_by_ls_peer))
        assert not self.peer_page.is_present(self.peer_page.peer_note_row(note_2_by_ls_peer))

    def test_foreign_pa_cannot_search_note(self):
        self.peer_page.enter_simple_search_and_hit_enter(test_ls.test_id)
        self.peer_page.when_visible(self.peer_page.PEER_NOTE_NO_RESULTS, utils.get_short_timeout())

    def test_domestic_pa_can_see_note(self):
        self.peer_page.log_out()
        self.homepage.dev_auth(peer_2_in_ls, 'Peer Advising')
        self.peer_page.when_visible(self.peer_page.PEER_NEW_NOTE_BTN, utils.get_short_timeout())
        self.peer_page.wait_for_peer_note(note_1_by_ls_peer)
        self.peer_page.wait_for_peer_note(note_2_by_ls_peer)

    def test_domestic_pa_can_search_note(self):
        self.peer_page.enter_simple_search_and_hit_enter(test_ls.test_id)
        self.peer_page.wait_for_peer_note(note_1_by_ls_peer)
        self.peer_page.wait_for_peer_note(note_2_by_ls_peer)


@pytest.mark.usefixtures('page_objects')
class TestPAMListView:

    def test_pam_dashboard_list_view(self):
        self.peer_page.log_out()
        self.homepage.dev_auth(pam_in_ls)
        self.homepage.click_pam_link()
        self.pam_page.click_peer_notes(peer_1_in_ls)

    def test_collapsed_note_student(self):
        assert self.pam_page.is_present(self.pam_page.peer_manager_note_student_link(note_1_by_ls_peer))
        assert self.pam_page.is_present(self.pam_page.peer_manager_note_student_link(note_2_by_ls_peer))

    def test_collapsed_note_body(self):
        utils.assert_equivalence(self.pam_page.peer_note_body(note_1_by_ls_peer), note_1_by_ls_peer.body)

    def test_collapsed_note_date(self):
        utils.assert_equivalence(self.pam_page.peer_manager_note_date(note_1_by_ls_peer),
                                 self.pam_page.peer_note_date_format(note_1_by_ls_peer))

    def test_expand_note(self):
        self.pam_page.expand_peer_note(note_1_by_ls_peer)

    def test_expanded_note_author(self):
        visible = self.pam_page.expanded_note_advisor(note_1_by_ls_peer)
        utils.assert_actual_includes_expected(visible, peer_1_in_ls.first_name)
        utils.assert_actual_includes_expected(visible, peer_1_in_ls.last_name)

    def test_expanded_note_topics(self):
        expected = [t.name.upper() for t in note_1_by_ls_peer.topics]
        expected.sort()
        utils.assert_equivalence(self.pam_page.expanded_note_topics(note_1_by_ls_peer), expected)

    def test_expanded_note_contact_type(self):
        utils.assert_equivalence(self.pam_page.expanded_note_contact_type(note_1_by_ls_peer),
                                 note_1_by_ls_peer.contact_type)

    def test_expanded_note_attachments(self):
        attachment_files = [a.file_name for a in note_1_by_ls_peer.attachments]
        attachment_files.sort()
        visible_attachments = self.peer_page.expanded_note_attachments(note_1_by_ls_peer)
        visible_attachments.sort()
        utils.assert_equivalence(visible_attachments, attachment_files)

    def test_collapse_note(self):
        self.pam_page.collapse_item(note_1_by_ls_peer)


@pytest.mark.usefixtures('page_objects')
class TestPAMNoteSearch:

    def test_search_note(self):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.exclude_students()
        self.homepage.exclude_classes()
        self.search_results_page.enter_adv_search_and_hit_enter(test_ls.test_id)
        self.search_results_page.assert_note_result_present(note_1_by_ls_peer)

    def test_search_note_dept(self):
        self.homepage.reopen_and_reset_adv_search()
        self.homepage.select_notes_posted_by_your_dept()
        self.search_results_page.enter_adv_search_and_hit_enter(test_ls.test_id)
        self.search_results_page.assert_note_result_present(note_1_by_ls_peer)


@pytest.mark.usefixtures('page_objects')
class TestPAMNoteEdit:

    def test_timeline_note(self):
        self.search_results_page.click_pam_link()
        self.pam_page.click_peer_notes(peer_1_in_ls)
        self.pam_page.click_peer_manager_note_student_link(note_1_by_ls_peer)
        self.student_page.show_notes()
        self.student_page.verify_note(note_1_by_ls_peer, pam_in_ls)

    def test_edit_note_body_required(self):
        old_body = note_1_by_ls_peer.body
        new_body = ''
        note_1_by_ls_peer.body = new_body
        self.student_page.click_edit_note_button(note_1_by_ls_peer)
        self.student_page.enter_note_body(note_1_by_ls_peer)
        note_1_by_ls_peer.body = old_body
        assert not self.student_page.element(self.student_page.EDIT_NOTE_SAVE_BUTTON).is_enabled()

    def test_edit_note_body(self):
        note_1_by_ls_peer.body = f'EDITED {note_1_by_ls_peer.body}'
        self.student_page.enter_note_body(note_1_by_ls_peer)

    def test_edit_note_contact_type(self):
        note_1_by_ls_peer.contact_type = 'Phone'
        self.student_page.select_contact_type(note_1_by_ls_peer)

    def test_edit_note_topics(self):
        topics_to_add = [Topic(PeerTopics.DBL_MAJOR.value), Topic(PeerTopics.REDUCED_LOAD.value)]
        self.student_page.remove_topics(note_1_by_ls_peer, note_1_by_ls_peer.topics)
        self.student_page.add_topics(note_1_by_ls_peer, topics_to_add)
        self.student_page.click_save_note_edit()
        self.student_page.when_not_present(self.student_page.EDIT_NOTE_SAVE_BUTTON, utils.get_short_timeout())

    def test_edit_note_attachments(self):
        attachments_to_add = valid_attachments[4:5]
        self.student_page.remove_attachments_from_existing_note(note_1_by_ls_peer, note_1_by_ls_peer.attachments)
        self.student_page.add_attachments_to_existing_note(note_1_by_ls_peer, attachments_to_add)

    def test_verify_edits(self):
        note_1_by_ls_peer.updated_date = datetime.now()
        self.student_page.click_close_msg(note_1_by_ls_peer)
        self.student_page.verify_note(note_1_by_ls_peer, pam_in_ls)

    def test_no_deleting(self):
        assert not self.student_page.is_present(self.student_page.delete_note_button_loc(note_1_by_ls_peer))

    def test_no_foreign_pam_edits(self):
        self.homepage.switch_user(pam_in_coe)
        self.student_page.load_page(student_1_for_ls_peer_note)
        self.student_page.expand_item(note_1_by_ls_peer)
        assert not self.student_page.is_present(self.student_page.edit_note_button_loc(note_1_by_ls_peer))

    def test_admin_deletion(self):
        self.homepage.switch_user()
        self.student_page.load_page(student_1_for_ls_peer_note)
        self.student_page.expand_item(note_1_by_ls_peer)
        self.student_page.delete_note(note_1_by_ls_peer)
        self.student_page.when_not_present(self.student_page.collapsed_item_loc(note_1_by_ls_peer), utils.get_short_timeout())

    def test_deleted_notes_removed_from_pam_dashboard(self):
        self.homepage.switch_user(pam_in_ls)
        self.homepage.click_pam_link()
        self.pam_page.click_peer_notes(peer_1_in_ls)
        assert not self.pam_page.is_present(self.pam_page.peer_note_row(note_1_by_ls_peer))
        assert self.pam_page.is_present(self.pam_page.peer_note_row(note_2_by_ls_peer))

    def test_deleted_notes_removed_from_peer_page(self):
        self.homepage.switch_user(peer_1_in_ls, 'Peer Advising')
        self.peer_page.when_visible(self.peer_page.PEER_NEW_NOTE_BTN, utils.get_short_timeout())
        assert not self.peer_page.is_present(self.peer_page.peer_note_row(note_1_by_ls_peer))
        assert self.peer_page.is_present(self.peer_page.peer_note_row(note_2_by_ls_peer))

    def test_blow_away_templates(self):
        self.homepage.switch_user(pam_in_ls)
        self.homepage.click_pam_link()
        self.pam_page.click_note_templates_tab()
        self.pam_page.delete_peer_template(peer_template_in_ls)

        self.homepage.switch_user(pam_in_coe)
        self.homepage.click_pam_link()
        self.pam_page.click_note_templates_tab()
        self.pam_page.delete_peer_template(peer_template_in_coe)

    def test_blow_away_test_peers(self):
        for peer in [peer_1_in_ls, peer_2_in_ls, peer_in_coe]:
            boa_utils.hard_delete_user(peer)
