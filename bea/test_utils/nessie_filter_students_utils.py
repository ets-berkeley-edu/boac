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

from bea.models.cohorts_and_groups.cohort_filter import CohortFilter
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
    return f"""SELECT DISTINCT student.student_profile_index.sid,
                      LOWER(student.student_profile_index.last_name),
                      LOWER(student.student_profile_index.first_name){select}
                 FROM student.student_profile_index"""


def previous_term_gpa_sub_query(term):
    return f"""(SELECT student.student_term_gpas.gpa
                FROM student.student_term_gpas
               WHERE student.student_term_gpas.sid = student_profile_index.sid
                 AND student.student_term_gpas.term_id = '{term}'
                 AND student.student_term_gpas.units_taken_for_gpa != '0.0') AS gpa_last_term
            """


def cohort_units_in_prog_sub_query():
    return f"""(SELECT student.student_enrollment_terms.enrolled_units
                FROM student.student_enrollment_terms
               WHERE student.student_enrollment_terms.sid = student_profile_index.sid
                 AND student.student_enrollment_terms.term_id = '{utils.get_current_term().sis_id}') AS units_in_progress
            """


def user_list_units_in_prog_sub_query():
    return f"""COALESCE((SELECT student.student_enrollment_terms.enrolled_units
                           FROM student.student_enrollment_terms
                          WHERE student.student_enrollment_terms.sid = student_profile_index.sid
                            AND student.student_enrollment_terms.term_id = '{utils.get_current_term().sis_id}'), 0) AS units_in_progress
            """


# WHERE


def academic_career_cond(cohort_filter, conditions_list):
    if cohort_filter.academic_careers:
        careers = []
        for career in cohort_filter.academic_careers:
            careers.extend(CohortFilter.colleges_per_career(career))
        conditions_list.append(f'student.student_majors.college IN({utils.in_op(careers)})')


def academic_division_cond(cohort_filter, conditions_list):
    if cohort_filter.academic_divisions:
        conditions_list.append(f'student.student_majors.division IN({utils.in_op(cohort_filter.academic_divisions)})')


def academic_standing_cond(cohort_filter, conditions_list):
    if cohort_filter.academic_standings:
        cond = []
        for term_standing in cohort_filter.academic_standings:
            s = term_standing.split('-')
            cond.append(
                f"(student.academic_standing.term_id = '{s[0]}' AND student.academic_standing.acad_standing_status = '{s[1]}')")
        conditions_list.append(f"({' OR '.join(cond)})")


def career_status_cond(cohort_filter, conditions_list):
    if cohort_filter.career_statuses:
        statuses = list(map(lambda c: c.lower(), cohort_filter.career_statuses))
        if 'inactive' in statuses:
            statuses.append('NULL')
        conditions_list.append(f'student.student_profile_index.academic_career_status IN({utils.in_op(statuses)})')


def college_cond(cohort_filter, conditions_list):
    if cohort_filter.colleges:
        conditions_list.append(f'student.student_majors.college IN ({utils.in_op(cohort_filter.colleges)})')


def degree_awarded_cond(cohort_filter, conditions_list):
    if cohort_filter.degrees_awarded:
        conditions_list.append(f'student.student_degrees.plan IN ({utils.in_op(cohort_filter.degrees_awarded)})')


def degree_term_cond(cohort_filter, conditions_list):
    if cohort_filter.degree_terms:
        conditions_list.append(f'student.student_degrees.term_id IN ({utils.in_op(cohort_filter.degree_terms)})')


def entering_term_cond(cohort_filter, conditions_list):
    if cohort_filter.entering_terms:
        conditions_list.append(
            f'student.student_profile_index.entering_term IN ({utils.in_op(cohort_filter.entering_terms)})')


def expected_grad_term_cond(cohort_filter, conditions_list):
    if cohort_filter.expected_grad_terms:
        conditions_list.append(
            f'student.student_profile_index.expected_grad_term IN ({utils.in_op(cohort_filter.expected_grad_terms)})')


def gpa_cond(cohort_filter, conditions_list):
    if cohort_filter.gpa_ranges:
        ranges = list(
            map(lambda r: f"(student.student_profile_index.gpa BETWEEN {r['min']} AND {r['max']})", cohort_filter.gpa_ranges))
        conditions_list.append(f"({' OR '.join(ranges)})")


