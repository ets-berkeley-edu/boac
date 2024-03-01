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
from bea.test_utils import boa_utils
from flask import current_app as app


class CohortFilter(object):

    def __init__(self, data, dept):
        self.data = data
        self.dept = dept

    @property
    def academic_careers(self):
        return self.data.get('academic_careers') and list(map(lambda d: d['career'], self.data['academic_careers']))

    @property
    def academic_divisions(self):
        return self.data.get('academic_divs') and list(map(lambda d: d['div'], self.data['academic_divs']))

    @property
    def academic_standings(self):
        return self.data.get('academic_standings') and list(map(lambda d: d['standing'], self.data['academic_standings']))

    @property
    def asc_inactive(self):
        return self.data.get('asc_inactive') if self.dept in [Department.ADMIN, Department.ASC] else None

    @property
    def asc_intensive(self):
        return self.data.get('asc_intensive') if self.dept in [Department.ADMIN, Department.ASC] else None

    @property
    def asc_teams(self):
        if self.dept in [Department.ADMIN, Department.ASC]:
            return self.data.get('asc_teams') and list(map(lambda d: d['squad'], self.data['asc_teams']))
        else:
            return None

    @property
    def career_statuses(self):
        return self.data.get('career_statuses') and list(map(lambda d: d['status'], self.data['career_statuses']))

    @property
    def coe_advisors(self):
        if self.dept in [Department.ADMIN, Department.COE]:
            return self.data.get('coe_advisors') and list(map(lambda d: d['advisor'], self.data['coe_advisors']))
        else:
            return None

    @property
    def coe_ethnicities(self):
        if self.dept in [Department.ADMIN, Department.COE]:
            return self.data.get('coe_ethnicities') and list(map(lambda d: d['ethnicity'], self.data['coe_ethnicities']))
        else:
            return None

    @property
    def coe_inactive(self):
        return self.data.get('coe_inactive') if self.dept in [Department.ADMIN, Department.COE] else None

    @property
    def coe_preps(self):
        if self.dept in [Department.ADMIN, Department.COE]:
            return self.data.get('coe_preps') and list(map(lambda d: d['prep'], self.data['coe_preps']))
        else:
            return None

    @property
    def coe_probation(self):
        return self.data.get('coe_probation') if self.dept in [Department.ADMIN, Department.COE] else None

    @property
    def coe_underrepresented_minority(self):
        return self.data.get('coe_underrepresented_minority') if self.dept in [Department.ADMIN, Department.COE] else None

    @property
    def cohort_owner_acad_plans(self):
        return self.data.get('cohort_owner_acad_plans') and list(map(lambda d: d['plan'], self.data['cohort_owner_acad_plans']))

    @property
    def colleges(self):
        return self.data.get('colleges') and list(map(lambda d: d['college'], self.data['colleges']))

    @property
    def degree_terms(self):
        return self.data.get('degree_terms') and list(map(lambda d: d['term'], self.data['degree_terms']))

    @property
    def degrees_awarded(self):
        return self.data.get('degrees_awarded') and list(map(lambda d: d['degree'], self.data['degrees_awarded']))

    @property
    def entering_terms(self):
        return self.data.get('entering_terms') and list(map(lambda d: d['term'], self.data['entering_terms']))

    @property
    def ethnicities(self):
        return self.data.get('ethnicities') and list(map(lambda d: d['ethnicity'], self.data['ethnicities']))

    @property
    def expected_grad_terms(self):
        if self.data.get('expected_grad_terms'):
            return [boa_utils.get_prev_term_sis_id(boa_utils.get_term_sis_id()), boa_utils.get_term_sis_id()]
        else:
            return None

    @property
    def gpa_ranges(self):
        return self.data.get('gpa_ranges') and list(map(lambda d: d['range'], self.data['gpa_ranges']))

    @property
    def gpa_ranges_last_term(self):
        return self.data.get('gpa_ranges_last_term') and list(map(lambda d: d['range'], self.data['gpa_ranges_last_term']))

    @property
    def grading_basis_epn(self):
        return self.data.get('grading_basis_epn') and f'{boa_utils.get_term_sis_id()}'

    @property
    def graduate_plans(self):
        return self.data.get('graduate_plans') and list(map(lambda d: d['plan'], self.data['graduate_plans']))

    @property
    def holds(self):
        return self.data.get('holds')

    @property
    def incomplete_grades(self):
        return self.data.get('incomplete_grades') and list(map(lambda d: d['grade'], self.data['incomplete_grades']))

    @property
    def incomplete_sched_grades(self):
        if self.data.get('incomplete_sched_grades'):
            return [{'min': datetime.now().strftime('%Y-%m-%d'), 'max': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}]
        else:
            return None

    @property
    def intended_majors(self):
        return self.data.get('intended_majors') and list(map(lambda d: d['major'], self.data['intended_majors']))

    @property
    def last_name(self):
        return self.data.get('last_initials') and list(map(lambda d: d['initial'], self.data['last_initials']))

    @property
    def levels(self):
        return self.data.get('levels') and list(map(lambda d: d['level'], self.data['levels']))

    @property
    def majors(self):
        return self.data.get('majors') and list(map(lambda d: d['major'], self.data['majors']))

    @property
    def mid_point_deficient(self):
        return self.data.get('mid_point_deficient')

    @property
    def minors(self):
        return self.data.get('minors') and list(map(lambda d: d['minor'], self.data['minors']))

    @property
    def transfer_student(self):
        return self.data.get('transfer_student')

    @property
    def underrepresented_minority(self):
        return self.data.get('underrepresented_minority')

    @property
    def units_completed(self):
        return self.data.get('units') and list(map(lambda d: d['unit'], self.data['units']))

    @property
    def visa_types(self):
        return self.data.get('visa_types') and list(map(lambda d: d['visa_type'], self.data['visa_types']))

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
