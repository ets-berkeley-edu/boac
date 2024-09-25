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

from bea.pages.page import Page
from flask import current_app as app
from selenium.webdriver.common.by import By


class CuratedModal(Page):

    GROUP_NAME_INPUT = By.ID, 'create-curated-group-input'
    GROUP_SAVE_BUTTON = By.ID, 'create-curated-group-confirm'
    GROUP_CANCEL_BUTTON = By.ID, 'create-curated-group-cancel'
    DUPE_GROUP_NAME_MSG = By.XPATH, '//div[contains(text(), "You have an existing curated group with this name")]'
    NO_CHARS_LEFT_MSG = By.XPATH, '//span[text()="(0 left)"]'

    def enter_group_name(self, group):
        app.logger.info(f'Entering group name {group.name}')
        self.wait_for_element_and_type(self.GROUP_NAME_INPUT, group.name)

    def name_and_save_group(self, group):
        self.enter_group_name(group)
        self.wait_for_element_and_click(self.GROUP_SAVE_BUTTON)

    def cancel_group(self):
        self.wait_for_element_and_click(self.GROUP_CANCEL_BUTTON)
        self.when_not_present(self.GROUP_CANCEL_BUTTON, 3)

    def cancel_group_if_modal(self):
        if self.is_present(self.GROUP_CANCEL_BUTTON):
            self.cancel_group()