def gpa_last_term_cond(cohort_filter, conditions_list):
    if cohort_filter.gpa_ranges_last_term:
        ranges = list(map(lambda r: f"(student.student_term_gpas.gpa BETWEEN {r['min']} AND {r['max']})",
                          cohort_filter.gpa_ranges_last_term))
        cond = f"""student.student_term_gpas.term_id = '{utils.get_prev_term_sis_id()}'
               AND student.student_term_gpas.units_taken_for_gpa != '0.0'
               AND ({' OR '.join(ranges)})"""
        conditions_list.append(cond)


def grading_basis_epn_cond(cohort_filter, conditions_list):
    if cohort_filter.grading_basis_epn:
        epn_conditions_list = f"""student.student_enrollment_terms.term_id IN ({utils.in_op(cohort_filter.grading_basis_epn)})
                          AND (student.student_enrollment_terms.enrollment_term LIKE '%%"gradingBasis": "EPN"%%'
                            OR student.student_enrollment_terms.enrollment_term LIKE '%%"gradingBasis": "CPN"%%')"""
        conditions_list.append(epn_conditions_list)


def incomplete_grade_cond(cohort_filter, conditions_list):
    if cohort_filter.incomplete_grades:
        conditions_list.append("student.student_incompletes.term_id > '2015'")
        options = []
        for grade in cohort_filter.incomplete_grades:
            if grade == 'Frozen':
                options.append('student.student_incompletes.frozen IS TRUE')
            elif grade == 'Failing grade, formerly an incomplete':
                options.append("student.student_incompletes.grade IN ('F', 'NP')")
            elif grade == 'Passing grade, formerly an incomplete':
                options.append(
                    "(student.student_incompletes.status IN ('L', 'R') AND student.student_incompletes.grade NOT IN ('I', 'F', 'NP'))")
            else:
                options.append(
                    "(student.student_incompletes.status = 'I' AND student.student_incompletes.frozen IS FALSE)")
        if options:
            conditions_list.append(f"({' OR '.join(options)})")


def incomplete_sched_cond(cohort_filter, conditions_list):
    if cohort_filter.incomplete_sched_grades:
        ranges = []
        for r in cohort_filter.incomplete_sched_grades:
            ranges.append(f"(student.student_incompletes.lapse_date BETWEEN '{r['min']}' AND '{r['max']}')")
        cond = f"""student.student_incompletes.frozen IS FALSE
               AND student.student_incompletes.status = 'I'
               AND student.student_incompletes.term_id > '2015'
               AND ({' OR '.join(ranges)})"""
        conditions_list.append(cond)


def intended_major_cond(cohort_filter, conditions_list):
    if cohort_filter.intended_majors:
        conditions_list.append(f'student.intended_majors.major IN ({utils.in_op(cohort_filter.intended_majors)})')


def level_cond(cohort_filter, conditions_list):
    if cohort_filter.levels:
        conditions_list.append(f'student.student_profile_index.level IN ({utils.in_op(cohort_filter.levels)})')


def major_cond(cohort_filter, conditions_list):
    majors = []
    if cohort_filter.majors:
        majors.extend(cohort_filter.majors)
    if cohort_filter.graduate_plans:
        majors.extend(cohort_filter.graduate_plans)
    if majors:
        conditions_list.append(f'student.student_majors.major IN ({utils.in_op(majors)})')


def minor_cond(cohort_filter, conditions_list):
    if cohort_filter.minors:
        conditions_list.append(f"""student.minors.minor IN ({utils.in_op(cohort_filter.minors)})
                               AND student.student_profile_index.level != 'GR'
                               AND student.student_majors.college NOT LIKE 'Graduate%%'""")


def midpoint_deficient_cond(cohort_filter, conditions_list):
    if cohort_filter.mid_point_deficient:
        conditions_list.append(f"""student.student_enrollment_terms.midpoint_deficient_grade IS TRUE
                               AND student.student_enrollment_terms.term_id = '{utils.get_current_term().sis_id}'""")


