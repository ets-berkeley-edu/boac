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

from bea.config.bea_test_config import BEATestConfig
from bea.models.advisor_role import AdvisorRole
from bea.models.department import Department
from bea.models.department_membership import DepartmentMembership
from bea.models.user import User
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest


test = BEATestConfig()
test.user_mgmt()
auth_users = boa_utils.get_authorized_users()
test_auth_user = next(filter(lambda a: a.uid != test.admin.uid and len(a.uid) == 7, auth_users))
test_student = test.students[-1]

# Initialize a user for the add/edit user tests
add_edit_user = User({
    'uid': app.config['TEST_USER_UID'],
    'active': True,
    'can_access_advising_data': True,
    'can_access_canvas_data': True,
    'dept_memberships': [
        DepartmentMembership(dept=Department.L_AND_S, advisor_role=AdvisorRole.ADVISOR, is_automated=True),
    ],
})

# Hard delete the add/edit user in case it's still lying around from a previous test run
boa_utils.hard_delete_user(add_edit_user)
for u in auth_users:
    if u.uid == add_edit_user.uid:
        auth_users.remove(u)

non_admin_depts = [d for d in Department if d not in [Department.ADMIN, Department.NOTES_ONLY]]
dept_advisors = list(map(lambda d: {'dept': d, 'advisors': boa_utils.get_dept_advisors(d)}, non_admin_depts))
for da in dept_advisors:
    if not da['advisors']:
        dept_advisors.remove(da)


