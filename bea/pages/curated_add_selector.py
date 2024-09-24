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

from bea.pages.boa_pages import BoaPages
from bea.pages.curated_modal import CuratedModal
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CuratedAddSelector(BoaPages, CuratedModal):

    REMOVED_FROM_GROUP_MSG = By.XPATH, '//*[contains(text(), "Removed")]'

    # GROUPS

    SELECTOR_CREATE_GROUP_BUTTON = By.ID, 'create-curated-group'
    ADD_ALL_TO_GROUP_CBX = By.XPATH, '//input[@id="add-all-to-curated-group"]/..'
    ADD_TO_GROUP_BUTTON = By.ID, 'add-to-curated-group'
    ADD_INDIVIDUAL_TO_GROUP_CBX = By.XPATH, '//input[contains(@id, "curated-group-checkbox")]'

    SELECTOR_CREATE_CE3_GROUP_BUTTON = By.ID, 'create-admissions-group'
    ADD_ALL_TO_CE3_GROUP_CBX = By.XPATH, '//input[@id="add-all-to-admissions-group"]/..'
    ADD_TO_CE3_GROUP_BUTTON = By.ID, 'add-to-admissions-group'
    ADD_INDIVIDUAL_TO_CE3_GROUP_CBX = By.XPATH, '//input[contains(@id, "admissions-group-checkbox")]/..'

    @staticmethod
    def student_button_loc(student):
        return By.ID, f'student-{student.sid}-add-to-curated-group'

    @staticmethod
    def student_checkbox_loc(student):
        return By.XPATH, f'//input[@id="student-{student.sid}-curated-group-checkbox"]/..'

    @staticmethod
    def admit_checkbox_loc(admit):
        return By.XPATH, f'//input[@id="admit-{admit.sid}-admissions-group-checkbox"]/..'

    def click_add_to_group_from_list_view_header_button(self, group):
        self.scroll_to_top()
        if group.is_ce3:
            self.wait_for_element_and_click(self.ADD_TO_CE3_GROUP_BUTTON)
        else:
            self.wait_for_element_and_click(self.ADD_TO_GROUP_BUTTON)

    def click_add_to_group_per_student_button(self, student):
        self.scroll_to_top()
        self.wait_for_element_and_click(self.student_button_loc(student))

    @staticmethod
    def group_checkbox_link_loc(group):
        if group.is_ce3:
            return By.XPATH, f'//input[@id="admissions-group-{group.cohort_id}-checkbox"]'
        else:
            return By.XPATH, f'//input[@id="curated-group-{group.cohort_id}-checkbox"]'

    def is_group_selected(self, group):
        self.when_present(self.group_checkbox_link_loc(group), utils.get_short_timeout())
        return 'Remove' in self.element(self.group_checkbox_link_loc(group)).get_attribute('aria-label')

    def check_group(self, group):
        self.wait_for_page_and_click(self.group_checkbox_link_loc(group))

    def click_create_new_grp(self, group):
        if group.is_ce3:
            app.logger.info('Clicking group selector button to create a new CE3 group')
            self.when_present(self.SELECTOR_CREATE_CE3_GROUP_BUTTON, utils.get_short_timeout())
            self.click_element_js(self.SELECTOR_CREATE_CE3_GROUP_BUTTON)
        else:
            app.logger.info('Clicking group selector button to create a new group')
            self.when_present(self.SELECTOR_CREATE_GROUP_BUTTON, utils.get_short_timeout())
            self.click_element_js(self.SELECTOR_CREATE_GROUP_BUTTON)
        self.when_present(self.GROUP_NAME_INPUT, utils.get_short_timeout())

    def select_members_to_add(self, members, group):
        sids = list(map(lambda member: member.sid, members))
        app.logger.info(f'Selecting SIDs {sids}')
        for m in members:
            if group.is_ce3:
                self.wait_for_element_and_click(self.admit_checkbox_loc(m))
            else:
                self.wait_for_element_and_click(self.student_checkbox_loc(m))

    def add_members_to_grp(self, members, group):
        sids = list(map(lambda member: member.sid, members))
        app.logger.info(f'Adding SIDs {sids} to group {group.name} ID {group.cohort_id}')
        self.check_group(group)
        boa_utils.append_new_members_to_group(group, members)
        self.wait_for_sidebar_group(group)

    def remove_member_from_grp(self, member, group):
        app.logger.info(f'Removing SID {member.sid} from group {group.name} ID {group.cohort_id}')
        self.click_add_to_group_from_list_view_header_button(group)
        self.check_group(group)
        self.when_visible(self.REMOVED_FROM_GROUP_MSG, utils.get_short_timeout())
        group.memmbers.remove(member)
        self.wait_for_sidebar_group(group)

    def add_members_to_new_grp(self, members, group):
        sids = list(map(lambda member: member.sid, members))
        app.logger.info(f'Adding SIDs {sids} to new group {group.name}')
        self.click_create_new_grp(group)
        self.name_and_save_group(group)
        boa_utils.append_new_members_to_group(group, members)
        self.wait_for_sidebar_group(group)

    def select_and_add_members_to_grp(self, members, group):
        self.select_members_to_add(members, group)
        self.click_add_to_group_from_list_view_header_button(group)
        self.add_members_to_grp(members, group)

    def select_and_add_members_to_new_grp(self, members, group):
        self.select_members_to_add(members, group)
        self.click_add_to_group_from_list_view_header_button(group)
        self.add_members_to_new_grp(members, group)

    def select_and_add_all_visible_to_grp(self, all_students_or_admits, group):
        if group.is_ce3:
            Wait(self.driver, utils.get_short_timeout()).until(
                ec.presence_of_all_elements_located(self.ADD_INDIVIDUAL_TO_CE3_GROUP_CBX),
            )
            self.wait_for_element_and_click(self.ADD_ALL_TO_CE3_GROUP_CBX)
            cbx_els = self.elements(self.ADD_INDIVIDUAL_TO_CE3_GROUP_CBX)
        else:
            Wait(self.driver, utils.get_short_timeout()).until(
                ec.presence_of_all_elements_located(self.ADD_INDIVIDUAL_TO_GROUP_CBX),
            )
            self.wait_for_element_and_click(self.ADD_ALL_TO_GROUP_CBX)
            cbx_els = self.elements(self.ADD_INDIVIDUAL_TO_GROUP_CBX)
        app.logger.info(f'There are {len(cbx_els)} individual checkboxes')
        # Don't try to add users to the group if they're already in the group
        group_sids = list(map(lambda member: member.sid, group.members))
        visible_sids = list(map(lambda el: el.get_attribute('id').split('-')[1], cbx_els))
        sids_to_add = [sid for sid in visible_sids if sid not in group_sids]
        members_to_add = list(filter(lambda st: st.sid in sids_to_add, all_students_or_admits))
        self.click_add_to_group_from_list_view_header_button(group)
        self.add_members_to_grp(members_to_add, group)
