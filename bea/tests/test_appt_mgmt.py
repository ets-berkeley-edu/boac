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
import random

import pytest
from flask import current_app as app

from bea.config.bea_test_config import BEATestConfig
from bea.models.notes_and_appts.note_comment import NoteComment
from bea.test_utils import boa_utils, nessie_timeline_utils, utils


@pytest.mark.usefixtures('page_objects')
class TestApptMgmt:

    test = BEATestConfig()
    test.appt_mgmt()

    auth_users = boa_utils.get_authorized_users()
    director = boa_utils.get_director(auth_users)
    other_advisor = boa_utils.get_advising_data_advisor(test.dept, test.advisor)

    app.logger.info(f'Advisor UID {test.advisor.uid}, other advisor UID {other_advisor.uid}')

    # Find a student with a non-legacy (Calendly or YCBM) appointment
    random.shuffle(test.test_students)
    test_student = None
    test_appt = None
    for _student in test.test_students:
        _appts = nessie_timeline_utils.get_ycbm_appts(_student) + nessie_timeline_utils.get_calendly_appts(_student)
        if _appts:
            test_student = _student
            test_appt = _appts[0]
            break

    comment_1 = NoteComment()

    # COMMENTS

    def test_comment_body_required(self):
        self.homepage.dev_auth(self.test.advisor)
        self.student_page.load_page(self.test_student)
        self.student_page.show_appts()
        self.student_page.expand_item(self.test_appt)
        self.student_page.click_add_appt_comment_button(self.test_appt)
        self.student_page.wait_for_element_and_click(self.student_page.appt_new_comment_save_loc(self.test_appt))
        self.student_page.when_present(self.student_page.COMMENT_SAVE_ERROR, utils.get_short_timeout())

    def test_add_comment_and_cancel(self):
        self.student_page.wait_for_textbox_and_send_keys(
            self.student_page.appt_new_comment_text_area_loc(self.test_appt),
            'A comment to forget',
        )
        self.student_page.cancel_new_appt_comment(self.test_appt)
        self.student_page.when_present(
            self.student_page.appt_add_comment_button_loc(self.test_appt),
            utils.get_short_timeout(),
        )

    def test_add_comment(self):
        self.comment_1.body = f'Comment 1 body {utils.get_test_identifier()}'
        self.student_page.add_appt_comment(self.test_appt, self.comment_1)
        comments = boa_utils.get_appt_comments(self.test_appt)
        matching = [c for c in comments if c.body == self.comment_1.body]
        assert len(matching) == 1
        self.comment_1.comment_id = matching[0].comment_id
        assert self.student_page.appt_comment_body_text(self.test_appt, self.comment_1) == self.comment_1.body

    def test_edit_comment(self):
        self.comment_1.body = f'{self.comment_1.body} - EDITED'
        self.student_page.click_edit_appt_comment_button(self.test_appt, self.comment_1)
        self.student_page.wait_for_textbox_and_send_keys(
            self.student_page.appt_edit_comment_text_area_loc(self.test_appt, self.comment_1),
            self.comment_1.body,
        )
        self.student_page.save_edit_appt_comment(self.test_appt, self.comment_1)
        assert self.student_page.appt_comment_body_text(self.test_appt, self.comment_1) == self.comment_1.body

    def test_non_author_sees_comment(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(self.other_advisor)
        self.student_page.load_page(self.test_student)
        self.student_page.show_appts()
        self.student_page.expand_item(self.test_appt)
        assert self.student_page.appt_comment_body_text(self.test_appt, self.comment_1) == self.comment_1.body

    def test_non_author_cannot_edit_comment(self):
        assert not self.student_page.is_present(
            self.student_page.appt_comment_edit_button_loc(self.test_appt, self.comment_1),
        )

    def test_admin_can_delete_comment(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth()
        self.student_page.load_page(self.test_student)
        self.student_page.show_appts()
        self.student_page.expand_item(self.test_appt)
        self.student_page.delete_appt_comment(self.test_appt, self.comment_1)

    def test_deleted_comment_not_visible(self):
        assert not self.student_page.is_present(
            self.student_page.appt_comment_body_loc(self.test_appt, self.comment_1),
        )
        remaining = boa_utils.get_appt_comments(self.test_appt)
        assert all(c.comment_id != self.comment_1.comment_id for c in remaining)

    def test_admin_cannot_add_comment(self):
        self.student_page.click_add_appt_comment_button(self.test_appt)
        self.student_page.wait_for_textbox_and_send_keys(
            self.student_page.appt_new_comment_text_area_loc(self.test_appt),
            'An admin comment attempt',
        )
        assert not self.student_page.element(self.student_page.appt_new_comment_save_loc(self.test_appt)).is_enabled()
        self.student_page.cancel_new_appt_comment(self.test_appt)