@pytest.mark.usefixtures('page_objects')
class TestAuthUserSearch:

    def test_defaults_to_search(self):
        self.homepage.load_page()
        self.homepage.dev_auth()
        self.homepage.click_pax_manifest_link()
        self.pax_manifest_page.when_present(self.pax_manifest_page.FILTER_MODE_SELECT, utils.get_medium_timeout())
        utils.assert_equivalence(self.pax_manifest_page.selected_option_text(self.pax_manifest_page.FILTER_MODE_SELECT),
                                 'Search')

    def test_search_by_uid(self):
        self.pax_manifest_page.search_for_advisor(test_auth_user)
        self.pax_manifest_page.wait_for_advisor_list()
        utils.assert_equivalence(self.pax_manifest_page.list_view_uids(), [test_auth_user.uid])

    def test_search_result_user_dept(self):
        if test_auth_user.uid in self.pax_manifest_page.list_view_uids():
            self.pax_manifest_page.expand_user_row(test_auth_user)
            visible_depts = self.pax_manifest_page.visible_advisor_depts(test_auth_user)
            visible_depts.sort()
            expected_depts = [d.value['name'] for d in test_auth_user.depts]
            expected_depts.sort()
            for memb in test_auth_user.dept_memberships:
                memb_dept = memb.dept.value['code']
                expected_roles = []
                if memb.advisor_role == AdvisorRole.ADVISOR:
                    expected_roles.append('advisor')
                if memb.advisor_role == AdvisorRole.DIRECTOR:
                    expected_roles.append('director')
                visible_user_details = self.pax_manifest_page.visible_user_details(test_auth_user)
                visible_dept = next(filter(lambda d: d['code'] == memb_dept, visible_user_details['departments']))
                visible_dept_roles = self.pax_manifest_page.visible_dept_roles(test_auth_user, memb.dept)
                visible_roles = visible_dept_roles.split(' and ')
                utils.assert_equivalence(visible_roles, expected_roles)
                utils.assert_equivalence(visible_dept['automateMembership'], memb.is_automated)

    def test_search_result_user_perms(self):
        if test_auth_user.uid in self.pax_manifest_page.list_view_uids():
            visible_user_details = self.pax_manifest_page.visible_user_details(test_auth_user)
            utils.assert_equivalence(visible_user_details['canAccessCanvasData'], test_auth_user.can_access_canvas_data)
            utils.assert_equivalence(visible_user_details['isAdmin'], test_auth_user.is_admin)

    def test_search_result_user_status(self):
        if test_auth_user.uid in self.pax_manifest_page.list_view_uids():
            visible_user_details = self.pax_manifest_page.visible_user_details(test_auth_user)
            visible_active_status = False if visible_user_details['deletedAt'] else True
            assert visible_active_status == test_auth_user.active
            utils.assert_equivalence(visible_user_details['isBlocked'], test_auth_user.is_blocked)

    def test_search_result_user_become_link(self):
        if test_auth_user.uid in self.pax_manifest_page.list_view_uids():
            become_link_present = self.pax_manifest_page.is_present(self.pax_manifest_page.become_user_loc(test_auth_user))
            if test_auth_user.active:
                assert become_link_present
            else:
                assert not become_link_present

    def test_filter_dept_options(self):
        self.pax_manifest_page.select_filter_mode()
        depts = ['All']
        depts.extend([a['dept'].value['name'] for a in dept_advisors])
        depts.sort()
        utils.assert_equivalence(self.pax_manifest_page.dept_filter_options(), depts)

    def test_filter_dept_results(self):
        dept = dept_advisors[0]['dept']
        advisors = dept_advisors[0]['advisors']
        expected = [a.uid for a in advisors]
        expected.sort()
        app.logger.info(f"Checking advisor list for {dept.value['name']}")
        self.pax_manifest_page.select_dept(dept)
        self.pax_manifest_page.wait_for_advisor_list()
        visible = self.pax_manifest_page.list_view_uids()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_filter_dept_results_include_names(self):
        self.pax_manifest_page.select_all_depts()
        self.pax_manifest_page.wait_for_advisor_list()
        visible = self.pax_manifest_page.els_text_if_exist(self.pax_manifest_page.ADVISOR_NAME)
        visible = [n for n in visible if n]
        assert visible

    def test_filter_dept_results_include_titles(self):
        visible = self.pax_manifest_page.els_text_if_exist(self.pax_manifest_page.ADVISOR_DEPT)
        visible = [t for t in visible if t]
        assert visible

    def test_filter_dept_results_include_emails(self):
        els = self.pax_manifest_page.elements(self.pax_manifest_page.ADVISOR_EMAIL)
        visible = [el.get_attribute('href') for el in els]
        visible = [e for e in visible if e]
        assert visible

    def test_admins_list(self):
        self.pax_manifest_page.select_admin_mode()
        expected = [a.uid for a in auth_users if a.is_admin]
        expected.sort()
        self.pax_manifest_page.wait_for_advisor_list()
        visible = self.pax_manifest_page.list_view_uids()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_user_export(self):
        download = self.pax_manifest_page.download_boa_users()
        uids = [row['uid'] for row in download]
        uids = list(set(uids))
        uids.sort()
        expected = [user.uid for user in auth_users if user.active]
        expected = list(set(expected))
        expected.sort()
        utils.assert_equivalence(uids, expected)


