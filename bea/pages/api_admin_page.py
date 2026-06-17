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
import json
import time

from flask import current_app as app
from selenium.webdriver.common.by import By

from bea.pages.api_page import ApiPage
from bea.test_utils import boa_utils, utils


class ApiAdminPage(ApiPage):

    def load_cachejob(self):
        self.driver.get(f'{boa_utils.get_boa_base_url(api=True)}/api/admin/cachejob')
        self.when_present(self.CONTENT, utils.get_short_timeout())
        return json.loads(self.element(self.CONTENT).text)

    def reindex_notes(self):
        app.logger.info('Reindexing BOA notes')
        base_url = boa_utils.get_boa_base_url(api=True)
        self.driver.get(f'{base_url}/api/admin/reindex/notes')
        self.wait_for_element((By.XPATH, '//*[contains(text(), "started")]'), utils.get_short_timeout())
        assert self.is_present((By.XPATH, '//*[contains(text(), "true")]'))
        time.sleep(10)
        tries = 0
        max_tries = 60
        while tries <= max_tries:
            tries += 1
            try:
                app.logger.info('Checking reindexing status')
                time.sleep(5)
                self.driver.get(f'{base_url}/api/admin/status/reindex_notes')
                self.wait_for_element((By.XPATH, '//*[contains(text(), "isActive")]'), utils.get_short_timeout())
                assert self.is_present((By.XPATH, '//*[contains(text(), "false")]'))
                break
            except AssertionError:
                if tries == max_tries:
                    raise
                else:
                    time.sleep(1)
        time.sleep(1)
        app.logger.info('Just double checking reindexing status')
        self.driver.get(f'{base_url}/api/admin/status/reindex_notes')
        self.wait_for_element((By.XPATH, '//*[contains(text(), "isActive")]'), utils.get_short_timeout())
        assert self.is_present((By.XPATH, '//*[contains(text(), "false")]'))
