"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

import pytest
import simplejson as json

admin_uid = '2040'
asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'


@pytest.fixture()
def admin_session(fake_auth):
    fake_auth.login(admin_uid)


@pytest.fixture()
def asc_advisor_session(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor_session(fake_auth):
    fake_auth.login(coe_advisor_uid)


class TestAllCohortFilterOptions:
    """Menu API."""

    @classmethod
    def _post(cls, client, json_data=()):
        return client.post(
            '/api/menu/cohort/all_filter_options',
            data=json.dumps(json_data),
            content_type='application/json',
        )

    @classmethod
    def _level_option(cls, student_class_level):
        return {
            'key': 'levels',
            'type': 'array',
            'value': student_class_level,
        }

    def test_menu_api_not_authenticated(self, client):
        """Menu API cohort-filter-options requires authentication."""
        assert self._post(client).status_code == 401

    def test_menu_with_nothing_disabled(self, client, coe_advisor_session):
        """Menu API with all menu options available."""
        response = self._post(
            client,
            {
                'existingFilters': [],
            },
        )
        assert response.status_code == 200
        for category in response.json:
            for menu in category:
                assert 'disabled' not in menu
                if menu['type'] == 'array':
                    for option in menu['options']:
                        assert 'disabled' not in option

    def test_menu_with_category_disabled(self, client, coe_advisor_session):
        """The coe_probation option is disabled if it is in existing-filters."""
        response = self._post(
            client,
            {
                'existingFilters':
                    [
                        {
                            'key': 'coeProbation',
                            'type': 'boolean',
                        },
                    ],
            },
        )
        assert response.status_code == 200
        filter_categories = response.json
        assert len(filter_categories) == 4
        for category in filter_categories:
            for menu in category:
                if menu['key'] == 'coeProbation':
                    assert menu['disabled'] is True
                else:
                    assert 'disabled' not in menu

    def test_menu_with_disabled_option(self, client, coe_advisor_session):
        """The 'Freshman' sub-menu option is disabled if it is already in cohort filter set."""
        response = self._post(
            client,
            {
                'existingFilters':
                    [
                        self._level_option('Freshman'),
                        self._level_option('Sophomore'),
                        self._level_option('Junior'),
                        {
                            'key': 'advisorLdapUids',
                            'type': 'array',
                            'value': '1022796',
                        },
                    ],
            },
        )
        assert response.status_code == 200
        filter_categories = response.json
        assert len(filter_categories) == 4
        assertion_count = 0
        for category in filter_categories:
            for menu in category:
                # All top-level category menus are enabled
                assert 'disabled' not in menu
                if menu['key'] == 'levels':
                    for option in menu['options']:
                        disabled = option.get('disabled')
                        if option['value'] in ['Freshman', 'Sophomore', 'Junior']:
                            assert disabled is True
                            assertion_count += 1
                        else:
                            assert disabled is None
                else:
                    assert 'disabled' not in menu
        assert assertion_count == 3

    def test_all_options_in_category_disabled(self, client, coe_advisor_session):
        """Disable the category if all its options are in existing-filters."""
        response = self._post(
            client,
            {
                'existingFilters':
                    [
                        self._level_option('Senior'),
                        self._level_option('Junior'),
                        self._level_option('Sophomore'),
                        self._level_option('Freshman'),
                    ],
            },
        )
        assert response.status_code == 200
        for category in response.json:
            for menu in category:
                if menu['key'] == 'levels':
                    assert menu.get('disabled') is True
                    for option in menu['options']:
                        assert option.get('disabled') is True
                else:
                    assert 'disabled' not in menu

    def test_disable_last_name_range(self, client, coe_advisor_session):
        """Disable the category if all its options are in existing-filters."""
        response = self._post(
            client,
            {
                'existingFilters':
                    [
                        {
                            'key': 'lastNameRange',
                            'type': 'range',
                            'value': ['A', 'B'],
                        },
                    ],
            },
        )
        assert response.status_code == 200
        for category in response.json:
            for menu in category:
                is_disabled = menu.get('disabled')
                if menu['key'] == 'lastNameRange':
                    assert is_disabled is True
                else:
                    assert is_disabled is None


class TestCohortFilterTranslate:
    """Menu API."""

    @classmethod
    def _post(cls, client, json_data=()):
        return client.post(
            '/api/menu/cohort/translate_filter_criteria_to_menu',
            data=json.dumps(json_data),
            content_type='application/json',
        )

    def test_translate_criteria_when_empty(self, client, coe_advisor_session):
        """Empty filterCriteria translates to zero rows."""
        response = self._post(client, {'filterCriteria': {}})
        assert response.status_code == 200
        assert json.loads(response.data) == []

    def test_translate_criteria_with_boolean(self, client, coe_advisor_session):
        """Filter-criteria with boolean is properly translated."""
        key = 'isInactiveCoe'
        response = self._post(client, {'filterCriteria': {key: False}})
        assert response.status_code == 200
        rows = json.loads(response.data)
        assert len(rows) == 1
        row = rows[0]
        assert row['name'] == 'Inactive'
        assert row['key'] == key
        assert row['value'] is False

    def test_translate_criteria_with_array(self, client, coe_advisor_session):
        """Filter-criteria with array is properly translated."""
        key = 'levels'
        selected_options = ['Freshman', 'Sophomore']
        response = self._post(client, {'filterCriteria': {key: selected_options}})
        assert response.status_code == 200
        rows = json.loads(response.data)
        assert len(rows) == 2
        assert rows[0]['name'] == rows[1]['name'] == 'Level'
        assert rows[0]['key'] == rows[1]['key'] == key
        assert rows[0]['value'] == 'Freshman'
        assert rows[1]['value'] == 'Sophomore'

    def test_translate_criteria_with_range(self, client, coe_advisor_session):
        """Filter-criteria with range is properly translated."""
        key = 'lastNameRange'
        selected_options = ['M', 'Z']
        response = self._post(client, {'filterCriteria': {key: selected_options}})
        assert response.status_code == 200
        rows = json.loads(response.data)
        assert len(rows) == 1
        row = rows[0]
        assert row['name'] == 'Last Name'
        assert row['key'] == key
        assert row['value'] == selected_options
