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

import logging
import os

ADMIN_PASSWORD = 'secret'
ADMIN_UID = '123456'
ADMIN_USERNAME = 'secret'

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BASE_URL = 'https://boa-qa.berkeley.edu'

BROWSER = 'chrome'
BROWSER_BINARY_PATH = '/path/to/chrome'
BROWSER_HEADLESS = False

CLICK_SLEEP = 0.5

LOGGING_LOCATION = 'bea.log'
LOGGING_LEVEL = logging.INFO

TERM_CODE = '2024-B'
TERM_NAME = 'Spring 2024'
TERM_SIS_ID = '2242'
TERM_START_DATE = '2024-01-16'

TEST_DATA = f'{BASE_DIR}/bea/fixtures/bea-test-data.json'
TEST_DEFAULT_COHORT_MAJOR = 'History BA'

TESTING = True

TIMEOUT_SHORT = 20
TIMEOUT_MEDIUM = 120
TIMEOUT_LONG = 500
