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
from copy import deepcopy
from datetime import datetime

from bea.config.bea_test_config import BEATestConfig
from bea.models.advisor_role import AdvisorRole
from bea.models.department import Department
from bea.models.department_membership import DepartmentMembership
from bea.models.notes_and_appts.note_template import NoteTemplate
from bea.models.notes_and_appts.topic import PeerTopics, Topic
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest

test_ls = BEATestConfig()
test_ls.peer_advising_mgmt(dept=Department.L_AND_S)
pam_ls = test_ls.advisor
peer_dept_ls = test_ls.get_peer_dept(pam_ls)
peer_dept_ls_id = boa_utils.get_peer_dept_id(peer_dept_ls)
peer_ls = test_ls.get_peer_advisor(test_ls.test_students[0])
pre_existing_peers_ls = boa_utils.get_peer_advisors(peer_dept_ls)
pre_existing_templates_ls = boa_utils.get_peer_note_templates(peer_dept_ls)

test_coe = BEATestConfig()
test_coe.peer_advising_mgmt(dept=Department.COE)
pam_coe = test_coe.advisor
peer_dept_coe = test_coe.get_peer_dept(pam_coe)
peer_dept_coe_id = boa_utils.get_peer_dept_id(peer_dept_coe)


@pytest.mark.usefixtures('page_objects')
class TestPAMMgmt:

    def test_admin_grant_pam_role_coe(self):
        self.homepage.load_page()
        self.homepage.dev_auth()
        self.pax_manifest_page.load_page_and_find_user(pam_coe)
        self.pax_manifest_page.edit_user(pam_coe)

    # TODO test_admin_grant_pa_role_coe

    def test_admin_grant_pam_role_ls(self):
        self.pax_manifest_page.search_for_advisor(pam_ls)
        self.pax_manifest_page.wait_for_advisor_list()
        self.pax_manifest_page.edit_user(pam_ls)


@pytest.mark.usefixtures('page_objects')
class TestPAMAccountMgmt:

    def test_pam_view_existing_active_peer_advisors(self):
        self.homepage.switch_user(pam_ls)
        self.homepage.click_pam_link()
        expected = [u.uid for u in pre_existing_peers_ls if u.is_active]
        expected.sort()
        visible = self.pam_page.visible_peer_advisor_uids()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_pam_view_existing_deleted_peer_advisors(self):
        self.pam_page.show_deleted_peers()
        expected = [u.uid for u in pre_existing_peers_ls]
        expected.sort()
        visible = self.pam_page.visible_peer_advisor_uids()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_pam_search_peer_by_name(self):
        self.pam_page.hide_deleted_peers()
        self.pam_page.search_student_by_name(peer_ls)
        self.pam_page.when_visible(self.pam_page.peer_auto_suggest_option(peer_ls), utils.get_short_timeout())

    def test_pam_search_peer_by_uid(self):
        self.pam_page.search_student_by_sid(peer_ls)
        self.pam_page.when_visible(self.pam_page.peer_auto_suggest_option(peer_ls), utils.get_short_timeout())

    def test_pam_create_peer_advisor(self):
        self.pam_page.add_peer(peer_ls)

    def test_pam_peer_name(self):
        visible = self.pam_page.peer_advisor_name(peer_ls)
        utils.assert_actual_includes_expected(visible, peer_ls.first_name)
        utils.assert_actual_includes_expected(visible, peer_ls.last_name)

    def test_pam_peer_note_count(self):
        utils.assert_equivalence(self.pam_page.peer_advisor_note_count(peer_ls), '0')

    def test_pam_peer_date(self):
        utils.assert_equivalence(self.pam_page.peer_advisor_date(peer_ls), datetime.today().strftime('%b %-d, %Y'))


