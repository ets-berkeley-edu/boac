"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


from boac.api.util import authorized_users_api_feed
from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_NAME_TO_CODE, COE_ETHNICITIES_PER_CODE, get_dept_codes
from boac.merged import athletics
from boac.merged.student import get_student_query_scope
from boac.models.authorized_user import AuthorizedUser


def get_cohort_filter_definitions(scope):
    all_dept_codes = list(BERKELEY_DEPT_NAME_TO_CODE.values())
    categories = [
        [
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'gpaRanges',
                'name': 'GPA',
                'options': _gpa_ranges,
                'param': 'gpa',
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
                'param': 'level',
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'unitRanges',
                'name': 'Units Completed',
                'options': _unit_ranges,
                'param': 'units',
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'majors',
                'name': 'Major',
                'options': _majors,
                'param': 'major',
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
                'param': 'ethnicity',
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'genders',
                'name': 'Gender',
                'options': _genders,
                'param': 'gender',
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'underrepresented',
                'name': 'Underrepresented Minority',
                'options': [True, False],
                'param': 'underrepresented',
                'type': 'boolean',
            },
        ],
        [
            {
                'availableTo': ['UWASC'],
                'defaultValue': False if 'UWASC' in scope else None,
                'key': 'isInactiveAsc',
                'name': 'Inactive',
                'options': [True, False],
                'param': 'inactive',
                'type': 'boolean',
            },
            {
                'availableTo': ['UWASC'],
                'defaultValue': None,
                'key': 'inIntensiveCohort',
                'name': 'Intensive',
                'options': [True, False],
                'param': 'intensive',
                'type': 'boolean',
            },
            {
                'availableTo': ['UWASC'],
                'defaultValue': None,
                'key': 'groupCodes',
                'name': 'Team',
                'options': _team_groups,
                'param': 'team',
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
        ],
        [
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'coePrepStatuses',
                'name': 'PREP',
                'options': _coe_prep_statuses,
                'param': 'prep',
                'subcategoryHeader': 'Choose...',
                'type': 'array',
            },
            {
                'availableTo': all_dept_codes,
                'defaultValue': None,
                'key': 'lastNameRange',
                'name': 'Last Name',
                'options': None,
                'param': 'lastName',
                'subcategoryHeader': ['Initials', 'through'],
                'type': 'range',
            },
            {
                'availableTo': ['COENG'],
                'defaultValue': None,
                'key': 'advisorLdapUids',
                'name': 'Advisor',
                'options': _get_coe_profiles,
                'param': 'advisor',
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


def _get_coe_profiles():
    users = list(filter(lambda user: 'COENG' in get_dept_codes(user), AuthorizedUser.query.all()))
    profiles = []
    for user in authorized_users_api_feed(users):
        uid = user['uid']
        first_name = user.get('firstName')
        last_name = user.get('lastName')
        name = f'{first_name} {last_name}' if first_name or last_name else uid
        profiles.append({'name': name, 'value': uid})
    return sorted(profiles, key=lambda p: p['name'])


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


def _genders():
    return [
        {'name': 'Female', 'value': 'f'},
        {'name': 'Male', 'value': 'm'},
    ]


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
    relevant_majors = [row['major'] for row in data_loch.get_majors(get_student_query_scope())]
    return [{'name': major, 'value': major} for major in relevant_majors]