def transfer_cond(cohort_filter, conditions_list):
    if cohort_filter.transfer_student:
        conditions_list.append('student.student_profile_index.transfer IS TRUE')


def units_completed_cond(cohort_filter, conditions_list):
    if cohort_filter.units_completed:
        ranges = []
        for r in cohort_filter.units_completed:
            if '+' in r:
                ranges.append('student.student_profile_index.units >= 120')
            else:
                units_range = r.split('-')
                for i in units_range:
                    i.strip()
                ranges.append(f'(student.student_profile_index.units BETWEEN {units_range[0]} AND {units_range[1]}.999)')
        conditions_list.append(f"({' OR '.join(ranges)})")


def ethnicity_cond(cohort_filter, conditions_list):
    if cohort_filter.ethnicities:
        conditions_list.append(f'student.ethnicities.ethnicity IN ({utils.in_op(cohort_filter.ethnicities)})')


def minority_cond(cohort_filter, conditions_list):
    if cohort_filter.underrepresented_minority:
        conditions_list.append('student.demographics.minority IS TRUE')


def visa_cond(cohort_filter, conditions_list):
    if cohort_filter.visa_types:
        conditions_list.append("student.visas.visa_status = 'G'")
        if 'All types' in cohort_filter.visa_types:
            conditions_list.append('student.visas.visa_type IS NOT NULL')
        else:
            visa_conditions_list = []
            for visa in cohort_filter.visa_types:
                if visa == 'Other':
                    visa_conditions_list.append("student.visas.visa_type NOT IN ('F1', 'J1', 'PR')")
                else:
                    visa_conditions_list.append(f"student.visas.visa_type = '{visa}'")
            visa_conditions_list = ' \nOR '.join(visa_conditions_list)
            if visa_conditions_list:
                conditions_list.append(f'({visa_conditions_list})')


def last_name_cond(cohort_filter, conditions_list):
    if cohort_filter.last_name:
        ranges = []
        for initials in cohort_filter.last_name:
            if initials['min'] == initials['max']:
                ranges.append(f"LOWER(student.student_profile_index.last_name) LIKE '{initials['min']}'%%")
            else:
                ranges.append(
                    f"LOWER(student.student_profile_index.last_name) BETWEEN '{initials['min']}' AND '{initials['max']}zz'")
        conditions_list.append(f"{' OR '.join(ranges)}")


def my_students_cond(cohort_filter, conditions_list, test):
    if cohort_filter.cohort_owner_acad_plans:
        conditions_list.append(f"boac_advisor.advisor_students.advisor_sid = '{test.advisor.sid}'")
        if 'All' not in cohort_filter.cohort_owner_acad_plans:
            conditions_list.append(
                f'boac_advisor.advisor_students.academic_plan_code IN ({utils.in_op(cohort_filter.cohort_owner_acad_plans)})"')


def asc_cond(cohort_filter, conditions_list):
    if cohort_filter.asc_inactive:
        conditions_list.append('boac_advising_asc.students.active IS FALSE')
    if cohort_filter.asc_intensive:
        conditions_list.append('boac_advising_asc.students.intensive IS TRUE')
    if cohort_filter.asc_teams:
        squads = [squad.value['code'] for squad in cohort_filter.asc_teams]
        conditions_list.append(f'boac_advising_asc.students.group_code IN ({utils.in_op(squads)})')


