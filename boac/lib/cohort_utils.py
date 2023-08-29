"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac import db
from boac.externals import data_loch
from boac.lib.berkeley import ACADEMIC_STANDING_DESCRIPTIONS, COE_ETHNICITIES_PER_CODE, term_ids_range, term_name_for_sis_id
from boac.merged import athletics
from boac.merged.calnet import get_calnet_users_for_uids
from boac.merged.calnet import get_csid_for_uid
from boac.merged.sis_terms import current_term_id, future_term_id
from boac.models.authorized_user import AuthorizedUser
from boac.models.json_cache import stow
from flask import current_app as app
from flask_login import current_user
from sqlalchemy import text


@stow('cohort_filter_options_coe_profiles')
def get_coe_profiles():
    users = list(filter(lambda _user: 'COENG' in _get_dept_codes(_user), AuthorizedUser.get_all_active_users()))
    calnet_users = get_calnet_users_for_uids(app, [u.uid for u in users])
    profiles = []
    for user in users:
        uid = user.uid
        calnet_user = calnet_users[uid]
        first_name = calnet_user.get('firstName')
        last_name = calnet_user.get('lastName')
        name = f'{first_name} {last_name}' if first_name or last_name else f'UID: {uid}'
        profiles.append({'name': name, 'value': uid})
    return sorted(profiles, key=lambda p: p['name'])


@stow('cohort_filter_options_academic_plans_for_{owner_uid}')
def academic_plans_for_cohort_owner(owner_uid):
    if owner_uid:
        owner_csid = get_csid_for_uid(app, owner_uid)
    else:
        owner_csid = current_user.csid
    plans = [
        {'name': 'All plans', 'value': '*'},
    ]
    plan_results = data_loch.get_academic_plans_for_advisor(owner_csid)
    for row in plan_results:
        value = row['academic_plan_code']
        if value:
            plans.append({'name': row['academic_plan'], 'value': value})
    return plans


def academic_career_status_options():
    return [
        {'name': 'Active', 'value': 'active'},
        {'name': 'Inactive', 'value': 'inactive'},
        {'name': 'Completed', 'value': 'completed'},
    ]


def academic_division_options():
    division_results = [row['division'] for row in data_loch.get_distinct_divisions()]
    return [{'name': division, 'value': division} for division in division_results if division]


@stow('cohort_filter_options_academic_standing')
def academic_standing_options(min_term_id=0):
    option_groups = {}
    for term_id in (r['term_id'] for r in data_loch.get_academic_standing_terms(min_term_id)):
        group = term_name_for_sis_id(term_id)
        option_groups[group] = []
        for value, standing in ACADEMIC_STANDING_DESCRIPTIONS.items():
            option_groups[group].append({
                'name': standing,
                'value': f'{term_id}:{value}',
            })
    return option_groups


def coe_gender_options():
    return [
        {'name': 'Female', 'value': 'F'},
        {'name': 'Male', 'value': 'M'},
    ]


def curated_group_options(user_id):
    results = db.session.execute(
        text("SELECT id, name FROM student_groups WHERE domain='default' AND owner_id = :user_id"),
        {'user_id': user_id},
    )
    return [{'name': row['name'], 'value': row['id']} for row in results]


@stow('cohort_filter_options_colleges')
def colleges():
    college_results = [row['college'] for row in data_loch.get_colleges()]
    return [{'name': college, 'value': college} for college in college_results]


@stow('cohort_filter_options_degree_terms')
def degree_terms():
    term_ids = [r['term_id'] for r in data_loch.get_distinct_degree_term_ids()]
    return [{'name': ' '.join(term_name_for_sis_id(term_id).split()[::-1]), 'value': term_id} for term_id in term_ids]


@stow('cohort_filter_options_degrees')
def degrees():
    return [{'name': row['plan'], 'value': row['plan']} for row in data_loch.get_distinct_degrees()]


@stow('cohort_filter_options_entering_terms')
def entering_terms():
    term_ids = [r['entering_term'] for r in data_loch.get_entering_terms()]
    return [{'name': ' '.join(term_name_for_sis_id(term_id).split()[::-1]), 'value': term_id} for term_id in term_ids]


@stow('cohort_filter_options_ethnicities')
def ethnicities():
    return [{'name': row['ethnicity'], 'value': row['ethnicity']} for row in data_loch.get_distinct_ethnicities()]


@stow('cohort_filter_options_genders')
def genders():
    return [{'name': row['gender'], 'value': row['gender']} for row in data_loch.get_distinct_genders()]


@stow('cohort_filter_options_grad_terms')
def grad_terms():
    current_term_id_ = current_term_id()
    option_groups = {
        'Future': [],
        'Past': [],
    }
    for term_id in [r['expected_grad_term'] for r in data_loch.get_expected_graduation_terms()]:
        key = 'Past' if term_id < current_term_id_ else 'Future'
        option_groups[key].append({
            'name': ' '.join(term_name_for_sis_id(term_id).split()[::-1]),
            'value': term_id,
        })
    return option_groups


@stow('cohort_filter_options_grading_terms')
def grading_terms():
    current_term = current_term_id()
    all_terms = term_ids_range(current_term, future_term_id())

    def _term_option(term_id):
        term_name = term_name_for_sis_id(term_id) + (' (active)' if term_id == current_term else ' (future)')
        return {'name': term_name, 'value': term_id}

    return [_term_option(term_id) for term_id in all_terms]


