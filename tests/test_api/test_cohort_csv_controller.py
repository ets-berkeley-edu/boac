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

from boac.api.csv_file_download_utils import get_students_csv_header_labels
from boac.merged.sis_terms import current_term_id
from boac.models.cohort_filter import CohortFilter
import pytest
import simplejson as json
from tests.test_api.api_test_utils import all_cohorts_owned_by, api_get_cohort

admin_uid = '177473'
asc_advisor_uid = '1081940'
asc_and_coe_advisor_uid = '90412'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'


class TestDownloadCohortCsv:

    @classmethod
    def setup_class(cls):
        cls.coe_owned_cohort = next((c for c in all_cohorts_owned_by(coe_advisor_uid) if c['name'] == 'Radioactive Women and Men'), None)
        cls.asc_owned_cohort = next((c for c in all_cohorts_owned_by(asc_advisor_uid) if c['name'] == 'All sports'), None)

    @classmethod
    def _api_download_cohort_csv(cls, client, cohort_id, csv_columns_selected, expected_status_code=200):
        response = client.post(
            '/api/cohort_csv/download',
            data=json.dumps({
                'cohortId': cohort_id,
                'csvColumnsSelected': csv_columns_selected,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.data

    def test_download_csv_not_authenticated(self, client):
        """API requires authentication."""
        self._api_download_cohort_csv(
            client,
            self.coe_owned_cohort['id'],
            csv_columns_selected=['sid'],
            expected_status_code=401,
        )

    def test_download_csv_unauthorized(self, client, fake_auth):
        """Sensitive COE attributes are not available to ASC advisor, when downloading CSV."""
        fake_auth.login(asc_advisor_uid)
        response = self._api_download_cohort_csv(
            client,
            cohort_id=self.asc_owned_cohort['id'],
            csv_columns_selected=['coe_status'],
        )
        # If you strip away line breaks and double-quotes then you are left with nothing more than a column header.
        data = response.decode('utf-8').replace('\n', '').replace('\r', '').replace('"', '')
        assert data == 'CoE status'

    def test_download_csv(self, client, fake_auth):
        """Advisor can download cohort CSV."""
        fake_auth.login(asc_advisor_uid)
        expected_sids = ['11667051', '2345678901', '3456789012', '5678901234', '7890123456', '9100000000']
        cohort = CohortFilter.create(
            uid=asc_advisor_uid,
            name='Download Me',
            filter_criteria={
                'cohortOwnerAcademicPlans': ['*'],
            },
        )
        api_json = api_get_cohort(client, cohort_id=cohort['id'], include_students=True)
        sids = sorted([student['sid'] for student in api_json['students']])
        assert sids == expected_sids
        data = self._api_download_cohort_csv(client, cohort['id'], csv_columns_selected=['sid'])
        sids_in_csv = [s for s in data.decode('utf-8').split() if s.isdigit()]
        assert sids_in_csv == expected_sids

        # Another ASC advisor downloads same CSV
        client.get('/api/auth/logout')
        fake_auth.login('6446')
        data = self._api_download_cohort_csv(client, cohort['id'], csv_columns_selected=['sid'])
        sids_in_csv = [s for s in data.decode('utf-8').split() if s.isdigit()]
        assert sids_in_csv == expected_sids


class TestDownloadCsvPerFilters:

    @classmethod
    def _api_download_csv_per_filters(cls, client, json_data=(), expected_status_code=200):
        response = client.post(
            '/api/cohort_csv/download_per_filters',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_download_csv_not_authenticated(self, client):
        """API requires authentication."""
        self._api_download_csv_per_filters(client, expected_status_code=401)

    def test_download_csv_with_empty(self, client, fake_auth):
        """API requires non-empty input."""
        fake_auth.login(coe_advisor_uid)
        self._api_download_csv_per_filters(client, {'filters': ()}, expected_status_code=400)

    def test_download_csv_unauthorized(self, client, fake_auth):
        """ASC advisor is not allowed to query with COE attributes."""
        fake_auth.login(asc_advisor_uid)
        self._api_download_csv_per_filters(
            client,
            {
                'filters': [
                    {'key': 'coeAcademicStandings', 'value': ['P']},
                ],
                'csvColumnsSelected': [
                    'first_name',
                    'last_name',
                    'sid',
                ],
            },
            expected_status_code=403,
        )

    def test_download_csv(self, client, fake_auth):
        """Advisor can download CSV with ALL students of cohort."""
        fake_auth.login(coe_advisor_uid)
        data = {
            'filters': [
                {'key': 'coeEthnicities', 'value': ['H', 'B']},
            ],
            'csvColumnsSelected': [
                'first_name',
                'last_name',
                'sid',
                'email',
                'phone',
                'college',
                'majors',
                'level_by_units',
                'terms_in_attendance',
                'expected_graduation_term',
                'units_completed',
                'term_gpa_2172',
                'term_gpa_2175',
                'cumulative_gpa',
                'program_status',
                'college_advisor',
                'coe_status',
                'course_activity',
            ],
        }
        response = client.post(
            '/api/cohort_csv/download_per_filters',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = response.data.decode('UTF-8').split('\n')
        # Verify that 'course_activity' related columns are present.
        header_label_lookup = get_students_csv_header_labels(current_term_id())
        expected_headers = ['first_name', 'last_name', 'sid', 'email', 'phone', 'majors', 'college', 'level_by_units',
                            'terms_in_attendance', 'expected_graduation_term', 'units_completed', 'term_gpa_2172',
                            'term_gpa_2175', 'cumulative_gpa', 'program_status', 'college_advisor', 'coe_status',
                            'Class Name', 'Units', 'Mid-point Grade', 'Final Grade']
        for expected_header in expected_headers:
            expected_label = header_label_lookup.get(expected_header, expected_header)
            assert expected_label in csv[0]
        for row in csv:
            if row.startswith('Deborah,Davies'):
                assert '11667051' in row
                assert 'Junior' in row
                assert 'English BA' in row
                assert ',Engineering; Undergrad Letters & Science,' in row
                assert 'BURMESE 1A' in row or 'MED ST 205' in row or 'NUC ENG 124' in row or 'PHYSED 11' in row or 'SOCIOL 198' in row

    def test_download_csv_custom_columns(self, client, fake_auth):
        """Advisor can generate a CSV with the columns they want."""
        fake_auth.login(coe_advisor_uid)
        data = {
            'filters': [
                {'key': 'levels', 'value': 'Junior'},
            ],
            'csvColumnsSelected': [
                'majors',
                'college',
                'level_by_units',
                'terms_in_attendance',
                'expected_graduation_term',
                'units_completed',
                'term_gpa_2172',
                'cumulative_gpa',
                'program_status',
                'intended_majors',
                'minors',
            ],
        }
        response = client.post(
            '/api/cohort_csv/download_per_filters',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'csv' in response.content_type
        csv = response.data.decode('UTF-8').split('\n')
        header_label_lookup = get_students_csv_header_labels(current_term_id())
        expected_headers = ['majors', 'college', 'level_by_units', 'terms_in_attendance', 'expected_graduation_term',
                            'units_completed', 'term_gpa_2172', 'cumulative_gpa', 'program_status', 'intended_majors',
                            'minors']
        for expected_header in expected_headers:
            expected_label = header_label_lookup.get(expected_header, expected_header)
            assert expected_label in csv[0]
        for row in csv[1:]:
            if row.startswith('Chemistry BS'):
                assert ',Chemistry,' in row
                assert 'Junior,4,Fall 2019,34,3.500,3.495,Active,' in row
            elif row.startswith('English BA; Political Economy BA'):
                assert ',Undergrad Letters & Science,' in row
                assert 'Junior,5,Fall 2019,70,,3.005,Active,' in row
            elif row:
                pytest.fail(f'Unexpected CSV content: {row}')

    admit_keys = [
        'applyuc_cpid',
        'cs_empl_id',
        'residency_category',
        'freshman_or_transfer',
        'admit_term',
        'admit_status',
        'current_sir',
        'college',
        'first_name',
        'middle_name',
        'last_name',
        'birthdate',
        'daytime_phone',
        'mobile',
        'permanent_street_1',
        'permanent_street_2',
        'permanent_city',
        'permanent_region',
        'permanent_postal',
        'permanent_country',
        'xethnic',
        'hispanic',
        'urem',
        'first_generation_college',
        'parent_1_education_level',
        'parent_2_education_level',
        'highest_parent_education_level',
        'hs_unweighted_gpa',
        'hs_weighted_gpa',
        'transfer_gpa',
        'application_fee_waiver_flag',
        'foster_care_flag',
        'family_is_single_parent',
        'student_is_single_parent',
        'family_dependents_num',
        'student_dependents_num',
        'family_income',
        'student_income',
        'is_military_dependent',
        'military_status',
        'reentry_status',
        'athlete_status',
        'summer_bridge_status',
        'last_school_lcff_plus_flag',
        'special_program_cep',
        'us_citizenship_status',
        'us_non_citizen_status',
        'citizenship_country',
        'permanent_residence_country',
        'non_immigrant_visa_current',
        'non_immigrant_visa_planned',
        'uid',
    ]

    @classmethod
    def _api_download_admit_csv(cls, client, expected_status_code=200):
        data = {
            'filters': [
                {'key': 'isFirstGenerationCollege', 'value': True},
            ],
            'csvColumnsSelected': cls.admit_keys,
            'domain': 'admitted_students',
        }
        response = client.post(
            '/api/cohort_csv/download_per_filters',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response

    def test_download_csv_admit_domain(self, client, fake_auth):
        """Download CSV admit domain."""
        fake_auth.login(ce3_advisor_uid)
        response = self._api_download_admit_csv(client)
        assert 'csv' in response.content_type
        csv = str(response.data)
        assert ','.join(self.admit_keys) in csv
        assert (
            '19938035,00005852,RES,Transfer,Spring,No,No,College of Letters and Science,'
            'Ralph,,Burgess,1984-09-04,984.110.7693x347,681-857-8070,9590 Chang Extensions,'
            'Suite 478,East Jacobton,NY,55531,United States,International,F,No,Yes,MasterDegree,'
            '3 - High School Graduate,,0.86,0.51,2.47,FeeWaiver,Y,,,05,02,41852,942,Y,'
            'ReserveOfficersTrainingProgram,No,,,,,Citizen,,United States,,,,123'
        ) in csv
        assert (
            '98002344,00029117,INT,Freshman,Spring,No,No,College of Engineering,Daniel,J,Mcknight,1993-07-06,859-319-8215x8689,'
            '231.865.8093,87758 Brown Throughway,Suite 657,West Andrea,M,25101,United States,White,T,,'
            'Yes,,5 - College Attended,,2.51,2.7,3.23,,,,Y,0,02,23915,426,Y,,,Committed,,1,'
            'Destination College,Citizen,,United States,,,,'
        ) in csv

    def test_admit_domain_denies_non_ce3_advisor(self, user_factory, client, fake_auth):
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        self._api_download_admit_csv(client, 404)