def coe_cond(cohort_filter, conditions_list):
    coe_conditions_list = []
    if cohort_filter.coe_advisors:
        coe_conditions_list.append(
            f'boac_advising_coe.students.advisor_ldap_uid IN ({utils.in_op(cohort_filter.coe_advisors)})')
    if cohort_filter.coe_ethnicities:
        coe_conditions_list.append(
            f'boac_advising_coe.students.ethnicity IN ({utils.in_op(cohort_filter.coe_ethnicities)})')
    if cohort_filter.coe_inactive:
        coe_conditions_list.append("boac_advising_coe.students.status IN ('D', 'O', 'P', 'U', 'W', 'X', 'Z')")
    if cohort_filter.coe_probation:
        coe_conditions_list.append('boac_advising_coe.students.probation IS TRUE')
    if cohort_filter.coe_underrepresented_minority:
        coe_conditions_list.append('boac_advising_coe.students.minority IS TRUE')

    prep_conditions_list = []
    if cohort_filter.coe_preps and 'PREP' in cohort_filter.coe_preps:
        prep_conditions_list.append('boac_advising_coe.students.did_prep IS TRUE')
    if cohort_filter.coe_preps and 'PREP eligible' in cohort_filter.coe_preps:
        prep_conditions_list.append('boac_advising_coe.students.prep_eligible IS TRUE')
    if cohort_filter.coe_preps and 'T-PREP' in cohort_filter.coe_preps:
        prep_conditions_list.append('boac_advising_coe.students.did_tprep IS TRUE')
    if cohort_filter.coe_preps and 'T-PREP eligible' in cohort_filter.coe_preps:
        prep_conditions_list.append('boac_advising_coe.students.tprep_eligible IS TRUE')
    prep_conditions_list = ' \nOR '.join(prep_conditions_list)
    if prep_conditions_list:
        coe_conditions_list.append(f'({prep_conditions_list})')

    if coe_conditions_list and not cohort_filter.coe_inactive:
        coe_conditions_list.append("boac_advising_coe.students.status NOT IN ('D', 'O', 'P', 'U', 'W', 'X', 'Z')")

    for c in coe_conditions_list:
        conditions_list.append(c)


def where(test, cohort_filter):
    conditions_list = []

    # GLOBAL FILTERS
    academic_career_cond(cohort_filter, conditions_list)
    academic_division_cond(cohort_filter, conditions_list)
    academic_standing_cond(cohort_filter, conditions_list)
    career_status_cond(cohort_filter, conditions_list)
    college_cond(cohort_filter, conditions_list)
    degree_awarded_cond(cohort_filter, conditions_list)
    degree_term_cond(cohort_filter, conditions_list)
    entering_term_cond(cohort_filter, conditions_list)
    expected_grad_term_cond(cohort_filter, conditions_list)
    gpa_cond(cohort_filter, conditions_list)
    gpa_last_term_cond(cohort_filter, conditions_list)
    grading_basis_epn_cond(cohort_filter, conditions_list)
    incomplete_grade_cond(cohort_filter, conditions_list)
    incomplete_sched_cond(cohort_filter, conditions_list)
    intended_major_cond(cohort_filter, conditions_list)
    last_name_cond(cohort_filter, conditions_list)
    level_cond(cohort_filter, conditions_list)
    major_cond(cohort_filter, conditions_list)
    minor_cond(cohort_filter, conditions_list)
    midpoint_deficient_cond(cohort_filter, conditions_list)
    transfer_cond(cohort_filter, conditions_list)
    units_completed_cond(cohort_filter, conditions_list)
    ethnicity_cond(cohort_filter, conditions_list)
    minority_cond(cohort_filter, conditions_list)
    visa_cond(cohort_filter, conditions_list)
    my_students_cond(cohort_filter, conditions_list, test)

    # ASC
    asc_cond(cohort_filter, conditions_list)

    # CoE
    coe_cond(cohort_filter, conditions_list)

    conditions_list = list(filter(None, conditions_list))
    conditions_list = ' \nAND '.join(conditions_list)

    if cohort_filter.career_statuses or cohort_filter.degrees_awarded or cohort_filter.degree_terms:
        active_cond = ''
    else:
        active_cond = "student.student_profile_index.academic_career_status = 'active' AND "

    return f'WHERE {active_cond}' + conditions_list


# JOIN

