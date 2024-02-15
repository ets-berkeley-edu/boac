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

from bea.test_utils import utils
from flask import current_app as app
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Coptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as Foptions


class WebDriverManager(object):

    @classmethod
    def launch_browser(cls, browser=None, headless=None):
        _browser = browser or utils.get_browser()
        if headless:
            _headless = True if headless == 'true' else False
        else:
            _headless = utils.browser_is_headless()
        app.logger.warning(f'Launching {_browser.capitalize()}, headless is {_headless}')

        if _browser == 'firefox':
            p = FirefoxProfile()
            p.set_preference(key='devtools.jsonview.enabled', value=False)
            options = Foptions()
            options.profile = p
            options.headless = _headless
            driver = webdriver.Firefox(options=options)
        else:
            options = Coptions()
            options.binary_location = utils.get_browser_chrome_binary_path()
            if _headless:
                options.add_argument('--headless=new')
            prefs = {
                'profile.default_content_settings.popups': 0,
                'download.default_directory': utils.default_download_dir(),
                'directory_upgrade': True,
            }
            options.add_experimental_option('prefs', prefs)
            driver = webdriver.Chrome(options=options)
        driver.set_window_size(1600, 900) if app.config['BROWSER_HEADLESS'] else driver.maximize_window()
        return driver

    @classmethod
    def quit_browser(cls, driver):
        app.logger.warning(f'Quitting {utils.get_browser().capitalize()}')
        driver.quit()

    @classmethod
    def get_browser_logs(cls, driver):
        if driver.name == 'chrome':
            log = driver.get_log('browser')
            messages = list(map(lambda mess: mess['message'], log))
            for message in messages:
                app.logger.info(f'Possible JS error {message}')
            return messages