@pytest.mark.usefixtures('page_objects')
class TestPeerAdvisingTemplateMgmt:

    peer_templates = boa_utils.get_peer_note_templates(peer_dept_ls)
    app.logger.info(f'Peer dept {peer_dept_ls_id} template ids are {list(map(lambda t: t.record_id, peer_templates))}')
    template_1 = NoteTemplate({
        'body': (f'Note 1 body {test_ls.test_id} ' * 10).strip(),
        'is_peer_advising': True,
        'title': f'Template #1 {test_ls.test_id}',
        'topics': [],
    })
    template_2 = NoteTemplate({
        'body': f'Note 2 body {test_ls.test_id}',
        'is_peer_advising': True,
        'title': f'Template #2 {test_ls.test_id}',
        'topics': [Topic(PeerTopics.ACAD_DIFFICULTY_PROBATION.value), Topic(PeerTopics.DEGREE_CHECK.value)],
    })
    template_3 = deepcopy(template_1)

    def test_delete_existing_templates(self):
        self.pam_page.click_note_templates_tab()
        if self.peer_templates:
            for template in self.peer_templates:
                self.pam_page.delete_peer_template(template)
        else:
            app.logger.info(f'Peer dept {peer_dept_ls} has no existing templates to delete')

    def test_no_templates(self):
        assert self.pam_page.is_present(self.pam_page.NO_PEER_TEMPLATES_MSG)

    def test_create_template_but_cancel(self):
        self.pam_page.click_create_peer_template()
        self.pam_page.click_cancel_peer_template()

    def test_create_template_1(self):
        self.pam_page.create_peer_template(self.template_1)

    def test_template_name_required(self):
        self.pam_page.click_create_peer_template()
        self.pam_page.enter_note_body(self.template_2)
        self.pam_page.add_peer_template_topics(self.template_2)
        assert not self.pam_page.is_save_peer_template_enabled()

    def test_template_no_dupe_name_allowed(self):
        self.pam_page.enter_peer_template_name(self.template_1.title)
        self.pam_page.click_save_peer_template()
        self.pam_page.when_visible(self.pam_page.PEER_TEMPLATE_DUPE_NAME_MSG, 2)

    def test_template_name_max_chars(self):
        too_long = self.template_2.title * 15
        self.pam_page.enter_peer_template_name(too_long)
        assert self.pam_page.el_value(self.pam_page.PEER_TEMPLATE_NAME_INPUT) == too_long[0:255]

    def test_template_body_required(self):
        self.pam_page.click_cancel_peer_template()
        self.pam_page.click_create_peer_template()
        self.pam_page.enter_peer_template_name(self.template_2.title)
        self.pam_page.add_peer_template_topics(self.template_2)
        assert not self.pam_page.is_save_peer_template_enabled()

    def test_template_topics_not_required(self):
        self.pam_page.click_cancel_peer_template()
        self.pam_page.click_create_peer_template()
        self.pam_page.enter_peer_template_name(self.template_2.title)
        self.pam_page.enter_note_body(self.template_2)
        assert self.pam_page.is_save_peer_template_enabled()

    def test_create_template_2(self):
        self.pam_page.create_peer_template(self.template_2)

    def test_list_view_template_ids(self):
        visible = self.pam_page.visible_peer_template_ids()
        expected = [t.record_id for t in [self.template_1, self.template_2]]
        utils.assert_equivalence(visible, expected)

    def test_list_view_template_name(self):
        utils.assert_equivalence(self.pam_page.peer_template_name(self.template_2), self.template_2.title)

    def test_list_view_template_date(self):
        utils.assert_equivalence(self.pam_page.peer_template_date(self.template_2), datetime.today().strftime('%b %-d, %Y'))

    def test_edit_template_but_cancel(self):
        self.pam_page.click_edit_peer_template(self.template_1)
        self.pam_page.click_cancel_peer_template()

    def test_edit_template_name_required(self):
        self.pam_page.click_edit_peer_template(self.template_1)
        self.pam_page.enter_peer_template_name('')
        assert not self.pam_page.is_save_peer_template_enabled()

    def test_edit_template_no_dupe_name_allowed(self):
        self.pam_page.enter_peer_template_name(self.template_2.title)
        self.pam_page.click_save_peer_template()
        self.pam_page.when_visible(self.pam_page.PEER_TEMPLATE_DUPE_NAME_MSG, 2)

    def test_edit_template_name_max_chars(self):
        too_long = self.template_1.title * 15
        self.pam_page.enter_peer_template_name(too_long)
        assert self.pam_page.el_value(self.pam_page.PEER_TEMPLATE_NAME_INPUT) == too_long[0:255]

    def test_edit_template_body_required(self):
        self.pam_page.click_cancel_peer_template()
        self.pam_page.click_edit_peer_template(self.template_1)
        self.pam_page.remove_chars(self.pam_page.NOTE_BODY_TEXT_AREA)
        assert not self.pam_page.is_save_peer_template_enabled()

    def test_edit_peer_template(self):
        self.template_1.title = f'{self.template_1.title} EDITED'
        self.template_1.body = f'EDITED - {self.template_1.body}'
        self.template_1.topics = [Topic(PeerTopics.WITHDRAW_READMIT.value)]
        self.pam_page.click_cancel_peer_template()
        self.pam_page.edit_peer_template(self.template_1)

    def test_copy_peer_template_but_cxl(self):
        self.pam_page.click_copy_peer_template(self.template_2)
        self.pam_page.click_cancel_peer_template()
        self.pam_page.when_not_present(self.pam_page.PEER_TEMPLATE_NAME_INPUT, 2)

    def test_copy_peer_template(self):
        self.pam_page.click_copy_peer_template(self.template_1)
        self.template_3.title = f'COPIED - Template #3 {test_ls.test_id}'
        self.pam_page.enter_peer_template_name(self.template_3.title)
        self.pam_page.click_save_peer_template()
        self.pam_page.set_new_template_id(self.template_3)
        self.pam_page.when_present(self.pam_page.peer_template_row(self.template_3), 2)

    def test_delete_template_but_cancel(self):
        self.pam_page.click_delete_peer_template(self.template_1)
        self.pam_page.cancel_delete_or_discard()

    def test_delete_template(self):
        self.pam_page.click_delete_peer_template(self.template_1)
        self.pam_page.confirm_delete_or_discard()
        self.pam_page.when_not_present(self.pam_page.peer_template_row(self.template_1), utils.get_short_timeout())
        visible = self.pam_page.visible_peer_template_ids()
        expected = [t.record_id for t in [self.template_3, self.template_2]]
        utils.assert_equivalence(visible, expected)