def filter_join_clauses(cohort_filter):
    joins = []
    sid = 'student.student_profile_index.sid'

    if cohort_filter.academic_standings:
        acad_standing_join = f'LEFT JOIN student.academic_standing ON {sid} = student.academic_standing.sid'
        joins.append(acad_standing_join)

    if cohort_filter.degrees_awarded or cohort_filter.degree_terms:
        degree_join = f'LEFT JOIN student.student_degrees ON {sid} = student.student_degrees.sid'
        joins.append(degree_join)

    if (cohort_filter.grading_basis_epn and not cohort_filter.mid_point_deficient) or cohort_filter.incomplete_grades:
        epn_join = f'LEFT JOIN student.student_enrollment_terms ON {sid} = student.student_enrollment_terms.sid'
        joins.append(epn_join)

    if cohort_filter.holds:
        holds_join = f'JOIN student.student_holds ON {sid} = student.student_holds.sid'
        joins.append(holds_join)

    if (cohort_filter.colleges or cohort_filter.majors or cohort_filter.academic_divisions or cohort_filter.graduate_plans
            or cohort_filter.minors or cohort_filter.academic_careers):
        major_join = f'LEFT JOIN student.student_majors ON {sid} = student.student_majors.sid'
        joins.append(major_join)

    if cohort_filter.incomplete_grades or cohort_filter.incomplete_sched_grades:
        incomplete_join = f'JOIN student.student_incompletes ON {sid} = student.student_incompletes.sid'
        joins.append(incomplete_join)

    if cohort_filter.intended_majors:
        intended_major_join = f'LEFT JOIN student.intended_majors ON {sid} = student.intended_majors.sid'
        joins.append(intended_major_join)

    if cohort_filter.minors:
        minor_join = f'LEFT JOIN student.minors ON {sid} = student.minors.sid'
        joins.append(minor_join)

    if cohort_filter.visa_types:
        visa_join = f'LEFT JOIN student.visas ON {sid} = student.visas.sid'
        joins.append(visa_join)

    if cohort_filter.ethnicities:
        ethnicity_join = f'LEFT JOIN student.ethnicities ON {sid} = student.ethnicities.sid'
        joins.append(ethnicity_join)

    if cohort_filter.underrepresented_minority:
        demographics_join = f'LEFT JOIN student.demographics ON {sid} = student.demographics.sid'
        joins.append(demographics_join)

    if cohort_filter.cohort_owner_acad_plans:
        advisor_student_join = f'LEFT JOIN boac_advisor.advisor_students ON {sid} = boac_advisor.advisor_students.student_sid'
        joins.append(advisor_student_join)

    if cohort_filter.mid_point_deficient:
        enroll_term_join = f"""LEFT JOIN student.student_enrollment_terms
                                      ON {sid} = student.student_enrollment_terms.sid
                                     AND student.student_enrollment_terms.term_id = '{utils.get_current_term().sis_id}'"""
        joins.append(enroll_term_join)

    if cohort_filter.gpa_ranges_last_term:
        term_gpa_join = f'LEFT JOIN student.student_term_gpas ON {sid} = student.student_term_gpas.sid'
        joins.append(term_gpa_join)

    if cohort_filter.asc_inactive or cohort_filter.asc_intensive or cohort_filter.asc_teams:
        asc_join = f'LEFT JOIN boac_advising_asc.students ON {sid} = boac_advising_asc.students.sid'
        joins.append(asc_join)

    if (cohort_filter.coe_advisors or cohort_filter.coe_ethnicities or cohort_filter.coe_inactive
            or cohort_filter.coe_preps or cohort_filter.coe_probation or cohort_filter.coe_underrepresented_minority):
        coe_join = f'LEFT JOIN boac_advising_coe.students ON {sid} = boac_advising_coe.students.sid'
        joins.append(coe_join)
    all_joins = list(set(joins))
    return ' \n'.join(all_joins)


def join(cohort_filter_joins, sort=None, opts=None):
    if sort:
        active_clause = 'AND student.student_profile_index.academic_career_status = \'active\''
        join = f"LEFT JOIN {sort['table']} ON student.student_profile_index.sid = {sort['table']}.sid"
        join = '' if join in cohort_filter_joins else join
        if opts and opts['active']:
            join = f'{join} {active_clause}'
        if not (sort['table'] == 'student.student_profile_index') or (join in cohort_filter_joins):
            cohort_filter_joins = cohort_filter_joins + f' {join}'
    return cohort_filter_joins


# GROUP BY

def group_by(sort=None):
    if sort and sort_value(sort, 'group_by') and (sort['col'] != 'first_name'):
        group = f", {sort['table']}.{sort['col']}"
    else:
        group = ''
    return f"""GROUP BY student.student_profile_index.sid,
                        student.student_profile_index.last_name,
                        student.student_profile_index.first_name{group}"""


# ORDER BY


