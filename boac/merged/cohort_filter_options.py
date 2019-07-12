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

from copy import deepcopy

from boac.api.util import authorized_users_api_feed
from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_NAME_TO_CODE, COE_ETHNICITIES_PER_CODE, term_name_for_sis_id
from boac.merged import athletics
from boac.merged.calnet import get_csid_for_uid
from boac.merged.student import get_student_query_scope
from boac.models.authorized_user import AuthorizedUser
from flask import current_app as app
from flask_login import current_user


def translate_to_filter_options(owner_uid, criteria=None):
    rows = []
    if criteria:
        for definitions in _get_filter_options(get_student_query_scope(), owner_uid):
            for definition in definitions:
                selected = criteria.get(definition['key'])
                if selected is not None:
                    if definition['type'] == 'array':
                        for selection in selected:
                            rows.append(_translate_filter_row(definition, selection))
                    else:
                        rows.append(_translate_filter_row(definition, selected))
    return rows


def get_cohort_filter_options(owner_uid, existing_filters):
    # Default menu has all options available. Options vary with cohort owner since the "My Students" filter includes
    # an list of the cohort owner's academic plans.
    filter_categories = _get_filter_options(get_student_query_scope(), owner_uid)
    menus = [menu for category in filter_categories for menu in category]
    for key in _keys_of_type_boolean(existing_filters):
        # Disable sub_menu options if they are already in cohort criteria
        for menu in menus:
            if menu['key'] == key:
                # Disable 'boolean' sub_menu (e.g., 'isInactiveCoe') if it is already in cohort criteria
                menu['disabled'] = True
    # Get filters of type 'range' (e.g., 'last name')
    for key, values in _selections_of_type('range', existing_filters).items():
        menu = next(s for s in menus if s['key'] == key)
        menu['disabled'] = True
    # Get filters of type 'array' (e.g., 'levels')
    for key, values in _selections_of_type('array', existing_filters).items():
        menu = next(s for s in menus if s['key'] == key)
        if len(values) == len(menu['options']):
            # If count of selected values equals number of options then disable the sub_menu
            menu['disabled'] = True
        for option in menu['options']:
            if option['value'] in values:
                # Disable sub_menu options that are already in cohort criteria
                option['disabled'] = True
    return filter_categories


