"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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
from datetime import datetime

from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, sis_term_id_for_name
from boac.lib.cohort_utils import academic_plans_for_cohort_owner, academic_standing_options, coe_ethnicities, \
    coe_gender_options, coe_prep_status_options, colleges, curated_groups, entering_terms, ethnicities, genders, \
    get_coe_profiles, get_coe_terms, grad_terms, intended_majors, level_options, majors, minors, student_admit_college_options, \
    student_admit_ethnicity_options, student_admit_freshman_or_transfer_options, \
    student_admit_residency_category_options, student_admit_special_program_cep_options, team_groups, \
    unit_range_options, visa_types
from boac.merged.student import get_student_query_scope
from boac.models.authorized_user import AuthorizedUser


class CohortFilterOptions:
    owner_uid = None
    scope = None

    def __init__(self, owner_uid, scope):
        self.owner_uid = owner_uid
        self.scope = scope

    def get_available_filter_option_groups(self, domain, populate_options=True):
        option_groups = {}

        def is_available(d):
            if domain in [d['domain'], '*']:
                available = 'ADMIN' in self.scope or next((dept_code for dept_code in d['availableTo'] if dept_code in self.scope), False)
                if available and populate_options and 'options' in d:
                    # If it is available then populate menu options
                    options = d.pop('options')
                    options = options() if callable(options) else options
                    if d['type']['ux'] == 'dropdown' and not len(options):
                        d['disabled'] = True
                    else:
                        d['options'] = options
                return available
            else:
                return False

        for label, option_group in self.get_filter_option_groups().items():
            options = list(filter(lambda option: is_available(option), option_group))
            if len(options):
                option_groups[label] = options
        return option_groups

    def get_filter_option_groups(self):
        current_year = datetime.now().year
        owner_user_id = AuthorizedUser.get_id_per_uid(self.owner_uid) if self.owner_uid else None
        return {
            'Academic': [
                _filter(
                    'academicStandings',
                    'Academic Standing',
                    options=academic_standing_options(min_term_id=sis_term_id_for_name(f'Fall {current_year - 5}')),
                ),
                _filter('colleges', 'College', options=colleges),
                _filter('enteringTerms', 'Entering Term', options=entering_terms),
                _filter('expectedGradTerms', 'Expected Graduation Term', options=grad_terms),
                _range_filter('gpaRanges', 'GPA (Cumulative)', labels_range=['', '-'], validation='gpa'),
                _range_filter('lastTermGpaRanges', 'GPA (Last Term)', labels_range=['', '-'], validation='gpa'),
                _boolean_filter('studentHolds', 'Holds'),
                _filter('intendedMajors', 'Intended Major', options=intended_majors),
                _filter('levels', 'Level', options=level_options),
                _filter('majors', 'Major', options=majors),
                _filter('minors', 'Minor', options=minors),
                _boolean_filter('midpointDeficient', 'Midpoint Deficient Grade'),
                _boolean_filter('transfer', 'Transfer Student'),
                _filter('unitRanges', 'Units Completed', options=unit_range_options),
            ],
            'Demographics': [
                _filter('ethnicities', 'Ethnicity', options=ethnicities),
                _filter('genders', 'Gender', options=genders),
                _range_filter(
                    'lastNameRanges',
                    'Last Name',
                    labels_range=['Initials', 'through'],
                    label_min_equals_max='Starts with',
                    validation='char',
                ),
                _boolean_filter('underrepresented', 'Underrepresented Minority'),
                _filter('visaTypes', 'Visa Type', options=visa_types),
            ],
            'Departmental (ASC)': [
                _boolean_filter_asc(
                    'isInactiveAsc',
                    'Inactive (ASC)',
                    default_value=False if 'UWASC' in self.scope else None,
                ),
                _boolean_filter('inIntensiveCohort', 'Intensive', available_to=['UWASC']),
                _filter('groupCodes', 'Team', options=team_groups, available_to=['UWASC']),
            ],
            'Departmental (COE)': [
                _filter('coeAdvisorLdapUids', 'Advisor (COE)', options=get_coe_profiles, available_to=['COENG']),
                _filter('coeEpn', 'EPN Grading Option (COE)', options=get_coe_terms, available_to=['COENG']),
                _filter('coeEthnicities', 'Ethnicity (COE)', options=coe_ethnicities, available_to=['COENG']),
                _filter('coeGenders', 'Gender (COE)', options=coe_gender_options, available_to=['COENG']),
                _boolean_filter_coe('isInactiveCoe', 'Inactive (COE)', default_value=False if 'COENG' in self.scope else None),
                _filter('coePrepStatuses', 'PREP', options=coe_prep_status_options, available_to=['COENG']),
                _boolean_filter_coe('coeProbation', 'Probation'),
                _boolean_filter_coe('coeUnderrepresented', 'Underrepresented Minority (COE)'),
            ],
            'Advising': [
                _filter('curatedGroupIds', 'My Curated Groups', options=lambda: curated_groups(owner_user_id) if owner_user_id else None),
                _filter(
                    'cohortOwnerAcademicPlans',
                    'My Students',
                    options=lambda: academic_plans_for_cohort_owner(self.owner_uid) if self.owner_uid else None,
                ),

                _filter(
                    'freshmanOrTransfer',
                    'Freshman or Transfer',
                    options=student_admit_freshman_or_transfer_options,
                    available_to=['ZCEEE'],
                    domain_='admitted_students',
                ),
                _boolean_filter_ce3('sir', 'Current SIR'),
                _filter(
                    'admitColleges',
                    'College',
                    available_to=['ZCEEE'],
                    domain_='admitted_students',
                    options=student_admit_college_options,
                ),
                _filter(
                    'xEthnicities',
                    'XEthnic',
                    available_to=['ZCEEE'],
                    domain_='admitted_students',
                    options=student_admit_ethnicity_options,
                ),
                _boolean_filter_ce3('isHispanic', 'Hispanic'),
                _boolean_filter_ce3('isUrem', 'UREM'),
                _boolean_filter_ce3('isFirstGenerationCollege', 'First Generation College'),
                _boolean_filter_ce3('hasFeeWaiver', 'Application Fee Waiver'),
                _filter(
                    'residencyCategories',
                    'Residency',
                    available_to=['ZCEEE'],
                    domain_='admitted_students',
                    options=student_admit_residency_category_options,
                ),
                _boolean_filter_ce3('inFosterCare', 'Foster Care'),
                _boolean_filter_ce3('isFamilySingleParent', 'Family Is Single Parent'),
                _boolean_filter_ce3('isStudentSingleParent', 'Student Is Single Parent'),
                _range_filter(
                    'familyDependentRanges',
                    'Family Dependents',
                    labels_range=['', '-'],
                    label_min_equals_max='Exactly',
                    available_to=['ZCEEE'],
                    domain_='admitted_students',
                    validation='dependents',
                ),
                _range_filter(
                    'studentDependentRanges',
                    'Student Dependents',
                    labels_range=['', '-'],
                    label_min_equals_max='Exactly',
                    available_to=['ZCEEE'],
                    domain_='admitted_students',
                    validation='dependents',
                ),
                _boolean_filter_ce3('isReentry', 'Re-entry Status'),
                _boolean_filter_ce3('isLastSchoolLCFF', 'Last School LCFF+'),
                _filter(
                    'specialProgramCep',
                    'Special Program CEP',
                    available_to=['ZCEEE'],
                    domain_='admitted_students',
                    options=student_admit_special_program_cep_options,
                ),
            ],
        }

    @classmethod
    def translate_to_filter_options(cls, owner_uid, domain, criteria=None):
        # Transform cohort filter criteria in the database to a UX-compatible data structure.
        rows = []
        if criteria:
            option_groups = cls(owner_uid, get_student_query_scope()).get_available_filter_option_groups(domain)
            for label, option_group in option_groups.items():
                for option in option_group:
                    selected = criteria.get(option['key'])
                    if selected is not None:
                        def _append_row(value_):
                            clone = deepcopy(option)
                            row = {k: clone.get(k) for k in ['key', 'label', 'options', 'type', 'validation']}
                            row['value'] = value_
                            rows.append(row)
                        filter_type = option['type']['db']
                        if filter_type == 'string[]':
                            all_options = option.get('options')
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

    @classmethod
    def get_cohort_filter_option_groups(cls, owner_uid, domain, existing_filters=()):
        # Disable filter options based on existing cohort criteria.
        option_groups = cls(owner_uid, get_student_query_scope()).get_available_filter_option_groups(domain)
        cohort_filter_per_key = {}
        filter_type_per_key = {}
        for label, option_group in option_groups.items():
            for option in option_group:
                _key = option['key']
                cohort_filter_per_key[_key] = option
                filter_type_per_key[_key] = option['type']['db']

        selected_values_per_key = {}
        for existing_filter in existing_filters:
            key = existing_filter['key']
            if key not in selected_values_per_key:
                selected_values_per_key[key] = []
            value = True if filter_type_per_key[key] == 'boolean' else existing_filter['value']
            selected_values_per_key[key].append(value)

        cls.populate_cohort_filter_options(cohort_filter_per_key, selected_values_per_key)
        return option_groups

    @classmethod
    def populate_cohort_filter_options(cls, cohort_filter_per_key, selected_values_per_key):
        for key, selected_values in selected_values_per_key.items():
            # Disable options that are represented in 'existing_filters'
            cohort_filter = cohort_filter_per_key[key]
            if cohort_filter['type']['ux'] == 'boolean':
                cohort_filter['disabled'] = True
            if cohort_filter['type']['ux'] == 'dropdown':
                # Populate dropdown
                selected_values = selected_values_per_key[key]
                available_options = cohort_filter['options']
                if len(available_options) == len(selected_values):
                    # This filter has zero available options.
                    cohort_filter['disabled'] = True
                    for option in available_options:
                        option['disabled'] = True
                else:
                    for option in available_options:
                        if option.get('value') in selected_values:
                            # Disable option
                            option['disabled'] = True
                # When a filter value is 'Select all', don't allow a new filter to be created, but leave other
                # options available so that existing filters can be edited.
                if '*' in selected_values:
                    cohort_filter['disabled'] = True