def sort_value(sort, key):
    try:
        return sort[f'{key}']
    except KeyError:
        return ''


def order_by(sort):
    default_sort = """LOWER(student.student_profile_index.last_name),
                      LOWER(student.student_profile_index.first_name),
                      student.student_profile_index.sid ASC"""
    if sort:
        if sort['col'] == 'first_name':
            return """ORDER BY LOWER(student.student_profile_index.first_name),
                               LOWER(student.student_profile_index.last_name),
                               student.student_profile_index.sid"""
        elif sort_value(sort, 'order_by'):
            return f"""ORDER BY {sort_value(sort, 'order_by')}{sort_value(sort, 'direction')}{sort_value(sort, 'nulls')},
                                {default_sort}"""
        else:
            return f"""ORDER BY {sort['table']}.{sort['col']}{sort_value(sort, 'direction')}{sort_value(sort, 'nulls')},
                                {default_sort}"""
    else:
        return f'ORDER BY {default_sort}'


# QUERIES - COHORT LIST VIEW

def get_cohort_result(test, cohort_filter, sort=None):
    sql = f"""{select_from(sort)}
              {join(filter_join_clauses(cohort_filter), sort)}
              {where(test, cohort_filter)}
              {group_by(sort)}
              {order_by(sort)}"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return [r['sid'] for r in results]


# Last Name

def cohort_by_last_name(test, cohort_filter):
    return get_cohort_result(test, cohort_filter)


# First name

def cohort_by_first_name(test, cohort_filter):
    sort = {
        'table': 'student.student_profile_index',
        'col': 'first_name',
        'group_by': False,
    }
    return get_cohort_result(test, cohort_filter, sort)


# Level

def cohort_by_level(test, cohort_filter):
    sort = {
        'table': 'student.student_profile_index',
        'col': 'level',
        'group_by': True,
    }
    return get_cohort_result(test, cohort_filter, sort)


# Major

def cohort_by_major(test, cohort_filter):
    sort = {
        'table': 'student.student_majors',
        'col': 'major',
        'nulls': ' NULLS FIRST',
        'select': '(ARRAY_AGG(student.student_majors.major ORDER BY student.student_majors.major))[1] AS major',
        'order_by': 'major',
        'group_by': False,
    }
    return get_cohort_result(test, cohort_filter, sort)


# Entering term

def cohort_by_matriculation(test, cohort_filter):
    sort = {
        'table': 'student.student_profile_index',
        'col': 'entering_term',
        'nulls': ' NULLS LAST',
        'group_by': True,
    }
    return get_cohort_result(test, cohort_filter, sort)


def cohort_by_expected_grad(test, cohort_filter):
    sort = {
        'table': 'student.student_profile_index',
        'col': 'expected_grad_term',
        'nulls': ' NULLS LAST',
        'group_by': True,
    }
    return get_cohort_result(test, cohort_filter, sort)


# Team

def cohort_by_team(test, cohort_filter):
    sort = {
        'table': 'boac_advising_asc.students',
        'col': 'group_name',
        'nulls': ' NULLS LAST',
        'select': '(ARRAY_AGG (boac_advising_asc.students.group_name ORDER BY boac_advising_asc.students.group_name))[1] AS team',
        'order_by': 'team',
        'group_by': False,
    }
    return get_cohort_result(test, cohort_filter, sort)


# GPA - cumulative

def cohort_by_gpa_sort():
    return {
        'table': 'student.student_profile_index',
        'col': 'gpa',
        'group_by': True,
    }


def cohort_by_gpa_asc(test, cohort_filter):
    gpa_sort = cohort_by_gpa_sort()
    gpa_sort.update({'direction': ' ASC', 'nulls': ' NULLS FIRST'})
    return get_cohort_result(test, cohort_filter, gpa_sort)


def cohort_by_gpa_desc(test, cohort_filter):
    gpa_sort = cohort_by_gpa_sort()
    gpa_sort.update({'direction': ' DESC', 'nulls': ' NULLS FIRST'})
    return get_cohort_result(test, cohort_filter, gpa_sort)


# GPA - previous term

def cohort_by_prev_term_gpa_sort(term):
    return {
        'table': 'student.student_term_gpas',
        'col': 'gpa',
        'nulls': ' NULLS LAST',
        'select': previous_term_gpa_sub_query(term),
        'term_id': term,
        'group_by': True,
    }


def cohort_by_gpa_last_term_asc(test, cohort_filter, term=None):
    term = term or utils.get_previous_term()
    gpa_sort = cohort_by_prev_term_gpa_sort(term.sis_id)
    gpa_sort.update({'direction': ' ASC', 'order_by': 'gpa_last_term'})
    return get_cohort_result(test, cohort_filter, gpa_sort)


def cohort_by_gpa_last_term_desc(test, cohort_filter, term=None):
    term = term or utils.get_previous_term()
    gpa_sort = cohort_by_prev_term_gpa_sort(term.sis_id)
    gpa_sort.update({'direction': ' DESC', 'order_by': 'gpa_last_term'})
    return get_cohort_result(test, cohort_filter, gpa_sort)


# Terms in attendance

def cohort_by_terms_in_attend_sort():
    return {
        'table': 'student.student_profile_index',
        'col': 'terms_in_attendance',
        'nulls': ' NULLS LAST',
        'group_by': True,
    }


def cohort_by_terms_in_attend_asc(test, cohort_filter):
    terms_sort = cohort_by_terms_in_attend_sort()
    terms_sort.update({'direction': ' ASC'})
    return get_cohort_result(test, cohort_filter, terms_sort)


def cohort_by_terms_in_attend_desc(test, cohort_filter):
    terms_sort = cohort_by_terms_in_attend_sort()
    terms_sort.update({'direction': ' DESC'})
    return get_cohort_result(test, cohort_filter, terms_sort)


# Units in progress

def cohort_by_units_in_prog_sort():
    return {
        'table': 'student.student_enrollment_terms',
        'col': 'enrolled_units',
        'nulls': ' NULLS LAST',
        'select': cohort_units_in_prog_sub_query(),
        'term_id': utils.get_current_term().sis_id,
        'order_by': 'units_in_progress',
        'group_by': True,
    }


def cohort_by_units_in_prog_asc(test, cohort_filter):
    units_sort = cohort_by_units_in_prog_sort()
    units_sort.update({'direction': ' ASC'})
    return get_cohort_result(test, cohort_filter, units_sort)


def cohort_by_units_in_prog_desc(test, cohort_filter):
    units_sort = cohort_by_units_in_prog_sort()
    units_sort.update({'direction': ' DESC'})
    return get_cohort_result(test, cohort_filter, units_sort)


# Units complete

def cohort_by_units_complete_sort():
    return {
        'table': 'student.student_profile_index',
        'col': 'units',
        'group_by': True,
    }


def cohort_by_units_complete_asc(test, cohort_filter):
    units_sort = cohort_by_units_complete_sort()
    units_sort.update({'direction': ' ASC', 'nulls': ' NULLS LAST'})
    return get_cohort_result(test, cohort_filter, units_sort)


def cohort_by_units_complete_desc(test, cohort_filter):
    units_sort = cohort_by_units_complete_sort()
    units_sort.update({'direction': ' DESC', 'nulls': ' NULLS LAST'})
    return get_cohort_result(test, cohort_filter, units_sort)


# QUERIES - USER LISTS

def order_by_list(sort):
    default_sort = """LOWER(student.student_profile_index.last_name),
                      LOWER(student.student_profile_index.first_name),
                      student.student_profile_index.sid ASC"""
    if sort:
        if sort['col'] == 'last_name':
            return f"""ORDER BY LOWER(student.student_profile_index.last_name){sort_value(sort, 'direction')}{sort_value(sort, 'nulls')},
                                LOWER(student.student_profile_index.first_name),
                                student.student_profile_index.sid"""
        elif sort_value(sort, 'order_by'):
            return f"""ORDER BY {sort_value(sort, 'order_by')}{sort_value(sort, 'direction')}{sort_value(sort, 'nulls')},
                                {default_sort}"""
        else:
            return f"""ORDER BY {sort['table']}.{sort['col']}{sort_value(sort, 'direction')}{sort_value(sort, 'nulls')},
                                {default_sort}"""
    else:
        return f'ORDER BY {default_sort}'


def get_list_result(sids, sort=None, opts=None):
    sids = list(map(lambda s: f"'{s}'", sids))
    sid_list = ', '.join(sids)
    sql = f"""{select_from(sort)}
              {join('', sort, opts)}
              WHERE student.student_profile_index.sid IN({sid_list})
              {group_by(sort)}
              {order_by_list(sort)}"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return [r['sid'] for r in results]