@pytest.mark.usefixtures('page_objects')
class TestUserAddEditDelete:

    def test_add_user_but_cancel(self):
        self.pax_manifest_page.load_page()
        self.pax_manifest_page.click_add_user()
        self.pax_manifest_page.click_cancel_button()

    def test_add_user(self):
        self.pax_manifest_page.add_user(add_edit_user)
        self.pax_manifest_page.search_for_advisor(add_edit_user)
        self.pax_manifest_page.wait_for_advisor_list()
        utils.assert_actual_includes_expected(self.pax_manifest_page.list_view_uids(), add_edit_user.uid)

    def test_no_dupe_users(self):
        self.pax_manifest_page.click_add_user()
        self.pax_manifest_page.enter_new_user_data(add_edit_user)
        self.pax_manifest_page.when_present(self.pax_manifest_page.dupe_user_loc(add_edit_user), utils.get_short_timeout())

    def test_edit_user_but_cancel(self):
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.click_edit_user(add_edit_user)
        self.pax_manifest_page.click_cancel_button()

    def test_block_user(self):
        add_edit_user.is_blocked = True
        self.pax_manifest_page.edit_user(add_edit_user)

    def test_unblock_user(self):
        add_edit_user.is_blocked = False
        self.pax_manifest_page.edit_user(add_edit_user)

    def test_automate_user(self):
        add_edit_user.dept_memberships[0].is_automated = True
        self.pax_manifest_page.edit_user(add_edit_user)

    def test_de_automate_user(self):
        add_edit_user.dept_memberships[0].is_automated = False
        self.pax_manifest_page.edit_user(add_edit_user)

    def test_convert_user_to_admin(self):
        add_edit_user.is_admin = True
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')
        self.pax_manifest_page.load_page()

    def test_convert_user_to_non_admin(self):
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        add_edit_user.is_admin = False
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')
        self.pax_manifest_page.hit_page_url()
        self.pax_manifest_page.wait_for_404()

    def test_remove_canvas_perms(self):
        add_edit_user.can_access_canvas_data = False
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')
        self.class_page.hit_class_page_url('2198', '21595')
        self.class_page.wait_for_403()

    def test_restore_canvas_perms(self):
        add_edit_user.can_access_canvas_data = True
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')
        self.class_page.load_page('2198', '21595')

    def test_remove_notes_perms(self):
        add_edit_user.can_access_advising_data = False
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')
        self.student_page.load_page(test_student)
        self.student_page.wait_for_timeline()
        assert not self.student_page.is_present(self.student_page.NEW_NOTE_BUTTON)
        assert not self.student_page.is_present(self.student_page.NOTES_BUTTON)
        assert not self.student_page.is_present(self.student_page.APPTS_BUTTON)

    def test_restore_notes_perms(self):
        add_edit_user.can_access_advising_data = True
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')
        self.student_page.load_page(test_student)
        self.student_page.wait_for_timeline()
        assert self.student_page.is_present(self.student_page.NEW_NOTE_BUTTON)
        assert self.student_page.is_present(self.student_page.NOTES_BUTTON)
        assert self.student_page.is_present(self.student_page.APPTS_BUTTON)

    def test_delete_user(self):
        add_edit_user.active = False
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.log_out()
        self.homepage.enter_dev_auth_creds(add_edit_user)
        self.homepage.when_present(self.homepage.AXIOS_ERROR_MSG, utils.get_short_timeout())

    def test_un_delete_user(self):
        add_edit_user.active = True
        self.homepage.dev_auth(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.log_out()
        self.homepage.dev_auth(add_edit_user)

    def test_add_dept_membership(self):
        membership = DepartmentMembership(dept=Department.ASC, advisor_role=AdvisorRole.ADVISOR, is_automated=False)
        add_edit_user.dept_memberships.append(membership)
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')
        self.homepage.click_sidebar_create_filtered()
        utils.assert_actual_includes_expected(self.filtered_students_page.filter_options(), 'Team (ASC)')

    def test_remove_dept_membership(self):
        membership = next(filter(lambda m: m.dept == Department.ASC, add_edit_user.dept_memberships))
        add_edit_user.dept_memberships.remove(membership)
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')
        self.homepage.click_sidebar_create_filtered()
        assert 'Team (ASC)' not in self.filtered_students_page.filter_options()

    def test_bestow_director_role(self):
        add_edit_user.dept_memberships[0].advisor_role = AdvisorRole.DIRECTOR
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')

    def test_bestow_advisor_role(self):
        add_edit_user.dept_memberships[0].advisor_role = AdvisorRole.ADVISOR
        self.homepage.switch_user(test.admin)
        self.pax_manifest_page.load_page_and_find_user(add_edit_user)
        self.pax_manifest_page.edit_user(add_edit_user)
        self.pax_manifest_page.click_become_user_link(add_edit_user)
        self.homepage.wait_for_boa_title('Home')

    def test_tear_down(self):
        boa_utils.hard_delete_user(add_edit_user)