def incomplete_types():
    return [
        {'name': 'Frozen', 'value': 'frozen'},
        {'name': 'Failing grade, formerly an incomplete', 'value': 'failing'},
        {'name': 'Passing grade, formerly an incomplete', 'value': 'passing'},
        {'name': 'Scheduled to become an F/NP', 'value': 'scheduled'},
    ]


@stow('cohort_filter_options_intended_majors')
def intended_majors():
    intended_major_results = [row['major'] for row in data_loch.get_intended_majors()]
    options = [{'name': major, 'value': major} for major in intended_major_results]
    return list(filter(lambda o: o['value'], options))


def level_options():
    return [
        {'name': 'Freshman (0-29 Units)', 'value': 'Freshman'},
        {'name': 'Sophomore (30-59 Units)', 'value': 'Sophomore'},
        {'name': 'Junior (60-89 Units)', 'value': 'Junior'},
        {'name': 'Senior (90+ Units)', 'value': 'Senior'},
        {'name': 'Masters and/or Professional', 'value': 'Masters/Professional'},
        {'name': 'Doctoral Students Not Advanced to Candidacy', 'value': 'Doctoral Pre-Candidacy'},
        {'name': 'Doctoral Advanced to Candidacy <= 6 Terms', 'value': 'Doctoral Candidate <= 6'},
        {'name': 'Doctoral Advanced to Candidacy > 6 Terms', 'value': 'Doctoral Candidate > 6'},
    ]


@stow('cohort_filter_options_coe_ethnicities')
def coe_ethnicities():
    rows = data_loch.get_coe_ethnicity_codes(['COENG'])
    key = 'ethnicity_code'

    def ethnicity(code):
        return COE_ETHNICITIES_PER_CODE.get(code)
    options = [{'name': ethnicity(row[key]), 'value': row[key]} for row in rows]
    return sorted(options, key=lambda e: e['name'])


def coe_prep_status_options():
    return [
        {'name': 'PREP', 'value': 'did_prep'},
        {'name': 'PREP eligible', 'value': 'prep_eligible'},
        {'name': 'T-PREP', 'value': 'did_tprep'},
        {'name': 'T-PREP eligible', 'value': 'tprep_eligible'},
    ]


def team_groups():
    rows = athletics.all_team_groups()
    return [{'name': row['groupName'], 'value': row['groupCode']} for row in rows]


@stow('cohort_filter_options_majors')
def majors():
    major_results = [row['major'] for row in data_loch.get_majors()]
    return [{'name': major, 'value': major} for major in major_results]


@stow('cohort_filter_options_minors')
def minors():
    minor_results = [row['minor'] for row in data_loch.get_minors()]
    return [{'name': minor, 'value': minor} for minor in minor_results]


@stow('cohort_filter_options_graduate_programs')
def graduate_programs():
    results = [row['major'] for row in data_loch.get_graduate_programs()]
    return [{'name': result, 'value': result} for result in results]


@stow('cohort_filter_options_admit_colleges')
def student_admit_college_options():
    college_results = [row['college'] for row in data_loch.get_admit_colleges()]
    return [{'name': college, 'value': college} for college in college_results]


@stow('cohort_filter_options_admit_ethnicities')
def student_admit_ethnicity_options():
    ethnicity_results = [row['xethnic'] for row in data_loch.get_admit_ethnicities()]
    return [{'name': ethnicity, 'value': ethnicity} for ethnicity in ethnicity_results]


@stow('cohort_filter_options_admit_freshman_or_transfer')
def student_admit_freshman_or_transfer_options():
    freshman_or_transfer_results = [row['freshman_or_transfer'] for row in data_loch.get_admit_freshman_or_transfer()]
    return [{'name': freshman_or_transfer, 'value': freshman_or_transfer} for freshman_or_transfer in freshman_or_transfer_results]


@stow('cohort_filter_options_admit_residency_categories')
def student_admit_residency_category_options():
    residency_category_results = [row['residency_category'] for row in data_loch.get_admit_residency_categories()]
    return [{'name': residency_category, 'value': residency_category} for residency_category in residency_category_results]


@stow('cohort_filter_options_admit_special_program_cep')
def student_admit_special_program_cep_options():
    special_program_cep_results = [row['special_program_cep'] for row in data_loch.get_admit_special_program_cep()]
    return [{'name': special_program_cep, 'value': special_program_cep} for special_program_cep in special_program_cep_results]


def unit_range_options():
    return [
        {'name': '0 - 29', 'value': 'numrange(NULL, 30, \'[)\')'},
        {'name': '30 - 59', 'value': 'numrange(30, 60, \'[)\')'},
        {'name': '60 - 89', 'value': 'numrange(60, 90, \'[)\')'},
        {'name': '90 - 119', 'value': 'numrange(90, 120, \'[)\')'},
        {'name': '120 +', 'value': 'numrange(120, NULL, \'[)\')'},
    ]


@stow('cohort_filter_options_visa_types')
def visa_types():
    other_types = [row['visa_type'] for row in data_loch.get_other_visa_types()]
    return [
        {'name': 'All types', 'value': '*'},
        {'name': 'F-1 International Student', 'value': 'F1'},
        {'name': 'J-1 International Student', 'value': 'J1'},
        {'name': 'Permanent Resident', 'value': 'PR'},
        {'name': 'Other', 'value': ','.join(other_types)},
    ]


def _get_dept_codes(user):
    return [m.university_dept.dept_code for m in user.department_memberships] if user else None
