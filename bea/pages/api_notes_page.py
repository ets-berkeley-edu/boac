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
import time

from bea.pages.page import Page
from bea.test_utils import boa_utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class ApiNotesPage(Page):

    NOT_FOUND_MSG = By.XPATH, '//*[contains(., "The requested resource could not be found.")]'
    ATTACH_NOT_FOUND_MSG = By.XPATH, '//*[text()="Sorry, attachment not available."]'
    NOTE_NOT_FOUND_MSG = By.XPATH, '//*[contains(., "Note not found")]'

    def load_attachment_page(self, attachment_file):
        app.logger.info(f'Hitting download endpoint for attachment at /api/notes/attachment/{attachment_file}')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/api/notes/attachment/{attachment_file}')
        time.sleep(2)

    def load_download_page(self, student):
        app.logger.info(f'Hitting download endpoint for student notes at /api/notes/download_for_sid/{student.sid}')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/api/notes/download_for_sid/{student.sid}')