def _filter(
        key,
        label_primary,
        type_db='string[]',
        type_ux='dropdown',
        available_to=None,
        default_value=None,
        domain_='default',
        label_min_equals_max='',
        labels_range=None,
        options=None,
        validation=None,
):
    return {
        'availableTo': available_to or tuple(BERKELEY_DEPT_CODE_TO_NAME.keys()),
        'defaultValue': default_value,
        'domain': domain_,
        'key': key,
        'label': {
            'primary': label_primary,
            'range': labels_range,
            'rangeMinEqualsMax': label_min_equals_max,
        },
        'options': options,
        'type': {
            'db': type_db,
            'ux': type_ux,
        },
        'validation': validation,
    }


def _boolean_filter(
        key,
        label_primary,
        default_value=None,
        domain_='default',
        available_to=None,
):
    return _filter(
        key,
        label_primary,
        type_db='boolean',
        type_ux='boolean',
        default_value=default_value,
        domain_=domain_,
        available_to=available_to,
    )


def _boolean_filter_asc(key, label_primary, default_value=None, domain_='default'):
    return _filter(
        key,
        label_primary,
        type_db='boolean',
        type_ux='boolean',
        default_value=default_value,
        domain_=domain_,
        available_to=['UWASC'],
    )


def _boolean_filter_ce3(key, label_primary, default_value=None):
    return _filter(
        key,
        label_primary,
        type_db='boolean',
        type_ux='boolean',
        default_value=default_value,
        domain_='admitted_students',
        available_to=['ZCEEE'],
    )


def _boolean_filter_coe(key, label_primary, default_value=None, domain_='default'):
    return _filter(
        key,
        label_primary,
        type_db='boolean',
        type_ux='boolean',
        default_value=default_value,
        domain_=domain_,
        available_to=['COENG'],
    )


def _range_filter(
        key,
        label_primary,
        labels_range,
        label_min_equals_max='',
        domain_='default',
        available_to=None,
        validation=None,
):
    return _filter(
        key,
        label_primary,
        type_db='json[]',
        type_ux='range',
        labels_range=labels_range,
        label_min_equals_max=label_min_equals_max,
        domain_=domain_,
        available_to=available_to,
        validation=validation,
    )
