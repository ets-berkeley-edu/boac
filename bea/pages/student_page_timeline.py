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
from datetime import datetime
import os.path
import re
import time

from bea.pages.boa_pages import BoaPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class StudentPageTimeline(BoaPages):
    SORRY_NO_ATTACHMENT_MSG = By.XPATH, '//body[text()="Sorry, attachment not available."]'
    TOPIC = By.XPATH, '//li[contains(@id, "topic")]'

    @staticmethod
    def item_type(item):
        if item.__class__.__name__ in ['Note', 'NoteBatch']:
            return 'note'
        elif item.__class__.__name__ == 'TimelineEForm':
            return 'eForm'
        else:
            return 'appointment'

    @staticmethod
    def expected_item_short_date_format(item_time):
        return item_time.strftime('%b %-d') if datetime.now().strftime('%Y') == item_time.strftime(
            '%Y') else item_time.strftime('%b %-d, %Y')

    @staticmethod
    def expected_item_long_date_format(item_time):
        if datetime.now().strftime('%Y') == item_time.strftime('%Y'):
            formatted = item_time.strftime('%b %-d %l:%M%P')
        else:
            formatted = item_time.strftime('%b %-d, %Y %l:%M%P')
        return re.sub('\s+', ' ', formatted)

    def visible_collapsed_item_ids(self, item_type):
        els = self.elements((By.XPATH, f"//div[contains(@id, '{item_type}-') and contains(@id, '-is-closed')]"))
        ids = []
        for el in els:
            parts = el.get_attribute('id').split('-')
            if parts[2] == 'is':
                ids.append(parts[1])
            else:
                ids.append('-'.join(parts[1:-3]))
        return ids

    def collapsed_item_loc(self, item):
        item_type = self.item_type(item)
        if f'{self.driver.name}' == 'firefox':
            return By.XPATH, f'//tr[@id="permalink-{item_type}-{item.record_id}"]/td'
        else:
            return By.ID, f'permalink-{item_type}-{item.record_id}'

    def visible_message_ids(self):
        els = self.elements((By.XPATH, '//tr[contains(@class, "message-row")]'))
        ids = list(map(lambda el: el.attribute('id').split('-')[2: - 1].join('-'), els))
        app.logger.debug(f'Visible message IDs are {ids}')
        return ids

    def close_msg_button(self, item):
        return By.XPATH, f'//tr[@id="permalink-{self.item_type(item)}-{item.record_id}"]//button[contains(@id, "-close-message")]'

    def visible_collapsed_item_data(self, item):
        item_type = self.item_type(item)
        self.when_visible((By.XPATH, f'collapsed-{item_type}-{item.record_id}-created-at'), utils.get_short_timeout())
        subject_loc = By.ID, f'{item_type}-{item.record_id}-is-closed'
        subject = self.element(subject_loc).text.replace('\n', '') if self.is_present(subject_loc) else None
        date_loc = By.ID, f'collapsed-{item_type}-{item.record_id}-created-at'
        date = re.sub('/\s+/', ' ', self.element(date_loc).text) if self.is_present(date_loc) else None
        return {
            'subject': subject,
            'date': date,
        }

    def expanded_item_loc(self, item):
        return By.ID, f'{self.item_type(item)}-{item.record_id}-is-open'

    def is_item_expanded(self, item):
        self.is_present(self.expanded_item_loc(item)) and self.element(self.expanded_item_loc(item)).is_displayed()

    def expand_item(self, item):
        item_type = self.item_type(item)
        if self.is_item_expanded(item):
            app.logger.info(f'{item_type} ID {item.record_id} is already expanded')
        else:
            app.logger.info(f'Expanding {item_type} ID {item.record_id}')
            self.scroll_to_top()
            self.wait_for_element_and_click(self.collapsed_item_loc(item))

    def click_close_msg(self, item):
        self.wait_for_element_and_click(self.close_msg_button(item))

    def collapse_item(self, item):
        item_type = self.item_type(item)
        if self.is_item_expanded(item):
            app.logger.info(f'Collapsing {item_type} ID {item.record_id}')
            self.click_close_msg(item)
        else:
            app.logger.info(f'{item_type} ID {item.record_id} is already collapsed')

    def attachment_span_loc(self, item):
        item_type = self.item_type(item)
        return By.XPATH, f'//span[contains(@id, "{item_type}-{item.record_id}-attachment")]'

    def attachment_link_loc(self, item):
        item_type = self.item_type(item)
        return By.XPATH, f'//a[contains(@id, "{item_type}-{item.record_id}-attachment")]'

    def item_attachment_els(self, item_type, item):
        spans = self.elements(self.attachment_span_loc(item))
        links = self.elements(self.attachment_link_loc(item))
        return spans + links

    def item_attachment_el(self, item, attachment_name):
        item_type = self.item_type(item)
        for el in self.item_attachment_els(item_type, item):
            if el.text.strip() == attachment_name:
                return el

    def download_attachment(self, item, attachment, student=None):
        app.logger.info(f'Downloading attachment {attachment.file_name} from record ID {item.record_id}')
        utils.prepare_download_dir()
        self.when_present(self.attachment_link_loc(item), utils.get_short_timeout())
        self.item_attachment_el(item, attachment.file_name).click()
        file_path = f'{utils.default_download_dir()}/{attachment.file_name}'
        tries = 0
        max_tries = 15
        while tries <= max_tries:
            tries += 1
            try:
                assert (os.path.exists(file_path)
                        or self.is_present(self.SORRY_NO_ATTACHMENT_MSG))
                break
            except AssertionError:
                if tries == max_tries:
                    raise
                else:
                    time.sleep(1)
        if self.is_present(self.SORRY_NO_ATTACHMENT_MSG):
            # Get back on the student page for subsequent tests
            self.driver.get(f'{boa_utils.get_boa_base_url()}/student/{student.uid}')
            if item.__class__.__name__ == 'Note':
                self.show_notes()
            # TODO else show appts
            if attachment.sis_file_name:
                app.logger.info(
                    f'Cannot download SIS note ID {item.record_id} attachment ID {attachment.sis_file_name}')
            else:
                app.logger.error(
                    f'Cannot download Boa note ID {item.record_id} attachment ID {attachment.attachment_id}')
                raise
        else:
            # If the attachment file size is known, then make sure the download reaches the same size.
            if attachment.file_size:
                tries = 0
                max_tries = utils.get_medium_timeout()
                while tries <= max_tries:
                    tries += 1
                    try:
                        assert os.path.getsize(file_path) == attachment.file_size
                        break
                    except AssertionError:
                        if tries == max_tries:
                            raise
                        else:
                            app.logger.info(
                                f'File size is {os.path.getsize(file_path)}, waiting for {attachment.file_size}')
                            time.sleep(1)
        size = os.path.getsize(file_path)
        # Zap the download dir again to make sure no attachment downloads are left behind on the test machine
        utils.prepare_download_dir()
        return size
