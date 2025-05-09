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

from boac.models.authorized_user import AuthorizedUser
from boac.models.curated_group import CuratedGroup
import simplejson as json

admin_uid = '177473'
asc_advisor_uid = '1081940'
asc_and_coe_advisor_uid = '90412'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'


class TestCohortFilterOptions:

    @classmethod
    def _api_cohort_filter_categories(cls, client, data, expected_status_code=200):
        response = client.post(
            '/api/cohort_filter_categories',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_filter_options_api_not_authenticated(self, client):
        """Menu API cohort-filter-options requires authentication."""
        self._api_cohort_filter_categories(client, data={}, expected_status_code=401)

    def test_filter_options_with_nothing_disabled(self, client, fake_auth):
        """Menu API with all menu options available."""
        fake_auth.login(coe_advisor_uid)
        post_data = {'existingFilters': [], 'ownerUid': coe_advisor_uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        for filter_category in api_json:
            for option in filter_category['options']:
                assert 'disabled' not in option
                if option['type']['ux'] == 'dropdown':
                    for dropdown_option in option['options']:
                        assert 'disabled' not in dropdown_option

    def test_filter_options_for_guest_advisor(self, user_factory, client, fake_auth):
        """Filter options available to GUEST advisor."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        post_data = {'existingFilters': [], 'ownerUid': advisor.uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        assert len(api_json)
        assert 'options' in list(api_json)[0]

    def test_filter_options_for_user_of_type_other(self, user_factory, client, fake_auth):
        """Filter options available to ZZZZZ user."""
        advisor = user_factory(dept_codes=['ZZZZZ'])
        fake_auth.login(advisor.uid)
        post_data = {'existingFilters': [], 'ownerUid': advisor.uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        assert len(api_json)
        assert 'options' in list(api_json)[0]

    def test_filter_options_my_students_for_me(self, client, fake_auth):
        """Returns user's own academic plans under 'My Students'."""
        fake_auth.login(coe_advisor_uid)
        post_data = {'existingFilters': [], 'ownerUid': coe_advisor_uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        my_students = next(opt for filter_category in api_json for opt in filter_category['options'] if opt['label']['primary'] == 'My Students')
        assert len(my_students['options']) == 5
        assert {'name': 'All plans', 'value': '*'} in my_students['options']
        assert {'name': 'Bioengineering BS', 'value': '16288U'} in my_students['options']
        assert {'name': 'Engineering Undeclared UG', 'value': '162B0U'} in my_students['options']
        assert {'name': 'BioE/MSE Joint Major BS', 'value': '162B3U'} in my_students['options']
        assert {'name': 'Bioengineering UG', 'value': '16I010U'} in my_students['options']

    def test_filter_options_my_students_for_not_me(self, client, fake_auth):
        """Returns another user's academic plans under 'My Students'."""
        fake_auth.login(coe_advisor_uid)
        post_data = {'existingFilters': [], 'ownerUid': asc_advisor_uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        my_students = next(opt for filter_category in api_json for opt in filter_category['options'] if opt['label']['primary'] == 'My Students')
        assert len(my_students['options']) == 4
        assert {'name': 'All plans', 'value': '*'} in my_students['options']
        assert {'name': 'English BA', 'value': '25345U'} in my_students['options']
        assert {'name': 'English UG', 'value': '25I039U'} in my_students['options']
        assert {'name': 'Medieval Studies UG', 'value': '25I054U'} in my_students['options']

    def test_filter_options_with_category_disabled(self, client, fake_auth):
        """The transfer option is disabled if it is in existing-filters."""
        fake_auth.login(coe_advisor_uid)
        post_data = {'existingFilters': [{'key': 'transfer', 'value': True}], 'ownerUid': coe_advisor_uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        assert len(api_json)
        for filter_category in api_json:
            for option in filter_category['options']:
                if option['key'] == 'transfer':
                    assert option['disabled'] is True
                else:
                    assert 'disabled' not in option

    def test_filter_options_with_one_disabled(self, client, fake_auth):
        """The 'Freshman' sub-menu option is disabled if it is already in cohort filter set."""
        fake_auth.login(coe_advisor_uid)
        post_data = {
            'existingFilters': [
                {'key': 'levels', 'value': 'Freshman'},
                {'key': 'levels', 'value': 'Sophomore'},
                {'key': 'levels', 'value': 'Junior'},
                {'key': 'coeAdvisorLdapUids', 'value': '1022796'},
            ],
            'ownerUid': coe_advisor_uid,
        }
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        assert len(api_json)
        assertion_count = 0
        for filter_category in api_json:
            for option in filter_category['options']:
                # All top-level category menus are enabled
                assert 'disabled' not in option
                if option['key'] == 'levels':
                    for dropdown_option in option['options']:
                        disabled = dropdown_option.get('disabled')
                        if dropdown_option['value'] in ['Freshman', 'Sophomore', 'Junior']:
                            assert disabled is True
                            assertion_count += 1
                        else:
                            assert disabled is None
                else:
                    assert 'disabled' not in option
        assert assertion_count == 3

    def test_all_options_in_category_disabled(self, client, fake_auth):
        """Disable the category if all its options are in existing-filters."""
        fake_auth.login(coe_advisor_uid)
        post_data = {
            'existingFilters': [
                {'key': 'cohortOwnerAcademicPlans', 'value': '*'},
                {'key': 'levels', 'value': 'Doctoral Candidate > 6'},
                {'key': 'levels', 'value': 'Doctoral Candidate <= 6'},
                {'key': 'levels', 'value': 'Doctoral Pre-Candidacy'},
                {'key': 'levels', 'value': 'Masters/Professional'},
                {'key': 'levels', 'value': 'Senior'},
                {'key': 'levels', 'value': 'Junior'},
                {'key': 'levels', 'value': 'Sophomore'},
                {'key': 'levels', 'value': 'Freshman'},
                {'key': 'visaTypes', 'value': '*'},
            ],
            'ownerUid': coe_advisor_uid,
        }
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        for filter_category in api_json:
            for option in filter_category['options']:
                if option['key'] == 'cohortOwnerAcademicPlans':
                    assert option.get('disabled') is True
                elif option['key'] == 'levels':
                    assert option.get('disabled') is True
                    for dropdown_option in option['options']:
                        assert dropdown_option.get('disabled') is True
                elif option['key'] == 'visaTypes':
                    assert option.get('disabled') is True
                else:
                    assert 'disabled' not in option

    def test_range_of_entering_terms(self, user_factory, client, fake_auth):
        """Cohort filter: Range of entering terms."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        post_data = {'existingFilters': [], 'ownerUid': advisor.uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        # Find sample category
        academic_filter_category = next((category for category in api_json if category['label'] == 'Academic'), None)
        entering_terms_filter = next((option for option in academic_filter_category['options'] if option['key'] == 'enteringTerms'), None)
        options = entering_terms_filter.get('options')
        assert len(options) == 4
        assert [o['name'] for o in options] == ['2015 Fall', '2015 Summer', '2015 Spring', '1993 Fall']

    def test_range_of_expected_grad_terms(self, user_factory, client, fake_auth):
        """Cohort filter: Range of expected grad terms."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        post_data = {'existingFilters': [], 'ownerUid': advisor.uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        # Find sample category
        academic_filter_category = next((category for category in api_json if category['label'] == 'Academic'), None)
        entering_terms_dropdown = next((option for option in academic_filter_category['options'] if option['key'] == 'expectedGradTerms'), None)
        options = entering_terms_dropdown['options']
        assert len(options['Past']) == 1
        assert options['Past'][0]['name'] == '1997 Fall'

    def test_range_of_majors(self, user_factory, client, fake_auth):
        """Cohort filter: Range of major terms."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        post_data = {'existingFilters': [], 'ownerUid': advisor.uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        # Find sample category
        academic_filter_category = next((category for category in api_json if category['label'] == 'Academic'), None)
        majors_dropdown = next((option for option in academic_filter_category['options'] if option['key'] == 'majors'), None)
        options = majors_dropdown['options']
        assert {'name': 'Chemistry BS', 'value': 'Chemistry BS'} in options
        assert {'name': 'Nuclear Engineering BS', 'value': 'Nuclear Engineering BS'} in options
        assert {'name': 'Mathematics PhD', 'value': 'Mathematics PhD'} not in options

    def test_range_of_graduate_programs(self, user_factory, client, fake_auth):
        """Cohort filter: Range of graduate programs."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        post_data = {'existingFilters': [], 'ownerUid': advisor.uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        # Find sample category
        academic_filter_category = next((category for category in api_json if category['label'] == 'Academic'), None)
        graduate_programs_dropdown = next((option for option in academic_filter_category['options'] if option['key'] == 'graduatePrograms'), None)
        assert len(graduate_programs_dropdown['options']) == 1
        assert graduate_programs_dropdown['options'][0] == {'name': 'Mathematics PhD', 'value': 'Mathematics PhD'}

    def test_no_curated_group_options(self, client, fake_auth):
        """User with no curated groups gets no cohort filter option where key='curatedGroupIds'."""
        fake_auth.login(asc_and_coe_advisor_uid)
        user_id = AuthorizedUser.get_id_per_uid(asc_and_coe_advisor_uid)
        assert not CuratedGroup.get_curated_groups(user_id)
        post_data = {'existingFilters': [], 'ownerUid': asc_and_coe_advisor_uid}
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        verified = False
        for filter_category in api_json:
            for option in filter_category['options']:
                if option['key'] == 'curatedGroupIds':
                    assert option['disabled'] is True
                    verified = True
        assert verified

    def test_invalid_domain_value(self, user_factory, client, fake_auth):
        """Cohort filter: Invalid domain value."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        post_data = {
            'domain': 'this_is_an_invalid_domain',
            'existingFilters': [],
            'ownerUid': advisor.uid,
        }
        self._api_cohort_filter_categories(client, data=post_data, expected_status_code=400)

    def test_admitted_students_domain_denied(self, user_factory, client, fake_auth):
        """Cohort filter: Denied access to Admitted students."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        post_data = {
            'domain': 'admitted_students',
            'existingFilters': [],
            'ownerUid': advisor.uid,
        }
        self._api_cohort_filter_categories(client, data=post_data, expected_status_code=404)

    def test_admitted_students_domain(self, client, fake_auth):
        """Cohort filter: Admitted students."""
        fake_auth.login(ce3_advisor_uid)
        post_data = {
            'domain': 'admitted_students',
            'existingFilters': [],
            'ownerUid': ce3_advisor_uid,
        }
        api_json = self._api_cohort_filter_categories(client, data=post_data)
        assert len(api_json)
        for filter_category in api_json:
            for option in filter_category['options']:
                # Verify the 'default' filters are not present.
                assert option['key'] != 'unitRanges'
                assert option['domain'] == 'admitted_students'


class TestTranslateToFilterOptions:

    @classmethod
    def _api_translate_to_filter_options(cls, client, data, expected_status_code=200):
        response = client.post(
            '/api/cohort_filter_options/translate',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_translate_criteria_when_empty(self, client, fake_auth):
        """Empty criteria translates to zero rows."""
        fake_auth.login(coe_advisor_uid)
        post_data = {
            'criteria': {},
            'ownerUid': coe_advisor_uid,
        }
        assert self._api_translate_to_filter_options(client, data=post_data) == []

    def test_translate_criteria_with_boolean(self, client, fake_auth):
        """Filter-criteria with boolean is properly translated."""
        fake_auth.login(coe_advisor_uid)
        post_data = {'criteria': {'isInactiveCoe': False}, 'ownerUid': coe_advisor_uid}
        api_json = self._api_translate_to_filter_options(client, data=post_data)
        assert len(api_json) == 1
        assert api_json[0]['label']['primary'] == 'Inactive (COE)'
        assert api_json[0]['key'] == 'isInactiveCoe'
        assert api_json[0]['value'] is False

    def test_translate_criteria_with_array(self, client, fake_auth):
        """Filter-criteria with array is properly translated."""
        fake_auth.login(coe_advisor_uid)
        post_data = {
            'criteria': {
                'levels': ['Freshman', 'Sophomore'],
                'majors': ['Chemistry BS', 'Nuclear Engineering BS'],
            },
            'ownerUid': coe_advisor_uid,
        }
        api_json = self._api_translate_to_filter_options(client, data=post_data)
        assert len(api_json) == 4
        # Levels
        assert api_json[0]['label']['primary'] == api_json[1]['label']['primary'] == 'Level'
        assert api_json[0]['key'] == api_json[1]['key'] == 'levels'
        assert api_json[0]['value'] == 'Freshman'
        assert api_json[1]['value'] == 'Sophomore'
        # Majors
        assert api_json[2]['label']['primary'] == api_json[3]['label']['primary'] == 'Major'
        assert api_json[2]['key'] == api_json[3]['key'] == 'majors'
        assert api_json[2]['value'] == 'Chemistry BS'
        assert api_json[3]['value'] == 'Nuclear Engineering BS'

    def test_handle_last_name_ranges(self, client, fake_auth):
        """Filter-criteria with last_name range is properly translated."""
        fake_auth.login(coe_advisor_uid)
        last_name_ranges = [
            {'min': 'B', 'max': 'D'},
            {'min': 'M', 'max': 'Z'},
        ]
        post_data = {
            'criteria': {
                'lastNameRanges': last_name_ranges,
            },
            'ownerUid': coe_advisor_uid,
        }
        api_json = self._api_translate_to_filter_options(client, data=post_data)
        assert len(api_json) == 2

        def _verify(index):
            assert api_json[index]['label']['primary'] == 'Last Name'
            assert api_json[index]['key'] == 'lastNameRanges'
            assert api_json[index]['value'] == last_name_ranges[index]
        _verify(0)
        _verify(1)

    def test_translate_criteria_my_students_for_me(self, client, fake_auth):
        """User's own 'My Students' criteria are properly translated."""
        fake_auth.login(coe_advisor_uid)
        post_data = {
            'criteria': {
                'cohortOwnerAcademicPlans': ['*'],
            },
            'ownerUid': coe_advisor_uid,
        }
        api_json = self._api_translate_to_filter_options(client, data=post_data)
        assert len(api_json) == 1
        assert api_json[0]['label']['primary'] == 'My Students'
        assert api_json[0]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[0]['value'] == '*'

    def test_translate_criteria_my_students_for_not_me(self, client, fake_auth):
        """Another user's 'My Students' criteria are properly translated."""
        fake_auth.login(coe_advisor_uid)
        post_data = {
            'criteria': {'cohortOwnerAcademicPlans': ['25I039U', '25I054U']},
            'ownerUid': asc_advisor_uid,
        }
        api_json = self._api_translate_to_filter_options(client, data=post_data)
        assert len(api_json) == 2
        assert api_json[0]['label']['primary'] == 'My Students'
        assert api_json[0]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[0]['value'] == '25I039U'
        assert api_json[1]['label']['primary'] == 'My Students'
        assert api_json[1]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[1]['value'] == '25I054U'
