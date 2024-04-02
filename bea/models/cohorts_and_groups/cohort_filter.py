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

from datetime import datetime
from datetime import timedelta

from bea.models.department import Department
from bea.models.squad import Squad
from bea.test_utils import utils
from flask import current_app as app


class CohortFilter(object):

    def __init__(self, data, dept):
        self.data = data
        self.dept = dept

    @property
    def academic_careers(self):
        return list(map(lambda d: d['career'], self.data['academic_careers'])) if self.data.get('academic_careers') else []

    @academic_careers.setter
    def academic_careers(self, value):
        self.data['academic_careers'] = value

    @property
    def academic_divisions(self):
        return list(map(lambda d: d['div'], self.data['academic_divs'])) if self.data.get('academic_divs') else []

    @academic_divisions.setter
    def academic_divisions(self, value):
        self.data['academic_divisions'] = value

    @property
    def academic_standings(self):
        return list(map(lambda d: d['standing'], self.data['academic_standings'])) if self.data.get('academic_standings') else []

    @academic_standings.setter
    def academic_standings(self, value):
        self.data['academic_standings'] = value

    @property
    def asc_inactive(self):
        return self.data.get('asc_inactive') if self.dept in [Department.ADMIN, Department.ASC] else None

    @asc_inactive.setter
    def asc_inactive(self, value):
        self.data['asc_inactive'] = value

    @property
    def asc_intensive(self):
        return self.data.get('asc_intensive') if self.dept in [Department.ADMIN, Department.ASC] else None

    @asc_intensive.setter
    def asc_intensive(self, value):
        self.data['asc_intensive'] = value

    @property
    def asc_teams(self):
        teams = self.data.get('asc_teams')
        if teams and self.dept in [Department.ADMIN, Department.ASC]:
            squads = []
            for team in teams:
                if team['squad'].__class__.__name__ == 'Squad':
                    squad = team['squad']
                else:
                    squad = next(filter(lambda sq: sq.value['name'] == team['squad'], Squad))
                squads.append(squad)
            return squads
        else:
            return []

    @asc_teams.setter
    def asc_teams(self, value):
        self.data['asc_teams'] = value

    @property
    def career_statuses(self):
        return list(map(lambda d: d['status'], self.data['career_statuses'])) if self.data.get('career_statuses') else []

    @career_statuses.setter
    def career_statuses(self, value):
        self.data['career_statuses'] = value

    @property
    def coe_advisors(self):
        if self.data.get('coe_advisors') and self.dept in [Department.ADMIN, Department.COE]:
            return list(map(lambda d: d['advisor'], self.data['coe_advisors']))
        else:
            return []

    @coe_advisors.setter
    def coe_advisors(self, value):
        self.data['coe_advisors'] = value

    @property
    def coe_ethnicities(self):
        if self.data.get('coe_ethnicities') and self.dept in [Department.ADMIN, Department.COE]:
            return list(map(lambda d: d['ethnicity'], self.data['coe_ethnicities']))
        else:
            return []

    @coe_ethnicities.setter
    def coe_ethnicities(self, value):
        self.data['coe_ethnicities'] = value

    @property
    def coe_inactive(self):
        return self.data.get('coe_inactive') if self.dept in [Department.ADMIN, Department.COE] else None

    @coe_inactive.setter
    def coe_inactive(self, value):
        self.data['coe_inactive'] = value

    @property
    def coe_preps(self):
        if self.data.get('coe_preps') and self.dept in [Department.ADMIN, Department.COE]:
            return list(map(lambda d: d['prep'], self.data['coe_preps']))
        else:
            return []

    @coe_preps.setter
    def coe_preps(self, value):
        self.data['coe_preps'] = value

    @property
    def coe_probation(self):
        return self.data.get('coe_probation') if self.dept in [Department.ADMIN, Department.COE] else None

    @coe_probation.setter
    def coe_probation(self, value):
        self.data['coe_probation'] = value

    @property
    def coe_underrepresented_minority(self):
        return self.data.get('coe_underrepresented_minority') if self.dept in [Department.ADMIN, Department.COE] else None

    @coe_underrepresented_minority.setter
    def coe_underrepresented_minority(self, value):
        self.data['coe_underrepresented_minority'] = value

    @property
    def cohort_owner_acad_plans(self):
        return list(map(lambda d: d['plan'], self.data['cohort_owner_acad_plans'])) if self.data.get('cohort_owner_acad_plans') else None

    @cohort_owner_acad_plans.setter
    def cohort_owner_acad_plans(self, value):
        self.data['cohort_owner_acad_plans'] = value

    @property
    def colleges(self):
        return list(map(lambda d: d['college'], self.data['colleges'])) if self.data.get('colleges') else []

    @colleges.setter
    def colleges(self, value):
        self.data['colleges'] = value

    @property
    def degree_terms(self):
        return list(map(lambda d: d['term'], self.data['degree_terms'])) if self.data.get('degree_terms') else []

    @degree_terms.setter
    def degree_terms(self, value):
        self.data['degree_terms'] = value

    @property
    def degrees_awarded(self):
        return list(map(lambda d: d['degree'], self.data['degrees_awarded'])) if self.data.get('degrees_awarded') else []

    @degrees_awarded.setter
    def degrees_awarded(self, value):
        self.data['degrees_awarded'] = value

    @property
    def entering_terms(self):
        return list(map(lambda d: d['entering_term'], self.data['entering_terms'])) if self.data.get('entering_terms') else []

    @entering_terms.setter
    def entering_terms(self, value):
        self.data['entering_terms'] = value

    @property
    def ethnicities(self):
        return list(map(lambda d: d['ethnicity'], self.data['ethnicities'])) if self.data.get('ethnicities') else []

    @ethnicities.setter
    def ethnicities(self, value):
        self.data['ethnicities'] = value

    @property
    def expected_grad_terms(self):
        if self.data.get('expected_grad_terms'):
            current_term = utils.get_current_term()
            prev_term = utils.get_previous_term()
            return [prev_term.sis_id, current_term.sis_id]
        else:
            return []

    @expected_grad_terms.setter
    def expected_grad_terms(self, value):
        self.data['expected_grad_terms'] = value

    @property
    def gpa_ranges(self):
        return list(map(lambda d: d['range'], self.data['gpa_ranges'])) if self.data.get('gpa_ranges') else []

    @gpa_ranges.setter
    def gpa_ranges(self, value):
        self.data['gpa_ranges'] = value

    @property
    def gpa_ranges_last_term(self):
        return list(map(lambda d: d['range'], self.data['gpa_ranges_last_term'])) if self.data.get('gpa_ranges_last_term') else []

    @gpa_ranges_last_term.setter
    def gpa_ranges_last_term(self, value):
        self.data['gpa_ranges_last_term'] = value

    @property
    def grading_basis_epn(self):
        return [f'{utils.get_current_term().sis_id}'] if self.data.get('grading_basis_epn') else []

    @grading_basis_epn.setter
    def grading_basis_epn(self, value):
        self.data['grading_basis_epn'] = value

    @property
    def graduate_plans(self):
        return list(map(lambda d: d['plan'], self.data['graduate_plans'])) if self.data.get('graduate_plans') else []

    @graduate_plans.setter
    def graduate_plans(self, value):
        self.data['graduate_plans'] = value

    @property
    def holds(self):
        return self.data.get('holds')

    @holds.setter
    def holds(self, value):
        self.data['holds'] = value

    @property
    def incomplete_grades(self):
        return list(map(lambda d: d['grade'], self.data['incomplete_grades'])) if self.data.get('incomplete_grades') else []

    @incomplete_grades.setter
    def incomplete_grades(self, value):
        self.data['incomplete_grades'] = value

    @property
    def incomplete_sched_grades(self):
        if self.data.get('incomplete_sched_grades'):
            return [{'min': datetime.now().strftime('%Y-%m-%d'), 'max': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}]
        else:
            return []

    @incomplete_sched_grades.setter
    def incomplete_sched_grades(self, value):
        self.data['incomplete_sched_grades'] = value

    @property
    def intended_majors(self):
        return list(map(lambda d: d['major'], self.data['intended_majors'])) if self.data.get('intended_majors') else []

    @intended_majors.setter
    def intended_majors(self, value):
        self.data['intended_majors'] = value

    @property
    def last_name(self):
        return list(map(lambda d: d['initial'], self.data['last_initials'])) if self.data.get('last_initials') else []

    @last_name.setter
    def last_name(self, value):
        self.data['last_name'] = value

    @property
    def levels(self):
        return list(map(lambda d: d['level'], self.data['levels'])) if self.data.get('levels') else []

    @levels.setter
    def levels(self, value):
        self.data['levels'] = value

    @property
    def majors(self):
        return list(map(lambda d: d['major'], self.data['majors'])) if self.data.get('majors') else []

    @majors.setter
    def majors(self, value):
        self.data['majors'] = value

    @property
    def mid_point_deficient(self):
        return self.data.get('mid_point_deficient')

    @mid_point_deficient.setter
    def mid_point_deficient(self, value):
        self.data['mid_point_deficient'] = value

    @property
    def minors(self):
        return list(map(lambda d: d['minor'], self.data['minors'])) if self.data.get('minors') else []

    @minors.setter
    def minors(self, value):
        self.data['minors'] = value

    @property
    def my_students(self):
        if self.data.get('cohort_owner_academic_plans'):
            return list(map(lambda p: p['plan'], self.data.get('cohort_owner_academic_plans')))
        else:
            return []

    @my_students.setter
    def my_students(self, value):
        self.data['cohort_owner_academic_plans'] = value

    @property
    def transfer_student(self):
        return self.data.get('transfer_student')

    @transfer_student.setter
    def transfer_student(self, value):
        self.data['transfer_student'] = value

    @property
    def underrepresented_minority(self):
        return self.data.get('underrepresented_minority')

    @underrepresented_minority.setter
    def underrepresented_minority(self, value):
        self.data['underrepresented_minority'] = value

    @property
    def units_completed(self):
        return list(map(lambda d: d['unit'], self.data['units'])) if self.data.get('units') else []

    @units_completed.setter
    def units_completed(self, value):
        self.data['units'] = value

    @property
    def visa_types(self):
        return list(map(lambda d: d['visa_type'], self.data['visa_types'])) if self.data.get('visa_types') else []

    @visa_types.setter
    def visa_types(self, value):
        self.data['visa_types'] = value

    @staticmethod
    def level_per_code(code):
        if code == '10':
            return 'Freshman (0-29 Units)'
        elif code == '20':
            return 'Sophomore (30-59 Units)'
        elif code == '30':
            return 'Junior (60-89 Units)'
        elif code == '40':
            return 'Senior (90+ Units)'
        elif code == '5':
            return 'Masters and/or Professional'
        elif code == '6':
            return 'Doctoral Students Not Advance to Candidacy'
        elif code == '7':
            return 'Doctoral Advanced to Candidacy <= 6 Terms'
        elif code == '8':
            return 'Doctoral Advanced to Candidacy > 6 Terms'
        else:
            app.logger.error(f'Unknown level code {code}')

    @staticmethod
    def coe_ethnicity_per_code(code):
        if code == 'A':
            return 'African-American / Black'
        elif code == 'B':
            return 'Japanese / Japanese-American'
        elif code == 'C':
            return 'American Indian / Alaska Native'
        elif code == 'D':
            return 'Other'
        elif code == 'E':
            return 'Mexican / Mexican-American / Chicano'
        elif code == 'F':
            return 'White / Caucasian'
        elif code == 'G':
            return 'Declined to state'
        elif code == 'H':
            return 'Chinese / Chinese-American'
        elif code == 'I':
            return 'Other Spanish-American / Latino'
        elif code == 'L':
            return 'Filipino / Filipino-American'
        elif code == 'M':
            return 'Pacific Islander'
        elif code == 'P':
            return 'Puerto Rican'
        elif code == 'R':
            return 'East Indian / Pakistani'
        elif code == 'T':
            return 'Thai / Other Asian'
        elif code == 'V':
            return 'Vietnamese'
        elif code == 'X':
            return 'Korean / Korean-American'
        elif code == 'Y':
            return 'Other Asian'
        else:
            app.logger.error(f'Unknown COE ethnicity code {code}')

    @staticmethod
    def visa_type_per_code(code):
        if code == 'F1':
            return 'F-1 International Student'
        elif code == 'J1':
            return 'J-1 International Student'
        elif code == 'PR':
            return 'Permanent Resident'
        else:
            return 'Other'

    @staticmethod
    def colleges_per_career(career):
        if career == 'Undergraduate':
            return [
                'Rausser Clg Natural Resources',
                'Undergrad Business',
                'Undergrad Chemistry',
                'Undergrad Engineering',
                'Undergrad Environmental Design',
                'Undergrad Letters & Science',
                'Undergrad Non-Degree/NonFinAid',
            ]
        elif career == 'Graduate':
            return [
                'Graduate Academic Programs',
                'Graduate Non-Degree/Non-FinAid',
                'Graduate Professional Programs',
                'Graduate Self-Supporting Pgms',
            ]
