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

from bea.test_utils import utils
from boac.externals import data_loch
from flask import current_app as app


# SELECT FROM


def select_from(sort=None):
    if sort and (sort['col'] != 'first_name'):
        sort_select = sort_value(sort, 'select')
        select = f', {sort_select}' if sort_select else f", {sort['table']}.{sort['col']}"
    else:
        select = ''
    return f"""SELECT DISTINCT boac_advising_oua.student_admits.cs_empl_id AS sid,
                      LOWER(boac_advising_oua.student_admits.last_name),
                      LOWER(boac_advising_oua.student_admits.first_name){select}
                 FROM boac_advising_oua.student_admits"""


# WHERE


def colleges_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.colleges:
        conditions_list.append(f'boac_advising_oua.student_admits.college IN({utils.in_op(cohort_admit_filter.colleges)})')


def current_sir_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.current_sir:
        conditions_list.append("boac_advising_oua.student_admits.current_sir = 'Yes'")


def family_dependents_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.family_dependents:
        ranges = list(map(lambda r: f"boac_advising_oua.student_admits.family_dependents_num BETWEEN '{r['min']}' AND '{r['max']}'",
                          cohort_admit_filter.family_dependents))
        cond = f"({' OR '.join(ranges)})"
        conditions_list.append(cond)


def family_single_parent_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.family_single_parent:
        conditions_list.append("boac_advising_oua.student_admits.family_is_single_parent = 'Y'")


def fee_waiver_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.fee_waiver:
        conditions_list.append("boac_advising_oua.student_admits.application_fee_waiver_flag = 'FeeWaiver'")


def first_gen_college_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.first_gen_college:
        conditions_list.append("boac_advising_oua.student_admits.first_generation_college = 'Yes'")


def foster_care_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.foster_care:
        conditions_list.append("boac_advising_oua.student_admits.foster_care_flag = 'Y'")


def freshman_or_transfer_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.freshman_or_transfer:
        ary = cohort_admit_filter.freshman_or_transfer
        conditions_list.append(f'boac_advising_oua.student_admits.freshman_or_transfer IN({utils.in_op(ary)})')


def hispanic(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.hispanic:
        conditions_list.append("boac_advising_oua.student_admits.hispanic = 'Y'")


def last_school_lcff_plus_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.last_school_lcff_plus:
        conditions_list.append("boac_advising_oua.student_admits.last_school_lcff_plus_flag = '1'")


def re_entry_status_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.re_entry_status:
        conditions_list.append("boac_advising_oua.student_admits.reentry_status = 'Yes'")


def residency_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.residency:
        ary = cohort_admit_filter.residency
        conditions_list.append(f'boac_advising_oua.student_admits.residency_category IN({utils.in_op(ary)})')


def special_program_cep_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.special_program_cep:
        ary = cohort_admit_filter.special_program_cep
        conditions_list.append(f'boac_advising_oua.student_admits.special_program_cep IN({utils.in_op(ary)})')


def student_dependents_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.student_dependents:
        ranges = list(map(lambda r: f"boac_advising_oua.student_admits.student_dependents_num BETWEEN '{r['min']}' AND '{r['max']}'",
                          cohort_admit_filter.student_dependents))
        cond = f"({' OR '.join(ranges)})"
        conditions_list.append(cond)


def student_single_parent_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.student_single_parent:
        conditions_list.append("boac_advising_oua.student_admits.student_is_single_parent = 'Y'")


def urem_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.urem:
        conditions_list.append("boac_advising_oua.student_admits.urem = 'Yes'")


def xethnic_cond(cohort_admit_filter, conditions_list):
    if cohort_admit_filter.xethnic:
        conditions_list.append(f'boac_advising_oua.student_admits.xethnic IN({utils.in_op(cohort_admit_filter.xethnic)})')


def where(test, cohort_admit_filter):
    conditions_list = []

    # GLOBAL FILTERS
    colleges_cond(cohort_admit_filter, conditions_list)
    current_sir_cond(cohort_admit_filter, conditions_list)
    family_dependents_cond(cohort_admit_filter, conditions_list)
    family_single_parent_cond(cohort_admit_filter, conditions_list)
    fee_waiver_cond(cohort_admit_filter, conditions_list)
    first_gen_college_cond(cohort_admit_filter, conditions_list)
    foster_care_cond(cohort_admit_filter, conditions_list)
    freshman_or_transfer_cond(cohort_admit_filter, conditions_list)
    hispanic(cohort_admit_filter, conditions_list)
    last_school_lcff_plus_cond(cohort_admit_filter, conditions_list)
    re_entry_status_cond(cohort_admit_filter, conditions_list)
    residency_cond(cohort_admit_filter, conditions_list)
    special_program_cep_cond(cohort_admit_filter, conditions_list)
    student_dependents_cond(cohort_admit_filter, conditions_list)
    student_single_parent_cond(cohort_admit_filter, conditions_list)
    urem_cond(cohort_admit_filter, conditions_list)
    xethnic_cond(cohort_admit_filter, conditions_list)

    conditions_list = list(filter(None, conditions_list))
    conditions_list = ' \nAND '.join(conditions_list)
    return f'WHERE {conditions_list}'


# ORDER BY


def sort_value(sort, key):
    try:
        return sort[f'{key}']
    except KeyError:
        return ''


def order_by(sort):
    default_sort = """LOWER(boac_advising_oua.student_admits.last_name),
                      LOWER(boac_advising_oua.student_admits.first_name),
                      boac_advising_oua.student_admits.cs_empl_id ASC"""
    if sort:
        if sort['col'] == 'first_name':
            return """ORDER BY LOWER(boac_advising_oua.student_admits.first_name),
                               LOWER(boac_advising_oua.student_admits.last_name),
                               boac_advising_oua.student_admits.cs_empl_id ASC"""
        elif sort['col'] == 'cs_empl_id':
            return 'ORDRE BY boac_advising_oua.student_admits.cs_empl_id ASC'
    else:
        return f'ORDER BY {default_sort}'


# QUERIES - COHORT LIST VIEW

def get_cohort_result(test, cohort_admit_filter, sort=None):
    sql = f"""{select_from(sort)}
              {where(test, cohort_admit_filter)}
              {order_by(sort)}"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return [r['sid'] for r in results]


# Last Name

def cohort_by_last_name(test, cohort_admit_filter):
    return get_cohort_result(test, cohort_admit_filter)


# First name

def cohort_by_first_name(test, cohort_admit_filter):
    sort = {
        'col': 'first_name',
    }
    return get_cohort_result(test, cohort_admit_filter, sort)


# CS_Empl_ID

def cohort_by_cs_empl_id(test, cohort_admit_filter):
    sort = {
        'col': 'cs_empl_id',
    }
    return get_cohort_result(test, cohort_admit_filter, sort)
