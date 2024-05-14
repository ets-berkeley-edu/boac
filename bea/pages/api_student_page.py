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
from bea.models.notes_and_appts.appointment import Appointment
from bea.models.notes_and_appts.note import Note
from bea.models.user import User
from bea.pages.page import Page
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app


class ApiStudentPage(Page):

    def __init__(self, driver, headless):
        super().__init__(driver, headless)
        self.parsed = {}

    def load_data(self, student):
        app.logger.info(f'Getting data for UID {student.uid}')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/api/student/by_uid/{student.uid}')
        self.parsed = self.parse_json()
        if self.parsed['message'] and self.parsed['message'] == 'Unknown student':
            app.logger.info(f'BOA does not recognize UID {student.uid}')
            self.parsed = None

    # Athletics Profile

    def asc_profile(self):
        return self.parsed['athleticsProfile']

    def asc_teams(self):
        if self.asc_profile():
            suffix = '' if self.asc_profile()['isActiveAsc'] else ' (Inactive)'
            return [f"{a['groupName']}{suffix}" for a in self.asc_profile()['athletics']]
        else:
            return None

    # CoE Profile

    def coe_profile(self):
        profile = self.parsed and self.parsed['coeProfile']
        return {
            'coe_advisor': (profile and profile['advisorUid']),
            'ethnicity': (profile and profile['ethnicity']),
            'coe_underrepresented_minority': (profile and profile['minority']),
            'coe_prep': (profile and profile['didPrep']),
            'prep_elig': (profile and profile['prepEligible']),
            't_prep': (profile and profile['didTprep']),
            't_prep_elig': (profile and profile['tprepEligible']),
        }

    # SIS Profile

    def sis_profile(self):
        return self.parsed and self.parsed['sisProfile']

    def sis_profile_data(self):
        profile = self.sis_profile()
        reqts = self.degree_progress()
        return {
            'name': (profile and profile['primaryName']),
            'preferred_name': (profile and profile['preferredName']),
            'email': (profile and profile['emailAddress']),
            'email_alternate': (profile and profile['emailAddressAlternate']),
            'phone': (profile and profile['phoneNumber'] and f"{profile['phoneNumber']}"),
            'cumulative_units': (profile and self.formatted_units(profile['cumulativeUnits'])),
            'cumulative_gpa': (profile and ('{:.3f}'.format(profile['cumulativeGPA']) if profile['cumulativeGPA'] else '--')),
            'majors': self.majors(),
            'minors': self.minors(),
            'level': (profile and profile['level'] and profile['level']['description']),
            'transfer': (profile and profile['transfer']),
            'terms_in_attendance': (profile and f"{profile['termsInAttendance']}"),
            'entered_term': (profile and profile['matriculation']),
            'intended_majors': self.intended_majors(),
            'expected_grad_term_id': (profile and profile['expectedGraduationTerm'] and profile['expectedGraduationTerm']['id']),
            'expected_grad_term_name': (profile and profile['expectedGraduationTerm'] and profile['expectedGraduationTerm']['name']),
            'withdrawal': self.withdrawal(),
            'academic_standing': (profile and profile['academicStanding']),
            'academic_career': (profile and profile['academicCareer']),
            'academic_career_status': (profile and profile['academicCareerStatus']),
            'reqt_writing': (reqts and reqts['writing']),
            'reqt_history': (reqts and reqts['history']),
            'reqt_institutions': (reqts and reqts['institutions']),
            'reqt_cultures': (reqts and reqts['cultures']),
        }

    @staticmethod
    def formatted_units(units_as_num):
        if units_as_num:
            if units_as_num == 0:
                return '0'
            else:
                if units_as_num.floor() == units_as_num:
                    return f'{units_as_num.floor()}'
                else:
                    return '{:.3f}'.format(units_as_num)

    def graduations(self):
        profile = self.sis_profile()
        graduations = []
        degrees = (profile and profile['degrees']) or []
        for d in degrees:
            majors = []
            minors = []
            for p in d['plans']:
                if p['type'] == 'MAJ':
                    majors.append({
                        'college': p['group'],
                        'plan': p['plan'],
                    })
                elif p['type'] == 'MIN':
                    minors.append({
                        'plan': p['plan'].replace('Minor in ', ''),
                    })
            graduations.append({
                'date': datetime.strptime(d['dateAwarded'], '%Y-%m-%d'),
                'degree': d['description'],
                'majors': majors,
                'minors': minors,
            })
        return graduations

    def majors(self):
        profile = self.sis_profile()
        majors = []
        if profile and profile['plans']:
            for p in profile['plans']:
                majors.append({
                    'active': (p['status'] == 'Active'),
                    'college': p['program'],
                    'major': p['description'],
                    'status': p['status'],
                })
            majors.sort(key=lambda m: 0 if m['active'] else 1)
        return majors

    def sub_plans(self):
        return self.sis_profile() and self.sis_profile()['subplans']

    def minors(self):
        profile = self.sis_profile()
        minors = []
        if profile and profile['plansMinor']:
            for p in profile['plansMinor']:
                minors.append({
                    'active': (p['status'] == 'Active'),
                    'college': p['program'],
                    'major': p['description'],
                    'status': p['status'],
                })
        return minors

    def intended_majors(self):
        profile = self.sis_profile()
        intended_majors = []
        profile_majors = (profile and profile['intendedMajors']) or []
        for m in profile_majors:
            if m['description']:
                intended_majors.append(m['description'])
        return intended_majors

    def withdrawal(self):
        profile = self.sis_profile()
        withdrawal = profile and profile['withdrawalCancel']
        return withdrawal and {
            'desc': withdrawal['description'],
            'reason': withdrawal['reason'],
            'date': datetime.strptime(withdrawal['date'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y'),
        }

    def academic_standing_profile(self):
        standing = self.sis_profile_data()['academic_standing']
        if standing:
            status = next(filter(lambda s: s.value['code'] == standing['status'], AcademicStandings))
            return {
                'status': status.value['descrip'],
                'term_name': standing['termName'],
            }

    def academic_standing(self):
        standings = []
        terms = self.terms() or []
        for t in terms:
            term_standing = t['academicStanding']
            if term_standing:
                standing = next(filter(lambda s: s.code == term_standing['status'], AcademicStandings))
                standings.append(AcademicStanding({
                    'code': (term_standing['status'] or ''),
                    'descrip': (standing and standing.value['descrip']),
                    'term_id': term_standing['termId'],
                    'term_name': self.term_name(t),
                }))
        standings = [s for s in standings if s]
        return standings

    def degree_progress(self):
        profile = self.sis_profile()
        progress = profile and profile['degreeProgress'] and profile['degreeProgress']['requirements']
        return progress and {
            'date': progress['reportDate'],
            'writing': f"{progress['entryLevelWriting']['name']} {progress['entryLevelWriting']['status']}",
            'cultures': f"{progress['americanCultures']['name']} {progress['americanCultures']['status']}",
            'history': f"{progress['americanHistory']['name']} {progress['americanHistory']['status']}",
            'institutions': f"{progress['americanInstitutions']['name']} {progress['americanInstitutions']['status']}",
        }

    # Demographics

    def demographics(self):
        data = self.parsed and self.parsed['demographics']
        if data:
            return {
                'ethnicities': data['ethnicities'],
                'nationalities': data['nationalities'],
                'underrepresented': data['underrepresented'],
                'visa': (data['visa'] and {
                    'status': data['visa']['status'],
                    'type': data['visa']['type'],
                }),
            }

    # Advisors

    def advisors(self):
        advisor_data = (self.parsed and self.parsed['advisors']) or []
        advisors = []
        for a in advisor_data:
            advisors.append({
                'email': a['email'],
                'name': f"{a['firstName']} {a['lastName']}",
                'role': a['role'],
                'plan': a['plan'],
            })
        return advisors

    # COURSES

    def terms(self):
        return self.parsed['enrollmentTerms']

    @staticmethod
    def term_id(term):
        return term['termId']

    @staticmethod
    def term_name(term):
        return term['termName']

    def current_term(self):
        return next(filter(lambda t: self.term_name(t) == utils.get_current_term().name, self.terms()))

    @staticmethod
    def term_units_float(term):
        return f"{float(term['enrolledUnits'])}"

    def term_units(self, term):
        return self.formatted_units(term['enrolledUnits'])

    @staticmethod
    def term_units_max_float(term):
        return f"{float(term['maxTermUnitsAllowed'])}"

    def term_units_max(self, term):
        return self.formatted_units(term['maxTermUnitsAllowed'])

    @staticmethod
    def term_units_min_float(term):
        return f"{float(term['minTermUnitsAllowed'])}"

    def term_units_min(self, term):
        return self.formatted_units(term['minTermUnitsAllowed'])

    @staticmethod
    def term_gpa(term):
        return term['termGpa'] and term['termGpa']['gpa']

    @staticmethod
    def term_gpa_units(term):
        return term['termGpa'] and term['termGpa']['unitsTakenForGpa']

    @staticmethod
    def courses(term):
        return term['enrollments']

    @staticmethod
    def sections(course):
        return course['sections']

    @staticmethod
    def course_display_name(course):
        return course['displayName']

    @staticmethod
    def sis_section_data(section):
        return {
            'ccn': f"{section['ccn']}",
            'number': f"{section['sectionNumber']}",
            'component': section['component'],
            'units_completed': f"{section['units'].floor() if section['units'].floor() == section['units'] else section['units']}",
            'primary': section['primary'],
            'status': section['enrollmentStatus'],
            'incomplete_code': section['incompleteStatusCode'],
            'incomplete_frozen': section['incompleteFrozenFlag'],
            'incomplete_lapse_date': section['incompleteLapseGradeDate'],
        }

    def sis_course_data(self, course):
        reqts = course['courseRequirements'] and list(
            map(lambda req: re.sub(r'\s+', ' ', req), course['courseRequirements']))
        return {
            'code': self.course_display_name(course),
            'title': (re.sub(r'\s+', ' ', course['title'])),
            'units_completed_float': f"{float(course['units'])}",
            'units_completed': f"{course['units'].floor() if course['units'].floor() == course['units'] else course['units']}",
            'midpoint': (course['midtermGrade'] and course['midtermGrade'].replace('-', '−')),
            'grade': (course['grade'] and course['grade'].replace('-', '−')),
            'grading_basis': course['gradingBasis'],
            'reqts': reqts,
            'acad_career': course['academicCareer'],
        }

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

    def course_section_ccns(self, course):
        return list(map(lambda s: self.sis_section_data(s)['ccn'], self.sections(course)))

    def course_primary_section(self, course):
        return next(filter(lambda s: self.sis_section_data(s)['primary'], self.sections(course)))

    @staticmethod
    def dropped_sections(term):
        sections = []
        section_data = term['droppedSections'] or []
        for s in section_data:
            sections.append({
                'title': s['displayName'],
                'component': s['component'],
                'number': s['sectionNumber'],
                'date': s['dropDate'],
            })
        return sections

    # REGISTRATIONS

    def term_registration(self):
        reg_data = self.sis_profile()['currentRegistration']
        if reg_data:
            begin_term = reg_data['academicLevels'] and next(
                filter(lambda level: level['type']['code'] == 'BOT', reg_data['academicLevels']))
            end_term = reg_data['academicLevels'] and next(
                filter(lambda level: level['type']['code'] == 'EOT', reg_data['academicLevels']))
            return {
                'term_id': reg_data['term']['id'],
                'career': reg_data['academicCareer']['code'],
                'begin_term': (begin_term and begin_term['level']['description']),
                'end_term': (end_term and end_term['level']['description']),
            }

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
            'code': site['courseCode'],
            'title': site['courseName'],
            'site_id': site['canvasCourseId'],
        }

    @staticmethod
    def analytics(site):
        return site['analytics']

    def site_scores(self, site):
        return self.analytics(site) and self.analytics(site)['courseCurrentScore']

    @staticmethod
    def student_data(analytics):
        return analytics['student']

    @staticmethod
    def course_deciles(analytics):
        return analytics['courseDeciles']

    def score(self, analytics):
        score = self.student_data(analytics) and self.student_data(analytics)['raw']
        if score and score == score.floor():
            return f'{score.floor()}'
        else:
            return f'{score}'

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
        return self.site_statistics(self.analytics(site))['assignmentsSubmitted'].update(
            {'type': 'Assignments Submitted'})

    def assignment_grades(self, site):
        return self.site_statistics(self.analytics(site))['currentScore'].update({'type': 'Assignment Grades'})

    def last_activity_day(self, site):
        epoch = self.site_statistics(self.analytics(site)['lastActivity'])['score']
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
        for term in self.terms():
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

    # TIMELINE

    def notifications(self):
        return self.parsed['notifications']

    def alerts(self, opts=None):
        alerts = self.notifications() and list(map(lambda a: a['message'], self.notifications()['alert']))
        if alerts and opts and opts['exclude_canvas']:
            for a in alerts:
                if 'activity!' in a:
                    alerts.remove(a)
        return alerts

    def holds(self):
        return self.notifications() and list(map(lambda h: h['message'], self.notifications()['hold']))

    def notes(self):
        notes = []
        note_data = (self.notifications() and self.notifications()['note']) or []
        for n in note_data:
            author = n['author']
            advisor = author and User({
                'uid': author['uid'],
                'full_name': author['name'],
                'email': author['email'],
                'depts': (list(map(lambda d: d['name'], author['departments']))),
            })
            attachments = n['attachments'] and list(map(lambda f: f['filename'] or f['sisFilename'], n['attachments']))
            attachments = [a for a in attachments if a]
            topics = n['topics'] or []
            topics.sort()
            notes.append(Note({
                'advisor': advisor,
                'attachments': attachments,
                'body': (n['body'] or ''),
                'created_date': n['createdAt'],
                'record_id': f"{n['id']}",
                'subject': (n['subject'] or ''),
                'topics': topics,
                'updated_date': n['updatedAt'],
            }))
        return notes

    def appointments(self):
        appts = []
        appt_data = (self.notifications() and self.notifications()['appointment']) or []
        for a in appt_data:
            author = a['advisor']
            advisor = author and User({
                'uid': author['uid'],
                'full_name': author['name'],
                'depts': author['departments'],
            })
            attachments = a['attachments'] and list(map(lambda f: f['filename'] or f['sisFilename'], a['attachments']))
            attachments = [a for a in attachments if a]
            appts.append(Appointment({
                'advisor': advisor,
                'attachments': attachments,
                'created_date': a['createdAt'],
                'detail': (a['details'] or ''),
                'record_id': f"{a['id']}",
                'subject': (a['appointmentTitle'] or ''),
                'updated_date': a['updatedAt'],
            }))
        return appts
