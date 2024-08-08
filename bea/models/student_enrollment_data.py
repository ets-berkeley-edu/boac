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
import re

from bea.models.academic_standings import AcademicStanding
from bea.models.academic_standings import AcademicStandings
from bea.models.degree_progress.degree_completed_course import DegreeCompletedCourse
from bea.test_utils import boa_utils
from bea.test_utils import utils


class EnrollmentData(object):

    def __init__(self, data):
        self.data = data

    def enrollment_terms(self):
        return self.data

    @staticmethod
    def term_id(term):
        return utils.safe_key(term, 'termId')

    @staticmethod
    def term_name(term):
        return utils.safe_key(term, 'termName')

    def current_term(self):
        for term in self.enrollment_terms():
            if self.term_name(term) == utils.get_current_term():
                return term

    @staticmethod
    def term_units_float(term):
        return f"{float(term['enrolledUnits'])}"

    @staticmethod
    def term_units(term):
        return utils.formatted_units(term['enrolledUnits'])

    @staticmethod
    def term_units_max_float(term):
        return f"{float(term['maxTermUnitsAllowed'])}"

    @staticmethod
    def term_units_max(term):
        return utils.formatted_units(term['maxTermUnitsAllowed'])

    @staticmethod
    def term_units_min_float(term):
        return f"{float(term['minTermUnitsAllowed'])}"

    @staticmethod
    def term_units_min(term):
        return utils.formatted_units(term['minTermUnitsAllowed'])

    @staticmethod
    def term_gpa(term):
        return utils.safe_key(term, 'termGpa') and utils.safe_key(term['termGpa'], 'gpa')

    @staticmethod
    def term_gpa_units(term):
        return utils.safe_key(term, 'termGpa') and utils.safe_key(term['termGpa'], 'unitsTakenForGpa')

    def academic_standing(self):
        standings = []
        terms = self.enrollment_terms() or []
        for t in terms:
            term_standing = utils.safe_key(t, 'academicStanding')
            if term_standing:
                standing = next(filter(lambda s: s.code == term_standing['status'], AcademicStandings))
                standings.append(AcademicStanding({
                    'code': (utils.safe_key(term_standing, 'status') or ''),
                    'descrip': (standing and standing.value['descrip']),
                    'term_id': term_standing['termId'],
                    'term_name': self.term_name(t),
                }))
        standings = [s for s in standings if s]
        return standings

    # Courses

    @staticmethod
    def courses(term):
        return term['enrollments']

    @staticmethod
    def course_display_name(course):
        return course['displayName']

    @staticmethod
    def grade(course, grade_key):
        if utils.safe_key(course, grade_key):
            return course[f'{grade_key}'].replace('-', '−')
        else:
            return None

    def sis_course_data(self, course):
        reqts = utils.safe_key(course, 'courseRequirements') and list(
            map(lambda req: re.sub(r'\s+', ' ', req), course['courseRequirements']))
        return {
            'code': self.course_display_name(course),
            'title': (re.sub(r'\s+', ' ', course['title'])),
            'units_completed_float': f"{float(course['units'])}",
            'units_completed': f"{(course['units'] // 1) if (course['units'] // 1) == course['units'] else course['units']}",
            'midpoint': self.grade(course, 'midtermGrade'),
            'grade': self.grade(course, 'grade'),
            'grading_basis': course['gradingBasis'],
            'reqts': reqts,
            'acad_career': course['academicCareer'],
        }

    def course_by_section_id(self, section):
        term = next(filter(lambda t: self.term_id(t) == section.term.sis_id, self.enrollment_terms()))
        for course in self.courses(term):
            if section.ccn in self.course_section_ccns(course):
                return course

    def term_courses_of_statuses(self, term, statuses):
        course_codes = []
        for c in self.courses(term):
            for s in self.sections(c):
                section_data = self.sis_section_data(s)
                if section_data['status'] in statuses:
                    course_codes.append(section_data['code'])
        return course_codes

    def current_non_dropped_course_codes(self, term):
        return self.term_courses_of_statuses(term, ['E', 'W'])

    def current_waitlisted_course_codes(self, term):
        return self.term_courses_of_statuses(term, ['W'])

    @staticmethod
    def incomplete_grade_outcome(grading_basis):
        if grading_basis in ['GRD', 'Letter']:
            return 'an F'
        elif grading_basis in ['NON', 'SUS']:
            return 'a U'
        elif grading_basis == 'FRZ':
            return 'a failing grade'
        else:
            return 'a NP'

    # Sections

    @staticmethod
    def sections(course):
        return course['sections']

    @staticmethod
    def sis_section_data(section):
        return {
            'ccn': f"{section['ccn']}",
            'number': f"{section['sectionNumber']}",
            'component': section['component'],
            'units_completed': f"{(section['units'] // 1) if (section['units'] // 1) == section['units'] else section['units']}",
            'primary': section['primary'],
            'status': section['enrollmentStatus'],
            'incomplete_code': utils.safe_key(section, 'incompleteStatusCode'),
            'incomplete_frozen': utils.safe_key(section, 'incompleteFrozenFlag'),
            'incomplete_lapse_date': utils.safe_key(section, 'incompleteLapseGradeDate'),
        }

    def course_section_ccns(self, course):
        return list(map(lambda s: self.sis_section_data(s)['ccn'], self.sections(course)))

    def course_primary_section(self, course):
        for section in self.sections(course):
            if utils.safe_key(self.sis_section_data(section), 'primary'):
                return section

    @staticmethod
    def dropped_sections(term):
        sections = []
        section_data = utils.safe_key(term, 'droppedSections') or []
        for s in section_data:
            sections.append({
                'title': s['displayName'],
                'component': s['component'],
                'number': s['sectionNumber'],
                'date': s['dropDate'],
            })
        return sections

    # COURSE SITES

    @staticmethod
    def course_sites(course):
        return course['canvasSites']

    @staticmethod
    def unmatched_sites(term):
        return term['unmatchedCanvasSites']

    @staticmethod
    def site_metadata(site):
        return {
            'code': re.sub(r'\s+', ' ', site['courseCode']),
            'title': re.sub(r'\s+', ' ', site['courseName']),
            'site_id': site['canvasCourseId'],
        }

    @staticmethod
    def analytics(site):
        return utils.safe_key(site, 'analytics')

    def site_scores(self, site):
        return self.analytics(site) and utils.safe_key(self.analytics(site), 'courseCurrentScore')

    @staticmethod
    def student_data(analytics):
        return utils.safe_key(analytics, 'student')

    @staticmethod
    def course_deciles(analytics):
        return utils.safe_key(analytics, 'courseDeciles')

    def score(self, analytics):
        score = self.student_data(analytics) and utils.safe_key(self.student_data(analytics), 'raw')
        if score:
            if score == int(score):
                return f'{int(score)}'
            else:
                return f'{score}'
        elif score == 0:
            return f'{score}'
        else:
            return None

    def site_statistics(self, analytics):
        student_data = self.student_data(analytics)
        deciles = self.course_deciles(analytics)
        return {
            'graphable': analytics['boxPlottable'],
            'perc': (student_data and student_data['percentile']),
            'perc_round': (student_data and student_data['roundedUpPercentile']),
            'score': self.score(analytics),
            'max': (deciles and f'{deciles[10]}'),
            'perc_70': (deciles and f'{deciles[7]}'),
            'perc_50': (deciles and f'{deciles[5]}'),
            'perc_30': (deciles and f'{deciles[3]}'),
            'min': (deciles and f'{deciles[0]}'),
        }

    def assignments_submitted(self, site):
        data = self.site_statistics(self.analytics(site)['assignmentsSubmitted'])
        data.update({'type': 'Assignments Submitted'})
        return data

    def assignment_grades(self, site):
        data = self.site_statistics(self.analytics(site)['currentScore'])
        data.update({'type': 'Assignment Grades'})
        return data

    def last_activity_day(self, site):
        epoch = utils.safe_key(self.site_statistics(self.analytics(site)['lastActivity']), 'score')
        if not epoch or int(epoch) == 0:
            return 'Never'
        else:
            activity_date = utils.date_to_local_tz(datetime.strptime(epoch, '%s')).date()
            if activity_date == datetime.today():
                return 'Today'
            elif activity_date == datetime.today() - timedelta(days=1):
                return 'Yesterday'
            else:
                return f'{(datetime.today() - activity_date).days} days ago'

    # DEGREE PROGRESS

    def degree_progress_in_prog_courses(self, degree_check):
        courses = []
        term_id = utils.get_current_term().sis_id
        for course in self.courses(self.current_term()):
            data = self.sis_course_data(course)
            if not data['grade']:
                primary_section = self.sis_section_data(self.course_primary_section(course))
                courses.append(DegreeCompletedCourse({
                    'ccn': primary_section['ccn'],
                    'degree_check': degree_check,
                    'name': data['code'],
                    'term_id': term_id,
                    'units': data['units_completed'],
                    'units_orig': data['units_completed'],
                    'waitlisted': (primary_section['status'] == 'W'),
                }))
        courses.sort(key=lambda c: c.name)
        return courses

    def degree_progress_courses(self, degree_check):
        courses = []
        for term in self.enrollment_terms():
            term_id = self.term_id(term)
            for course in self.courses(term):
                data = self.sis_course_data(course)
                primary_section = self.sis_section_data(self.course_primary_section(course))
                if not float(data['units_completed']) == 0:
                    course = DegreeCompletedCourse({
                        'ccn': primary_section['ccn'],
                        'degree_check': degree_check,
                        'grade': data['grade'].replace('−', '-'),
                        'name': data['code'],
                        'term_id': term_id,
                        'units': data['units_completed'],
                        'units_orig': data['units_completed'],
                    })
                    boa_utils.set_degree_sis_course_id(degree_check, course)
                    courses.append(course)
        courses.sort(key=lambda c: c.name)
        return courses