@pytest.mark.usefixtures('page_objects')
class TestPeerAdvisorMgmt:

    def test_pam_delete_peer_but_cxl(self):
        self.pam_page.click_acct_mgmt_tab()
        self.pam_page.click_delete_peer(peer_ls)
        self.pam_page.cancel_delete_or_discard()

    def test_pam_delete_peer(self):
        self.pam_page.click_delete_peer(peer_ls)
        self.pam_page.confirm_delete_or_discard()
        self.pam_page.when_not_present(self.pam_page.peer_advisor_row(peer_ls), utils.get_short_timeout())

    def test_deleted_peer(self):
        self.pam_page.log_out()
        self.homepage.enter_dev_auth_creds(peer_ls)
        self.homepage.when_present(self.homepage.AXIOS_ERROR_MSG, utils.get_short_timeout())

    def test_pam_restore_peer(self):
        self.homepage.load_page()
        self.homepage.dev_auth(pam_ls)
        self.homepage.click_pam_link()
        self.pam_page.show_deleted_peers()
        self.pam_page.restore_peer(peer_ls)
        self.pam_page.hide_deleted_peers()
        assert self.pam_page.is_present(self.pam_page.peer_advisor_row(peer_ls))

    def test_restored_peer(self):
        self.pam_page.log_out()
        self.homepage.dev_auth(peer_ls, 'Peer Advising')
        self.peer_page.when_present(self.peer_page.PEER_NEW_NOTE_BTN, utils.get_short_timeout())


@pytest.mark.usefixtures('page_objects')
class TestPeerAdvisingPerms:

    def test_no_pams_for_peers(self):
        self.pam_page.hit_peer_advisor_manager_page_url(peer_dept_ls_id)
        self.peer_page.wait_for_404()
        assert not self.peer_page.is_present(self.peer_page.PAM_LINK)

    def test_no_foreign_depts_for_pams(self):
        self.homepage.switch_user(pam_coe)
        self.pam_page.hit_peer_advisor_manager_page_url(peer_dept_ls_id)
        self.pam_page.wait_for_404()

    def test_admin_revoke_pam_role(self):
        pam_ls.dept_memberships = [DepartmentMembership(advisor_role=AdvisorRole.ADVISOR,
                                                        dept=test_ls.dept,
                                                        is_automated=None,
                                                        peer_advising_dept=None,
                                                        peer_advising_role=None)]
        self.homepage.switch_user()
        self.pax_manifest_page.load_page_and_find_user(pam_ls)
        self.pax_manifest_page.edit_user(pam_ls)

    def test_no_pams_for_non_pams(self):
        self.pax_manifest_page.click_become_user_link(pam_ls)
        self.homepage.wait_for_boa_title('Home')
        self.pam_page.hit_peer_advisor_manager_page_url(peer_dept_ls_id)
        self.homepage.wait_for_404()

    def test_pams_for_admins(self):
        self.homepage.switch_user()
        self.pam_page.load_peer_advisor_manager_page(peer_dept_ls_id)


class TestTeardown:

    def test_remove_peer(self):
        boa_utils.hard_delete_user(peer_ls)