# Last name

def list_by_last_name_asc(sids):
    return get_list_result(sids)


def list_by_last_name_desc(sids):
    sort = {
        'table': 'student.student_profile_index',
        'col': 'last_name',
        'direction': ' DESC',
    }
    return get_list_result(sids, sort)


# Major

def list_by_major_sort():
    return {
        'table': 'student.student_majors',
        'col': 'major',
        'select': '(ARRAY_AGG(student.student_majors.major ORDER BY student.student_majors.major))[1] AS major',
        'order_by': 'major',
        'group_by': False,
    }


def list_by_major_asc(sids):
    major_sort = list_by_major_sort()
    major_sort.update({'nulls': ' NULLS FIRST', 'direction': ' ASC'})
    return get_list_result(sids, major_sort, {'active': True})


def list_by_major_desc(sids):
    major_sort = list_by_major_sort()
    major_sort.update({'nulls': ' NULLS LAST', 'direction': ' DESC'})
    return get_list_result(sids, major_sort, {'active': True})


# Grad term

def list_by_grad_term_sort():
    return {
        'table': 'student.student_profile_index',
        'col': 'expected_grad_term',
        'select': 'student.student_profile_index.expected_grad_term AS term',
        'nulls': ' NULLS FIRST',
        'order_by': 'term',
        'group_by': True,
    }


