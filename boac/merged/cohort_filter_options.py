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

from copy import copy, deepcopy

from boac.api.util import authorized_users_api_feed
from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, COE_ETHNICITIES_PER_CODE, current_term_id, term_name_for_sis_id
from boac.merged import athletics
from boac.merged.calnet import get_csid_for_uid
from boac.merged.student import get_student_query_scope
from boac.models.authorized_user import AuthorizedUser
from flask import current_app as app
from flask_login import current_user


def translate_to_filter_options(owner_uid, criteria=None):
    # Transform cohort filter criteria in the database to a UX-compatible data structure.
    rows = []
    if criteria:
        for category in _get_filter_options(get_student_query_scope(), owner_uid):
            for filter_option in category:
                selected = criteria.get(filter_option['key'])
                if selected is not None:
                    def _append_row(value):
                        clone = deepcopy(filter_option)
                        row = {k: clone.get(k) for k in ['key', 'label', 'options', 'type', 'validation']}
                        row['value'] = value
                        rows.append(row)
                    filter_type = filter_option['type']['db']
                    if filter_type == 'string[]':
                        all_options = filter_option.get('options')
                        for selection in selected:
                            value = next((o.get('value') for o in all_options if o.get('value') == selection), None)
                            if value:
                                _append_row(value)
                    elif filter_type == 'boolean':
                        _append_row(selected)
                    elif filter_type == 'json[]':
                        for obj in selected:
                            _append_row(copy(obj))
                    else:
                        raise ValueError(f'Unrecognized filter_type "{filter_type}"')
    return rows


def get_cohort_filter_options(owner_uid, existing_filters=()):
    # Disable filter options based on existing cohort criteria.
    cohort_filter_options = _get_filter_options(get_student_query_scope(), owner_uid)
    cohort_filter_per_key = {}
    filter_type_per_key = {}
    for category in cohort_filter_options:
        for _filter in category:
            _key = _filter['key']
            cohort_filter_per_key[_key] = _filter
            filter_type_per_key[_key] = _filter['type']['db']

    selected_values_per_key = {}
    for existing_filter in existing_filters:
        key = existing_filter['key']
        if key not in selected_values_per_key:
            selected_values_per_key[key] = []
        value = True if filter_type_per_key[key] == 'boolean' else existing_filter['value']
        selected_values_per_key[key].append(value)

    for key, selected_values in selected_values_per_key.items():
        # Disable options that are represented in 'existing_filters'
        cohort_filter = cohort_filter_per_key[key]
        if cohort_filter['type']['ux'] == 'boolean':
            cohort_filter['disabled'] = True
        if cohort_filter['type']['ux'] == 'dropdown':
            # Populate dropdown
            selected_values = selected_values_per_key[key]
            available_options = cohort_filter['options']
            if len(available_options) - len(selected_values) == 0:
                # This filter has zero available options.
                cohort_filter['disabled'] = True
                for option in available_options:
                    option['disabled'] = True
            else:
                for option in available_options:
                    if option.get('value') in selected_values:
                        # Disable option
                        option['disabled'] = True
    return cohort_filter_options


