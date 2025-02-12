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

from bea.pages.boa_pages import BoaPages
from bea.test_utils import boa_degree_progress_utils
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class DegreeCheckCreatePage(BoaPages):

    DEGREE_TEMPLATE_SELECT = By.ID, 'degree-template-select'
    SAVE_DEGREE_CHECK_BUTTON = By.ID, 'save-degree-check-btn'
    CANCEL_DEGREE_CHECK_BUTTON = By.ID, 'cancel-create-degree-check-btn'

    def load_page(self, student):
        app.logger.info(f'Loading degree checks page for UID {student.uid}')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/student/{student.uid}/degree/create')

    def select_template(self, template):
        self.wait_for_select_and_click_option(self.DEGREE_TEMPLATE_SELECT, template.name)

    def click_save_degree(self):
        self.wait_for_element_and_click(self.SAVE_DEGREE_CHECK_BUTTON)

    def click_cancel_degree(self):
        self.wait_for_element_and_click(self.CANCEL_DEGREE_CHECK_BUTTON)

    def create_new_degree_check(self, degree_check):
        app.logger.info(f'Creating a new degree check named {degree_check.name}')
        self.select_template(degree_check)
        self.click_save_degree()
        self.when_not_present(self.SAVE_DEGREE_CHECK_BUTTON, utils.get_short_timeout())
        self.wait_for_spinner()
        boa_degree_progress_utils.set_degree_check_ids(degree_check)
