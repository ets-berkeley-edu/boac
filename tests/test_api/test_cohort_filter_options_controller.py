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
    def _api_cohort_filter_options(cls, client, data, expected_status_code=200):
        response = client.post(
            '/api/cohort_filter_options',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_filter_options_api_not_authenticated(self, client):
        """Menu API cohort-filter-options requires authentication."""
        self._api_cohort_filter_options(client, data={}, expected_status_code=401)

    def test_filter_options_with_nothing_disabled(self, client, fake_auth):
        """Menu API with all menu options available."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_cohort_filter_options(
            client,
            data={'existingFilters': [], 'ownerUid': coe_advisor_uid},
        )
        for label, option_group in api_json.items():
            for entry in option_group:
                assert 'disabled' not in entry
                if entry['type']['ux'] == 'dropdown':
                    for option in entry['options']:
                        assert 'disabled' not in option

    def test_filter_options_for_guest_user(self, user_factory, client, fake_auth):
        """Filter options available to GUEST user."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': advisor.uid})
        assert len(api_json)
        assert 'options' in list(api_json.values())[0][0]

    def test_filter_options_for_user_of_type_other(self, user_factory, client, fake_auth):
        """Filter options available to ZZZZZ user."""
        advisor = user_factory(dept_codes=['ZZZZZ'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': advisor.uid})
        assert len(api_json)
        assert 'options' in list(api_json.values())[0][0]

    def test_filter_options_my_students_for_me(self, client, fake_auth):
        """Returns user's own academic plans under 'My Students'."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': coe_advisor_uid})
        my_students = next(opt for label, group in api_json.items() for opt in group if opt['label']['primary'] == 'My Students')
        assert len(my_students['options']) == 5
        assert {'name': 'All plans', 'value': '*'} in my_students['options']
        assert {'name': 'Bioengineering BS', 'value': '16288U'} in my_students['options']
        assert {'name': 'Engineering Undeclared UG', 'value': '162B0U'} in my_students['options']
        assert {'name': 'BioE/MSE Joint Major BS', 'value': '162B3U'} in my_students['options']
        assert {'name': 'Bioengineering UG', 'value': '16I010U'} in my_students['options']

    def test_filter_options_my_students_for_not_me(self, client, fake_auth):
        """Returns another user's academic plans under 'My Students'."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': asc_advisor_uid})
        my_students = next(opt for label, group in api_json.items() for opt in group if opt['label']['primary'] == 'My Students')
        assert len(my_students['options']) == 4
        assert {'name': 'All plans', 'value': '*'} in my_students['options']
        assert {'name': 'English BA', 'value': '25345U'} in my_students['options']
        assert {'name': 'English UG', 'value': '25I039U'} in my_students['options']
        assert {'name': 'Medieval Studies UG', 'value': '25I054U'} in my_students['options']

    def test_filter_options_with_category_disabled(self, client, fake_auth):
        """The transfer option is disabled if it is in existing-filters."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_cohort_filter_options(
            client,
            data={'existingFilters': [{'key': 'transfer', 'value': True}], 'ownerUid': coe_advisor_uid},
        )
        assert len(api_json.keys())
        for label, option_group in api_json.items():
            for entry in option_group:
                if entry['key'] == 'transfer':
                    assert entry['disabled'] is True
                else:
                    assert 'disabled' not in entry

    def test_filter_options_with_one_disabled(self, client, fake_auth):
        """The 'Freshman' sub-menu option is disabled if it is already in cohort filter set."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_cohort_filter_options(
            client,
            data={
                'existingFilters': [
                    {'key': 'levels', 'value': 'Freshman'},
                    {'key': 'levels', 'value': 'Sophomore'},
                    {'key': 'levels', 'value': 'Junior'},
                    {'key': 'coeAdvisorLdapUids', 'value': '1022796'},
                ],
                'ownerUid': coe_advisor_uid,
            },
        )
        assert len(api_json.keys())
        assertion_count = 0
        for label, opt_group in api_json.items():
            for entry in opt_group:
                # All top-level category menus are enabled
                assert 'disabled' not in entry
                if entry['key'] == 'levels':
                    for option in entry['options']:
                        disabled = option.get('disabled')
                        if option['value'] in ['Freshman', 'Sophomore', 'Junior']:
                            assert disabled is True
                            assertion_count += 1
                        else:
                            assert disabled is None
                else:
                    assert 'disabled' not in entry
        assert assertion_count == 3

    def test_all_options_in_category_disabled(self, client, fake_auth):
        """Disable the category if all its options are in existing-filters."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_cohort_filter_options(
            client,
            data={
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
            },
        )
        for label, option_group in api_json.items():
            for entry in option_group:
                if entry['key'] == 'cohortOwnerAcademicPlans':
                    assert entry.get('disabled') is True
                elif entry['key'] == 'levels':
                    assert entry.get('disabled') is True
                    for option in entry['options']:
                        assert option.get('disabled') is True
                elif entry['key'] == 'visaTypes':
                    assert entry.get('disabled') is True
                else:
                    assert 'disabled' not in entry

    def test_range_of_entering_terms(self, user_factory, client, fake_auth):
        """Cohort filter: Range of entering terms."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': advisor.uid})
        entering_terms_filter = next((f for f in api_json['Academic'] if f['key'] == 'enteringTerms'), None)
        assert entering_terms_filter
        filter_options = entering_terms_filter.get('options')
        assert len(filter_options) == 4
        assert [o['name'] for o in filter_options] == ['2015 Fall', '2015 Summer', '2015 Spring', '1993 Fall']

    def test_range_of_expected_grad_terms(self, user_factory, client, fake_auth):
        """Cohort filter: Range of expected grad terms."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': advisor.uid})
        entering_terms_filter = next((f for f in api_json['Academic'] if f['key'] == 'expectedGradTerms'), None)
        assert entering_terms_filter
        filter_options = entering_terms_filter.get('options')
        assert len(filter_options['Past']) == 1
        assert filter_options['Past'][0]['name'] == '1997 Fall'

    def test_range_of_majors(self, user_factory, client, fake_auth):
        """Cohort filter: Range of major terms."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': advisor.uid})
        majors_filter = next((f for f in api_json['Academic'] if f['key'] == 'majors'), None)
        assert {'name': 'Chemistry BS', 'value': 'Chemistry BS'} in majors_filter['options']
        assert {'name': 'Nuclear Engineering BS', 'value': 'Nuclear Engineering BS'} in majors_filter['options']
        assert {'name': 'Mathematics PhD', 'value': 'Mathematics PhD'} not in majors_filter['options']

    def test_range_of_graduate_programs(self, user_factory, client, fake_auth):
        """Cohort filter: Range of graduate programs."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': advisor.uid})
        majors_filter = next((f for f in api_json['Academic'] if f['key'] == 'graduatePrograms'), None)
        assert len(majors_filter['options']) == 1
        assert majors_filter['options'][0] == {'name': 'Mathematics PhD', 'value': 'Mathematics PhD'}

    def test_no_curated_group_options(self, client, fake_auth):
        """User with no curated groups gets no cohort filter option where key='curatedGroupIds'."""
        fake_auth.login(asc_and_coe_advisor_uid)
        user_id = AuthorizedUser.get_id_per_uid(asc_and_coe_advisor_uid)
        assert not CuratedGroup.get_curated_groups(user_id)
        api_json = self._api_cohort_filter_options(client, data={'existingFilters': [], 'ownerUid': asc_and_coe_advisor_uid})
        verified = False
        for label, option_group in api_json.items():
            for filter_ in option_group:
                if filter_['key'] == 'curatedGroupIds':
                    assert filter_['disabled'] is True
                    verified = True
        assert verified

    def test_invalid_domain_value(self, user_factory, client, fake_auth):
        """Cohort filter: Invalid domain value."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        self._api_cohort_filter_options(
            client,
            expected_status_code=400,
            data={
                'domain': 'this_is_an_invalid_domain',
                'existingFilters': [],
                'ownerUid': advisor.uid,
            },
        )

    def test_admitted_students_domain_denied(self, user_factory, client, fake_auth):
        """Cohort filter: Denied access to Admitted students."""
        advisor = user_factory(dept_codes=['GUEST'])
        fake_auth.login(advisor.uid)
        self._api_cohort_filter_options(
            client,
            expected_status_code=404,
            data={
                'domain': 'admitted_students',
                'existingFilters': [],
                'ownerUid': advisor.uid,
            },
        )

    def test_admitted_students_domain(self, client, fake_auth):
        """Cohort filter: Admitted students."""
        fake_auth.login(ce3_advisor_uid)
        api_json = self._api_cohort_filter_options(
            client,
            data={
                'domain': 'admitted_students',
                'existingFilters': [],
                'ownerUid': ce3_advisor_uid,
            },
        )
        assert len(api_json)
        for label, option_group in api_json.items():
            for entry in option_group:
                # Verify the 'default' filters are not present.
                assert entry['key'] != 'unitRanges'
                assert entry['domain'] == 'admitted_students'


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
        assert self._api_translate_to_filter_options(
            client,
            data={
                'criteria': {},
                'ownerUid': coe_advisor_uid,
            },
        ) == []

    def test_translate_criteria_with_boolean(self, client, fake_auth):
        """Filter-criteria with boolean is properly translated."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_translate_to_filter_options(
            client,
            data={'criteria': {'isInactiveCoe': False}, 'ownerUid': coe_advisor_uid},
        )
        assert len(api_json) == 1
        assert api_json[0]['label']['primary'] == 'Inactive (COE)'
        assert api_json[0]['key'] == 'isInactiveCoe'
        assert api_json[0]['value'] is False

    def test_translate_criteria_with_array(self, client, fake_auth):
        """Filter-criteria with array is properly translated."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_translate_to_filter_options(
            client,
            data={
                'criteria': {
                    'levels': ['Freshman', 'Sophomore'],
                    'majors': ['Chemistry BS', 'Nuclear Engineering BS'],
                },
                'ownerUid': coe_advisor_uid,
            },
        )
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
        api_json = self._api_translate_to_filter_options(
            client,
            data={
                'criteria': {
                    'lastNameRanges': last_name_ranges,
                },
                'ownerUid': coe_advisor_uid,
            },
        )
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
        api_json = self._api_translate_to_filter_options(
            client,
            data={
                'criteria': {
                    'cohortOwnerAcademicPlans': ['*'],
                },
                'ownerUid': coe_advisor_uid,
            },
        )
        assert len(api_json) == 1
        assert api_json[0]['label']['primary'] == 'My Students'
        assert api_json[0]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[0]['value'] == '*'

    def test_translate_criteria_my_students_for_not_me(self, client, fake_auth):
        """Another user's 'My Students' criteria are properly translated."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_translate_to_filter_options(
            client,
            data={
                'criteria': {'cohortOwnerAcademicPlans': ['25I039U', '25I054U']},
                'ownerUid': asc_advisor_uid,
            },
        )
        assert len(api_json) == 2
        assert api_json[0]['label']['primary'] == 'My Students'
        assert api_json[0]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[0]['value'] == '25I039U'
        assert api_json[1]['label']['primary'] == 'My Students'
        assert api_json[1]['key'] == 'cohortOwnerAcademicPlans'
        assert api_json[1]['value'] == '25I054U'
