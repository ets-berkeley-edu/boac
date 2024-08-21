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

from bea.pages.cohort_pages import CohortPages
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class CohortAndGroupAdmitPages(CohortPages):

    EXPORT_FERPA_CONFIRM_BUTTON = By.ID, 'are-you-sure-confirm'
    EXPORT_FERPA_CANCEL_BUTTON = By.ID, 'ferpa-reminder-cancel'

    def sort_by_cs_id(self):
        self.sort_by('cs_empl_id')

    def click_export_ferpa_confirm(self):
        self.wait_for_element_and_click(self.EXPORT_FERPA_CONFIRM_BUTTON)

    def click_export_ferpa_cancel(self):
        self.wait_for_element_and_click(self.EXPORT_FERPA_CANCEL_BUTTON)

    def export_admit_list(self, cohort):
        app.logger.info(f'Exporting admit list for cohort or group {cohort.cohort_id}')
        utils.prepare_download_dir()
        self.click_export_list()
        self.click_export_ferpa_confirm()
        return utils.wait_for_export_csv()

    @staticmethod
    def verify_admits_present_in_export(cohort, csv_reader):
        sids = []
        for r in csv_reader:
            sids.append(r['cs_empl_id'])
        sids.sort()
        cohort_sids = list(map(lambda m: m.sid, cohort.members))
        cohort_sids.sort()
        assert sids == cohort_sids

    @staticmethod
    def verify_no_email_in_export(csv_reader):
        cols = next(csv_reader)
        assert 'email' not in cols
        assert 'campus_email_1' not in cols

    @staticmethod
    def verify_mandatory_data_in_export(csv_reader):
        admit_statuses = []
        admit_terms = []
        applyuc_cpids = []
        birthdates = []
        citizenship_countries = []
        colleges = []
        current_sirs = []
        first_names = []
        freshmen_or_transfers = []
        highest_parent_education_levels = []
        last_names = []
        parent_1_education_levels = []
        parent_2_education_levels = []
        permanent_cities = []
        permanent_countries = []
        permanent_postals = []
        permanent_street_1s = []
        reentry_statuses = []
        residency_categories = []
        urems = []
        us_citizenship_statuses = []
        xethnics = []
        for r in csv_reader:
            admit_statuses.append(r['admit_status'])
            admit_terms.append(r['admit_term'])
            applyuc_cpids.append(r['applyuc_cpid'])
            birthdates.append(r['birthdate'])
            citizenship_countries.append(r['citizenship_country'])
            colleges.append(r['college'])
            current_sirs.append(r['current_sir'])
            first_names.append(r['first_name'])
            freshmen_or_transfers.append(r['freshman_or_transfer'])
            highest_parent_education_levels.append(r['highest_parent_education_level'])
            last_names.append(r['last_name'])
            parent_1_education_levels.append(r['parent_1_education_level'])
            parent_2_education_levels.append(r['parent_2_education_level'])
            permanent_cities.append(r['permanent_city'])
            permanent_countries.append(r['permanent_country'])
            permanent_postals.append(r['permanent_postal'])
            permanent_street_1s.append(r['permanent_street_1'])
            reentry_statuses.append(r['reentry_status'])
            residency_categories.append(r['residency_category'])
            urems.append(r['urem'])
            us_citizenship_statuses.append(r['us_citizenship_status'])
            xethnics.append(r['xethnic'])
        assert list(filter(None, admit_statuses)) == admit_statuses
        assert list(filter(None, admit_terms)) == admit_terms
        assert list(filter(None, applyuc_cpids)) == applyuc_cpids
        assert list(filter(None, birthdates)) == birthdates
        assert list(filter(None, citizenship_countries)) == citizenship_countries
        assert list(filter(None, colleges)) == colleges
        assert list(filter(None, current_sirs)) == current_sirs
        assert list(filter(None, first_names)) == first_names
        assert list(filter(None, freshmen_or_transfers)) == freshmen_or_transfers
        assert list(filter(None, highest_parent_education_levels)) == highest_parent_education_levels
        assert list(filter(None, last_names)) == last_names
        assert list(filter(None, parent_1_education_levels)) == parent_1_education_levels
        assert list(filter(None, parent_2_education_levels)) == parent_2_education_levels
        assert list(filter(None, permanent_cities)) == permanent_cities
        assert list(filter(None, permanent_countries)) == permanent_countries
        assert list(filter(None, permanent_postals)) == permanent_postals
        assert list(filter(None, permanent_street_1s)) == permanent_street_1s
        assert list(filter(None, reentry_statuses)) == reentry_statuses
        assert list(filter(None, residency_categories)) == residency_categories
        assert list(filter(None, urems)) == urems
        assert list(filter(None, us_citizenship_statuses)) == us_citizenship_statuses
        assert list(filter(None, xethnics)) == xethnics

    @staticmethod
    def verify_optional_data_in_export(csv_reader):
        application_fee_waiver_flags = []
        athlete_statuses = []
        family_dependents_nums = []
        family_incomes = []
        family_is_single_parents = []
        first_generation_colleges = []
        foster_care_flags = []
        hispanics = []
        hs_unweighted_gpas = []
        hs_weighted_gpas = []
        is_military_dependents = []
        last_school_lcff_plus_flags = []
        middle_names = []
        military_statuses = []
        non_immigrant_visa_currents = []
        non_immigrant_visa_planneds = []
        permanent_regions = []
        permanent_residence_countries = []
        permanent_streets_2 = []
        special_program_ceps = []
        student_dependents_nums = []
        student_incomes = []
        student_is_single_parents = []
        summer_bridge_statuses = []
        transfer_gpas = []
        us_non_citizen_statuses = []
        for r in csv_reader:
            application_fee_waiver_flags.append(r['application_fee_waiver_flag'])
            athlete_statuses.append(r['athlete_status'])
            family_dependents_nums.append(r['family_dependents_num'])
            family_incomes.append(r['family_income'])
            family_is_single_parents.append(r['family_is_single_parent'])
            first_generation_colleges.append(r['first_generation_college'])
            foster_care_flags.append(r['foster_care_flag'])
            hispanics.append(r['hispanic'])
            hs_unweighted_gpas.append(r['hs_unweighted_gpa'])
            hs_weighted_gpas.append(r['hs_weighted_gpa'])
            is_military_dependents.append(r['is_military_dependent'])
            last_school_lcff_plus_flags.append(r['last_school_lcff_plus_flag'])
            middle_names.append(r['middle_name'])
            military_statuses.append(r['military_status'])
            non_immigrant_visa_currents.append(r['non_immigrant_visa_current'])
            non_immigrant_visa_planneds.append(r['non_immigrant_visa_planned'])
            permanent_regions.append(r['permanent_region'])
            permanent_residence_countries.append(r['permanent_residence_country'])
            permanent_streets_2.append(r['permanent_street_2'])
            special_program_ceps.append(r['special_program_cep'])
            student_dependents_nums.append(r['student_dependents_num'])
            student_incomes.append(r['student_income'])
            student_is_single_parents.append(r['student_is_single_parent'])
            summer_bridge_statuses.append(r['summer_bridge_status'])
            transfer_gpas.append(r['transfer_gpa'])
            us_non_citizen_statuses.append(r['us_non_citizen_status'])
        assert list(filter(None, application_fee_waiver_flags))
        assert list(filter(None, athlete_statuses))
        assert list(filter(None, family_dependents_nums))
        assert list(filter(None, family_incomes))
        assert list(filter(None, family_is_single_parents))
        assert list(filter(None, first_generation_colleges))
        assert list(filter(None, hispanics))
        assert list(filter(None, hs_unweighted_gpas))
        assert list(filter(None, hs_weighted_gpas))
        assert list(filter(None, is_military_dependents))
        assert list(filter(None, last_school_lcff_plus_flags))
        assert list(filter(None, middle_names))
        assert list(filter(None, military_statuses))
        assert list(filter(None, non_immigrant_visa_currents))
        assert list(filter(None, non_immigrant_visa_planneds))
        assert list(filter(None, permanent_regions))
        assert list(filter(None, permanent_residence_countries))
        assert list(filter(None, permanent_streets_2))
        assert list(filter(None, special_program_ceps))
        assert list(filter(None, student_dependents_nums))
        assert list(filter(None, student_incomes))
        assert list(filter(None, student_is_single_parents))
        assert list(filter(None, summer_bridge_statuses))
        assert list(filter(None, transfer_gpas))
        assert list(filter(None, us_non_citizen_statuses))