def list_by_grad_term_asc(sids):
    grad_sort = list_by_grad_term_sort()
    grad_sort.update({'direction': ' ASC'})
    return get_list_result(sids, grad_sort)


def list_by_grad_term_desc(sids):
    grad_sort = list_by_grad_term_sort()
    grad_sort.update({'direction': ' DESC'})
    return get_list_result(sids, grad_sort)


# GPA

def list_by_gpa_sort():
    return {
        'table': 'student.student_profile_index',
        'col': 'gpa',
        'group_by': True,
    }


def list_by_gpa_asc(sids):
    gpa_sort = list_by_gpa_sort()
    gpa_sort.update({'nulls': ' NULLS FIRST', 'direction': ' ASC'})
    return get_list_result(sids, gpa_sort)


def list_by_gpa_desc(sids):
    gpa_sort = list_by_gpa_sort()
    gpa_sort.update({'nulls': ' NULLS LAST', 'direction': ' DESC'})
    return get_list_result(sids, gpa_sort)


# Units in progress

def list_by_units_in_prog_sort():
    return {
        'table': 'student.student_enrollment_terms',
        'col': 'enrolled_units',
        'select': user_list_units_in_prog_sub_query(),
        'term_id': utils.get_current_term().sis_id,
        'order_by': 'units_in_progress',
        'group_by': True,
    }


def list_by_units_in_prog_asc(sids):
    units_sort = list_by_units_in_prog_sort()
    units_sort.update({'nulls': ' NULLS FIRST', 'direction': ' ASC'})
    return get_list_result(sids, units_sort)


def list_by_units_in_prog_desc(sids):
    units_sort = list_by_units_in_prog_sort()
    units_sort.update({'nulls': ' NULLS LAST', 'direction': ' DESC'})
    return get_list_result(sids, units_sort)


# Units complete

def list_by_units_complete_sort():
    return {
        'table': 'student.student_profile_index',
        'col': 'units',
        'group_by': True,
    }


def list_by_units_complete_asc(sids):
    units_sort = list_by_units_complete_sort()
    units_sort.update({'nulls': ' NULLS FIRST', 'direction': ' ASC'})
    return get_list_result(sids, units_sort)


def list_by_units_complete_desc(sids):
    units_sort = list_by_units_complete_sort()
    units_sort.update({'nulls': ' NULLS LAST', 'direction': ' DESC'})
    return get_list_result(sids, units_sort)
