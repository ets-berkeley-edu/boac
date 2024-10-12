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
import csv
import re
from zipfile import ZipFile

from bea.pages.create_note_modal import CreateNoteModal
from bea.pages.student_page_timeline import StudentPageTimeline
from flask import current_app as app
from selenium.webdriver.common.by import By


class StudentPageEForm(StudentPageTimeline, CreateNoteModal):

    # E-FORMS

    E_FORMS_BUTTON = (By.ID, 'timeline-tab-eForm')
    SHOW_HIDE_E_FORMS_BUTTON = (By.ID, 'toggle-expand-all-eForms')
    E_FORM_MSG_ROW = By.XPATH, '//tr[contains(@id, "permalink-eForm-")]'
    E_FORMS_DOWNLOAD_LINK = (By.ID, 'download-notes-link')

    def show_e_forms(self):
        app.logger.info('Checking eForms tab')
        self.wait_for_element_and_click(self.E_FORMS_BUTTON)
        if self.is_present(self.SHOW_HIDE_E_FORMS_BUTTON) and 'Show?' in self.element(
                self.SHOW_HIDE_E_FORMS_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_E_FORMS_BUTTON)

    @staticmethod
    def expected_e_form_id_sort_order(e_forms):
        e_forms.sort(key=lambda ef: [ef.created_date, ef.record_id])
        e_forms.reverse()
        return [e_form.record_id for e_form in e_forms]

    @staticmethod
    def e_form_data_loc(e_form, label):
        return By.XPATH, f"//tr[@id='permalink-eForm-{e_form.record_id}']//dt[text()='{label}']/following-sibling::dd"

    def collapsed_e_form_date(self, e_form):
        date_loc = By.ID, f'collapsed-eForm-{e_form.record_id}-created-at'
        return self.el_text_if_exists(date_loc, 'Last updated on')

    def expanded_e_form_created_date(self, e_form):
        created_loc = By.ID, f'expanded-eForm-{e_form.record_id}-created-at'
        if self.is_present(created_loc):
            text = self.element(created_loc).text.replace('Created on', '')
            return re.sub(r'/\s+ /', ' ', text).strip()
        else:
            return None

    def expanded_e_form_updated_date(self, e_form):
        updated_loc = By.ID, f'expanded-eForm-{e_form.record_id}-updated-at'
        if self.is_present(updated_loc):
            text = self.element(updated_loc).text.replace('Last updated on', '')
            return re.sub(r'/\s+ /', ' ', text).strip()
        else:
            return None

    def expanded_e_form_action(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Action'))

    def expanded_e_form_course(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Course'))

    def expanded_e_form_date_final(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Final Date & Time Stamp'))

    def expanded_e_form_date_init(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Date Initiated'))

    def expanded_e_form_id(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Form ID'))

    def expanded_e_form_status(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Form Status '))

    def expanded_e_form_term(self, e_form):
        return self.el_text_if_exists(self.e_form_data_loc(e_form, 'Term'))

    # Downloads

    def e_forms_export_zip_file_name(self, student):
        return self.export_zip_file_name(student, 'eForms')

    def e_forms_export_csv_file_name(self, student):
        return self.export_csv_file_name(student, 'eForms')

    def download_e_forms(self, student):
        app.logger.info(f'Downloading eForms for UID {student.uid}')
        self.download_file(self.E_FORMS_DOWNLOAD_LINK, self.e_forms_export_zip_file_name(student))

    def e_form_export_file_names(self, student):
        return self.downloaded_zip_file_name_list(self.e_forms_export_zip_file_name(student))

    def expected_e_form_export_file_names(self, student):
        return [self.e_forms_export_csv_file_name(student)]

    def parse_e_forms_export_csv_to_table(self, student):
        with ZipFile(self.e_forms_export_zip_file_name(student)) as zip_file:
            with zip_file.read(self.e_forms_export_csv_file_name(student)) as csv_file:
                return csv.DictReader(open(csv_file))

    @staticmethod
    def verify_e_form_in_export_csv(student, e_form, csv_reader):
        rows = list(csv_reader)
        for row in rows:
            try:
                assert row['created_date'] == e_form.created_date.strftime('%Y-%m-%d')
                assert row['student_sid'] == int(student.sid)
                assert row['student_name'] == student.full_name
                assert row['eform_id'] == e_form.form_id
                if e_form.action:
                    assert row['late_change_request_action'] == e_form.action
                if e_form.grading_basis:
                    assert row['grading_basis'] == e_form.grading_basis
                if e_form.requested_grading_basis:
                    assert row['requested_grading_basis'] == e_form.requested_grading_basis
                if e_form.units_taken:
                    assert row['units_taken'] == e_form.units_taken
                if e_form.requested_units_taken:
                    assert row['requested_units_taken'] == e_form.requested_units_taken
                if e_form.status:
                    assert row['late_change_request_status'] == e_form.status
                if e_form.term:
                    assert row['late_change_request_term'] == e_form.term
                assert row['late_change_request_course'] == e_form.course
                return True
            except AssertionError:
                if row == rows[-1]:
                    return False