def _get_filter_options(scope, cohort_owner_uid):
    all_dept_codes = list(BERKELEY_DEPT_CODE_TO_NAME.keys())
    categories = [
        [
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'enteringTerms',
                'label': {
                    'primary': 'Entering Term',
                },
                'options': _entering_terms,
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'expectedGradTerms',
                'label': {
                    'primary': 'Expected Graduation Term',
                },
                'options': _grad_terms,
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'gpaRanges',
                'options': None,
                'label': {
                    'primary': 'GPA',
                    'range': ['', '-'],
                    'rangeMinEqualsMax': '',
                },
                'type': {
                    'db': 'json[]',
                    'ux': 'range',
                },
                'validation': 'gpa',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'levels',
                'label': {
                    'primary': 'Level',
                },
                'options': [
                    {'name': 'Freshman (0-29 Units)', 'value': 'Freshman'},
                    {'name': 'Sophomore (30-59 Units)', 'value': 'Sophomore'},
                    {'name': 'Junior (60-89 Units)', 'value': 'Junior'},
                    {'name': 'Senior (90+ Units)', 'value': 'Senior'},
                ],
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'majors',
                'label': {
                    'primary': 'Major',
                },
                'options': _majors,
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'midpointDeficient',
                'label': {
                    'primary': 'Midpoint Deficient Grade',
                },
                'type': {
                    'db': 'boolean',
                    'ux': 'boolean',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'transfer',
                'label': {
                    'primary': 'Transfer Student',
                },
                'type': {
                    'db': 'boolean',
                    'ux': 'boolean',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'unitRanges',
                'label': {
                    'primary': 'Units Completed',
                },
                'options': [
                    {'name': '0 - 29', 'value': 'numrange(NULL, 30, \'[)\')'},
                    {'name': '30 - 59', 'value': 'numrange(30, 60, \'[)\')'},
                    {'name': '60 - 89', 'value': 'numrange(60, 90, \'[)\')'},
                    {'name': '90 - 119', 'value': 'numrange(90, 120, \'[)\')'},
                    {'name': '120 +', 'value': 'numrange(120, NULL, \'[)\')'},
                ],
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
        ],
        [
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'ethnicities',
                'label': {
                    'primary': 'Ethnicity',
                },
                'options': _ethnicities,
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'genders',
                'label': {
                    'primary': 'Gender',
                },
                'options': _genders,
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'underrepresented',
                'label': {
                    'primary': 'Underrepresented Minority',
                },
                'type': {
                    'db': 'boolean',
                    'ux': 'boolean',
                },
            },
        ],
        [
            {
                'availableTo': ['UWASC'],
                'defaultValue': False if 'UWASC' in scope else None,
                'key': 'isInactiveAsc',
                'label': {
                    'primary': 'Inactive (ASC)',
                },
                'type': {
                    'db': 'boolean',
                    'ux': 'boolean',
                },
            },
            {
                'availableTo': ['UWASC'],
                'defaultValue': None,
                'key': 'inIntensiveCohort',
                'label': {
                    'primary': 'Intensive',
                },
                'type': {
                    'db': 'boolean',
                    'ux': 'boolean',
                },
            },
            {
                'availableTo': ['UWASC'],
                'defaultValue': None,
                'key': 'groupCodes',
                'label': {
                    'primary': 'Team',
                },
                'options': _team_groups,
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
        ],
        [
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coeAdvisorLdapUids',
                'label': {
                    'primary': 'Advisor (COE)',
                },
                'options': _get_coe_profiles,
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coeEthnicities',
                'label': {
                    'primary': 'Ethnicity (COE)',
                },
                'options': _coe_ethnicities,
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coeGenders',
                'label': {
                    'primary': 'Gender (COE)',
                },
                'options': [
                    {'name': 'Female', 'value': 'F'},
                    {'name': 'Male', 'value': 'M'},
                ],
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': False if 'COENG' in scope else None,
                'key': 'isInactiveCoe',
                'label': {
                    'primary': 'Inactive (COE)',
                },
                'type': {
                    'db': 'boolean',
                    'ux': 'boolean',
                },
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'lastNameRanges',
                'label': {
                    'primary': 'Last Name',
                    'range': ['Initials', 'through'],
                    'rangeMinEqualsMax': 'Starts with',
                },
                'type': {
                    'db': 'json[]',
                    'ux': 'range',
                },
                'validation': 'char',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'cohortOwnerAcademicPlans',
                'label': {
                    'primary': 'My Students',
                },
                'options': _academic_plans_for_cohort_owner(cohort_owner_uid),
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coePrepStatuses',
                'label': {
                    'primary': 'PREP',
                },
                'options': [
                    {'name': 'PREP', 'value': 'did_prep'},
                    {'name': 'PREP eligible', 'value': 'prep_eligible'},
                    {'name': 'T-PREP', 'value': 'did_tprep'},
                    {'name': 'T-PREP eligible', 'value': 'tprep_eligible'},
                ],
                'type': {
                    'db': 'string[]',
                    'ux': 'dropdown',
                },
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coeProbation',
                'label': {
                    'primary': 'Probation',
                },
                'type': {
                    'db': 'boolean',
                    'ux': 'boolean',
                },
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coeUnderrepresented',
                'label': {
                    'primary': 'Underrepresented Minority (COE)',
                },
                'type': {
                    'db': 'boolean',
                    'ux': 'boolean',
                },
            },
        ],
    ]
    available_categories = []

    def is_available(d):
        available = 'ADMIN' in scope or next((dept_code for dept_code in d['availableTo'] if dept_code in scope), False)
        if available and 'options' in d:
            # If it is available then populate menu options
            options = d.pop('options')
            d['options'] = options() if callable(options) else options
        return available

    for category in categories:
        available_categories.append(list(filter(lambda d: is_available(d), category)))
    # Remove unavailable (ie, empty) categories
    return list(filter(lambda g: len(g), available_categories))


def _get_coe_profiles():
    users = list(filter(lambda _user: 'COENG' in _get_dept_codes(_user), AuthorizedUser.get_all_active_users()))
    profiles = []
    for user in authorized_users_api_feed(users):
        uid = user['uid']
        first_name = user.get('firstName')
        last_name = user.get('lastName')
        name = f'{first_name} {last_name}' if first_name or last_name else f'UID: {uid}'
        profiles.append({'name': name, 'value': uid})
    return sorted(profiles, key=lambda p: p['name'])


def _academic_plans_for_cohort_owner(owner_uid):
    if owner_uid:
        owner_csid = get_csid_for_uid(app, owner_uid)
    else:
        owner_csid = current_user.get_csid()
    plans = [
        {'name': 'All plans', 'value': '*'},
    ]
    plan_results = data_loch.get_academic_plans_for_advisor(owner_csid)
    for row in plan_results:
        value = row['academic_plan_code']
        if value:
            plans.append({'name': row['academic_plan'], 'value': value})
    return plans


def _entering_terms():
    term_ids = [r['entering_term'] for r in data_loch.get_entering_terms()]
    return [{'name': ' '.join(term_name_for_sis_id(term_id).split()[::-1]), 'value': term_id} for term_id in term_ids]


def _ethnicities():
    return [{'name': row['ethnicity'], 'value': row['ethnicity']} for row in data_loch.get_distinct_ethnicities()]


def _genders():
    return [{'name': row['gender'], 'value': row['gender']} for row in data_loch.get_distinct_genders()]


def _grad_terms():
    term_ids = [r['expected_grad_term'] for r in data_loch.get_expected_graduation_terms()]
    terms = [{'name': ' '.join(term_name_for_sis_id(term_id).split()[::-1]), 'value': term_id} for term_id in term_ids]
    first_previous_term_index = next((i for i, term in enumerate(terms) if term['value'] < current_term_id()), None)
    terms.insert(first_previous_term_index, {'name': 'divider', 'value': 'divider'})
    return terms


def _coe_ethnicities():
    rows = data_loch.get_coe_ethnicity_codes(['COENG'])
    key = 'ethnicity_code'

    def ethnicity(code):
        return COE_ETHNICITIES_PER_CODE.get(code)
    coe_ethnicities = [{'name': ethnicity(row[key]), 'value': row[key]} for row in rows]
    return sorted(coe_ethnicities, key=lambda e: e['name'])


def _team_groups():
    rows = athletics.all_team_groups()
    return [{'name': row['groupName'], 'value': row['groupCode']} for row in rows]


def _majors():
    major_results = [row['major'] for row in data_loch.get_majors()]
    return [{'name': major, 'value': major} for major in major_results]


def _get_dept_codes(user):
    return [m.university_dept.dept_code for m in user.department_memberships] if user else None