def _get_filter_options(scope, cohort_owner_uid):
    all_dept_codes = list(BERKELEY_DEPT_NAME_TO_CODE.values())
    categories = [
        [
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'cohortOwnerAcademicPlans',
                'name': 'My Students',
                'options': _academic_plans_for_cohort_owner(cohort_owner_uid),
                'subcategoryHeader': 'Choose academic plan...',
                'type': 'array',
            },
        ],
        [
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'gpaRanges',
                'name': 'GPA',
                'options': _gpa_ranges,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
        ],
        [
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'levels',
                'name': 'Level',
                'options': _class_levels,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'unitRanges',
                'name': 'Units Completed',
                'options': _unit_ranges,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'majors',
                'name': 'Major',
                'options': _majors,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'transfer',
                'name': 'Transfer Student',
                'options': [True, False],
                'subcategoryHeader': 'Choose...',
                'type': 'boolean',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'expectedGradTerms',
                'name': 'Expected Graduation Term',
                'options': _grad_terms,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
        ],
        [
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'ethnicities',
                'name': 'Ethnicity',
                'options': _coe_ethnicities,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coeGenders',
                'name': 'Gender (COE)',
                'options': _coe_genders,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'underrepresented',
                'name': 'Underrepresented Minority',
                'options': [True, False],
                'type': 'boolean',
            },
        ],
        [
            {
                'availableTo': ['UWASC'],
                'defaultValue': False if 'UWASC' in scope else None,
                'key': 'isInactiveAsc',
                'name': 'Inactive' if 'UWASC' in scope else 'Inactive (ASC)',
                'options': [True, False],
                'type': 'boolean',
            },
            {
                'availableTo': ['UWASC'],
                'defaultValue': None,
                'key': 'inIntensiveCohort',
                'name': 'Intensive',
                'options': [True, False],
                'type': 'boolean',
            },
            {
                'availableTo': ['UWASC'],
                'defaultValue': None,
                'key': 'groupCodes',
                'name': 'Team',
                'options': _team_groups,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
        ],
        [
            {
                'availableTo': ['COENG'],
                'defaultValue': False if 'COENG' in scope else None,
                'key': 'isInactiveCoe',
                'name': 'Inactive' if 'COENG' in scope else 'Inactive (COE)',
                'options': [True, False],
                'type': 'boolean',
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coePrepStatuses',
                'name': 'PREP',
                'options': _coe_prep_statuses,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coeProbation',
                'name': 'Probation',
                'options': [True, False],
                'type': 'boolean',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'lastNameRange',
                'name': 'Last Name',
                'options': None,
                'subcategoryHeader': ['Initials', 'through'],
                'type': 'range',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'genders',
                'name': 'Gender',
                'options': _genders,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'advisorLdapUids',
                'name': 'Advisor',
                'options': _get_coe_profiles,
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
        ],
    ]
    available_categories = []

    def is_available(d):
        available = 'ADMIN' in scope or next((dept_code for dept_code in d['availableTo'] if dept_code in scope), False)
        if available:
            # If it is available then populate menu options
            options = d.pop('options')
            d['options'] = options() if callable(options) else options
        return available

    for category in categories:
        available_categories.append(list(filter(lambda d: is_available(d), category)))
    # Remove unavailable (ie, empty) categories
    return list(filter(lambda g: len(g), available_categories))


def _translate_filter_row(definition, selection=None):
    clone = deepcopy(definition)
    row = {k: clone.get(k) for k in ['key', 'name', 'options', 'subcategoryHeader', 'type']}
    if definition['type'] == 'array':
        option = next((o for o in row.get('options', []) if o['value'] == selection), None)
        if option:
            row['value'] = option['value']
    else:
        row['value'] = selection
    return row


def _keys_of_type_boolean(rows):
    # First, get selected 'boolean' options (e.g., 'coeProbation') from cohort criteria.
    existing_boolean_rows = list(filter(lambda row: row['type'] in ['boolean'], rows))
    return list(map(lambda r: r['key'], existing_boolean_rows))


def _selections_of_type(filter_type, existing_filters):
    rows = list(filter(lambda row: row['type'] in [filter_type], existing_filters))
    unique_keys = set(map(lambda row: row['key'], rows))
    selections = dict.fromkeys(unique_keys)
    for row in rows:
        key = row['key']
        if not selections[key]:
            selections[key] = []
        value = row.get('value')
        if value:
            selections[key].append(value)
    return selections


def _get_coe_profiles():
    users = list(filter(lambda _user: 'COENG' in _get_dept_codes(_user), AuthorizedUser.query.all()))
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
            name = row['academic_plan']
        else:
            name = row['[No plan]']
        plans.append({'name': name, 'value': value})
    return plans


def _unit_ranges():
    return [
        {'name': '0 - 29', 'value': 'numrange(NULL, 30, \'[)\')'},
        {'name': '30 - 59', 'value': 'numrange(30, 60, \'[)\')'},
        {'name': '60 - 89', 'value': 'numrange(60, 90, \'[)\')'},
        {'name': '90 - 119', 'value': 'numrange(90, 120, \'[)\')'},
        {'name': '120 +', 'value': 'numrange(120, NULL, \'[)\')'},
    ]


def _class_levels():
    return [
        {'name': 'Freshman (0-29 Units)', 'value': 'Freshman'},
        {'name': 'Sophomore (30-59 Units)', 'value': 'Sophomore'},
        {'name': 'Junior (60-89 Units)', 'value': 'Junior'},
        {'name': 'Senior (90+ Units)', 'value': 'Senior'},
    ]


def _coe_prep_statuses():
    return [
        {'name': 'PREP', 'value': 'did_prep'},
        {'name': 'PREP eligible', 'value': 'prep_eligible'},
        {'name': 'T-PREP', 'value': 'did_tprep'},
        {'name': 'T-PREP eligible', 'value': 'tprep_eligible'},
    ]


def _coe_genders():
    return [
        {'name': 'Female', 'value': 'F'},
        {'name': 'Male', 'value': 'M'},
    ]


def _genders():
    return [{'name': row['gender'], 'value': row['gender']} for row in data_loch.get_distinct_genders()]


def _grad_terms():
    term_ids = [r['expected_grad_term'] for r in data_loch.get_expected_graduation_terms()]
    return [{'name': term_name_for_sis_id(term_id), 'value': term_id} for term_id in term_ids]


def _gpa_ranges():
    return [
        {'name': '3.50 - 4.00', 'value': 'numrange(3.5, 4, \'[]\')'},
        {'name': '3.00 - 3.49', 'value': 'numrange(3, 3.5, \'[)\')'},
        {'name': '2.50 - 2.99', 'value': 'numrange(2.5, 3, \'[)\')'},
        {'name': '2.00 - 2.49', 'value': 'numrange(2, 2.5, \'[)\')'},
        {'name': 'Below 2.0', 'value': 'numrange(0, 2, \'[)\')'},
    ]


def _coe_ethnicities():
    rows = data_loch.get_ethnicity_codes(['COENG'])
    key = 'ethnicity_code'

    def ethnicity(code):
        return COE_ETHNICITIES_PER_CODE.get(code)
    ethnicities = [{'name': ethnicity(row[key]), 'value': row[key]} for row in rows]
    return sorted(ethnicities, key=lambda e: e['name'])


def _team_groups():
    rows = athletics.all_team_groups()
    return [{'name': row['groupName'], 'value': row['groupCode']} for row in rows]


def _majors():
    major_results = [row['major'] for row in data_loch.get_majors()]
    return [{'name': major, 'value': major} for major in major_results]


def _get_dept_codes(user):
    return [m.university_dept.dept_code for m in user.department_memberships] if user else None
