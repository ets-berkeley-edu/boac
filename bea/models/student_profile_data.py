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

from bea.models.notes_and_appts.appointment import Appointment
from bea.models.notes_and_appts.note import Note
from bea.models.user import User
from bea.test_utils import utils


class Profile(object):

    def __init__(self, data):
        self.data = data

    @property
    def profile(self):
        return self.data

    # Athletics Profile

    def asc_profile(self):
        return utils.safe_key(self.data, 'athleticsProfile')

    def asc_teams(self):
        if self.asc_profile():
            suffix = '' if self.asc_profile()['isActiveAsc'] else ' (Inactive)'
            return [f"{a['groupName']}{suffix}" for a in self.asc_profile()['athletics']]
        else:
            return None

    # CoE Profile

    def coe_profile(self):
        profile = utils.safe_key(self.data, 'coeProfile')
        return {
            'coe_advisor': utils.safe_key(profile, 'advisorUid'),
            'ethnicity': utils.safe_key(profile, 'ethnicity'),
            'coe_underrepresented_minority': utils.safe_key(profile, 'minority'),
            'coe_prep': utils.safe_key(profile, 'didPrep'),
            'prep_elig': utils.safe_key(profile, 'prepEligible'),
            't_prep': utils.safe_key(profile, 'didTprep'),
            't_prep_elig': utils.safe_key(profile, 'tprepEligible'),
        }

    # SIS Profile

    def sis_profile(self):
        return utils.safe_key(self.profile, 'sisProfile')

    def academic_career(self):
        return utils.safe_key(self.sis_profile(), 'academicCareer')

    def academic_career_status(self):
        return utils.safe_key(self.sis_profile(), 'academicCareerStatus')

    def cumulative_gpa(self):
        return '{:.3f}'.format(self.sis_profile()['cumulativeGPA']) if utils.safe_key(self.sis_profile(), 'cumulativeGPA') else '--'

    def cumulative_units(self):
        return utils.safe_key(self.sis_profile(), 'cumulativeUnits') and utils.formatted_units(self.sis_profile()['cumulativeUnits'])

    def degree_progress(self):
        profile = self.sis_profile()
        progress = utils.safe_key(profile, 'degreeProgress') and utils.safe_key(profile['degreeProgress'], 'requirements')
        return progress and {
            'date': progress['reportDate'],
            'writing': f"{progress['entryLevelWriting']['name']} {progress['entryLevelWriting']['status']}",
            'cultures': f"{progress['americanCultures']['name']} {progress['americanCultures']['status']}",
            'history': f"{progress['americanHistory']['name']} {progress['americanHistory']['status']}",
            'institutions': f"{progress['americanInstitutions']['name']} {progress['americanInstitutions']['status']}",
        }

    def email(self):
        return utils.safe_key(self.sis_profile(), 'emailAddress')

    def email_alternate(self):
        return utils.safe_key(self.sis_profile(), 'emailAddressAlternate')

    def entered_term(self):
        return utils.safe_key(self.sis_profile(), 'matriculation')

    def expected_grad_term_id(self):
        grad_term = utils.safe_key(self.sis_profile(), 'expectedGraduationTerm')
        return grad_term and grad_term['id']

    def expected_grad_term_name(self):
        grad_term = utils.safe_key(self.sis_profile(), 'expectedGraduationTerm')
        return grad_term and grad_term['name']

    def graduations(self):
        profile = self.sis_profile()
        graduations = []
        degrees = utils.safe_key(profile, 'degrees') or []
        for d in degrees:
            majors = []
            minors = []
            plans = utils.safe_key(d, 'plans') or []
            for p in plans:
                plan = utils.safe_key(p, 'plan')
                plan_type = utils.safe_key(p, 'type')
                if plan_type == 'MAJ':
                    majors.append({
                        'college': utils.safe_key(p, 'group'),
                        'plan': plan,
                    })
                elif plan_type == 'MIN':
                    minors.append({
                        'plan': plan.replace('Minor in ', ''),
                    })
            graduations.append({
                'date': (utils.safe_key(d, 'dateAwarded') and datetime.strptime(d['dateAwarded'], '%Y-%m-%d')),
                'degree': utils.safe_key(d, 'description'),
                'majors': majors,
                'minors': minors,
            })
        graduations.sort(key=lambda g: g['date'], reverse=True)
        return graduations

    def intended_majors(self):
        profile = self.sis_profile()
        intended_majors = []
        profile_majors = utils.safe_key(profile, 'intendedMajors') or []
        for m in profile_majors:
            if utils.safe_key(m, 'description'):
                intended_majors.append(m['description'])
        return intended_majors

    def level(self):
        return utils.safe_key(self.sis_profile(), 'level') and utils.safe_key(self.sis_profile()['level'], 'description')

    def majors(self):
        profile = self.sis_profile()
        majors = []
        if utils.safe_key(profile, 'plans'):
            for p in profile['plans']:
                majors.append({
                    'active': (p['status'] == 'Active'),
                    'college': p['program'],
                    'major': p['description'],
                    'status': p['status'],
                })
            majors.sort(key=lambda m: 0 if m['active'] else 1)
        return majors

    def majors_active(self):
        active_major_data = [m for m in self.majors() if m['active']]
        return list(map(lambda maj: maj['major'], active_major_data))

    def majors_discontinued(self):
        discontinued_major_data = [m for m in self.majors() if not m['active']]
        return list(map(lambda maj: maj['major'], discontinued_major_data))

    def colleges_active(self):
        active_major_data = [m for m in self.majors() if m['active']]
        return list(map(lambda maj: maj['college'], active_major_data))

    def colleges_discontinued(self):
        discontinued_major_data = [m for m in self.majors() if not m['active']]
        return list(map(lambda maj: maj['college'], discontinued_major_data))

    def minors(self):
        profile = self.sis_profile()
        minors = []
        if utils.safe_key(profile, 'plansMinor'):
            for p in profile['plansMinor']:
                minors.append({
                    'active': (p['status'] == 'Active'),
                    'college': p['program'],
                    'major': p['description'],
                    'status': p['status'],
                })
        return minors

    def minors_active(self):
        active_minor_data = [m for m in self.minors() if m['active']]
        return list(map(lambda minor: minor['minor'], active_minor_data))

    def minors_discontinued(self):
        active_minor_data = [m for m in self.minors() if not m['active']]
        return list(map(lambda minor: minor['minor'], active_minor_data))

    def name(self):
        return utils.safe_key(self.sis_profile(), 'primaryName')

    def preferred_name(self):
        return utils.safe_key(self.sis_profile(), 'preferredName')

    def phone(self):
        return utils.safe_key(self.sis_profile(), 'phoneNumber') and f"{self.sis_profile()['phoneNumber']}"

    def reqts(self):
        reqts = self.degree_progress()
        return {
            'reqt_writing': utils.safe_key(reqts, 'writing'),
            'reqt_history': utils.safe_key(reqts, 'history'),
            'reqt_institutions': utils.safe_key(reqts, 'institutions'),
            'reqt_cultures': utils.safe_key(reqts, 'cultures'),
        }

    def sub_plans(self):
        return self.sis_profile() and utils.safe_key(self.sis_profile(), 'subplans')

    def terms_in_attendance(self):
        return utils.safe_key(self.sis_profile(), 'termsInAttendance') and f"{self.sis_profile()['termsInAttendance']}"

    def transfer(self):
        return utils.safe_key(self.sis_profile(), 'transfer')

    def withdrawal(self):
        profile = self.sis_profile()
        withdrawal = utils.safe_key(profile, 'withdrawalCancel')
        return withdrawal and {
            'desc': withdrawal['description'],
            'reason': withdrawal['reason'],
            'date': datetime.strptime(withdrawal['date'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y'),
        }

    # Demographics

    def demographics(self):
        data = utils.safe_key(self.profile, 'demographics')
        if data:
            return {
                'ethnicities': data['ethnicities'],
                'nationalities': data['nationalities'],
                'underrepresented': data['underrepresented'],
                'visa': (utils.safe_key(data, 'visa') and {
                    'status': data['visa']['status'],
                    'type': data['visa']['type'],
                }),
            }

    # Advisors

    def advisor_plans(self):
        advisor_data = utils.safe_key(self.profile, 'advisors') or []
        return [a['plan'] for a in advisor_data]

    def advisor_names(self):
        advisor_data = utils.safe_key(self.profile, 'advisors') or []
        return [f"{a['firstName']} {a['lastName']}" for a in advisor_data]

    def advisor_emails(self):
        advisor_data = utils.safe_key(self.profile, 'advisors') or []
        return [a['email'] for a in advisor_data]

    def advisors(self):
        advisor_data = utils.safe_key(self.profile, 'advisors') or []
        advisors = []
        for a in advisor_data:
            advisors.append({
                'email': a['email'],
                'name': f"{a['firstName']} {a['lastName']}",
                'role': a['role'],
                'plan': a['plan'],
            })
        return advisors

    # REGISTRATIONS

    def term_registration(self):
        reg_data = utils.safe_key(self.sis_profile(), 'currentRegistration')
        if reg_data:
            begin_term = utils.safe_key(reg_data, 'academicLevels') and next(
                filter(lambda level: level['type']['code'] == 'BOT', reg_data['academicLevels']))
            end_term = utils.safe_key(reg_data, 'academicLevels') and next(
                filter(lambda level: level['type']['code'] == 'EOT', reg_data['academicLevels']))
            return {
                'term_id': reg_data['term']['id'],
                'career': reg_data['academicCareer']['code'],
                'begin_term': (begin_term and utils.safe_key(begin_term['level'], 'description')),
                'end_term': (end_term and utils.safe_key(end_term['level'], 'description')),
            }

    # TIMELINE

    def notifications(self):
        return utils.safe_key(self.profile, 'notifications')

    def alerts(self, opts=None):
        alerts = self.notifications() and list(map(lambda al: al['message'], self.notifications()['alert']))
        if alerts and opts and opts['exclude_canvas']:
            for a in alerts:
                if 'activity!' in a:
                    alerts.remove(a)
        return alerts

    def appointments(self):
        appts = []
        appt_data = (self.notifications() and utils.safe_key(self.notifications(), 'appointment')) or []
        for a in appt_data:
            author = utils.safe_key(a, 'advisor')
            advisor = author and User({
                'uid': author['uid'],
                'full_name': author['name'],
                'depts': author['departments'],
            })
            attachment_data = utils.safe_key(a, 'attachments') or []
            attachments = attachment_data and list(
                map(lambda f: utils.safe_key(f, 'filename') or utils.safe_key(f, 'sisFilename'), attachment_data))
            attachments = [a for a in attachments if a]
            appts.append(Appointment({
                'advisor': advisor,
                'attachments': attachments,
                'created_date': a['createdAt'],
                'detail': (utils.safe_key(a, 'details') or ''),
                'record_id': f"{a['id']}",
                'subject': (utils.safe_key(a, 'appointmentTitle') or ''),
                'updated_date': a['updatedAt'],
            }))
        return appts

    def holds(self):
        hold_data = self.notifications() and utils.safe_key(self.notifications(), 'hold') or []
        return self.notifications() and list(map(lambda h: h['message'], hold_data))

    def notes(self):
        notes = []
        note_data = (self.notifications() and utils.safe_key(self.notifications(), 'note')) or []
        for n in note_data:
            author = n['author']
            advisor = author and User({
                'uid': author['uid'],
                'full_name': author['name'],
                'email': author['email'],
                'depts': (list(map(lambda d: d['name'], author['departments']))),
            })
            attachment_data = utils.safe_key(n, 'attachments') or []
            attachments = attachment_data and list(
                map(lambda f: utils.safe_key(f, 'filename') or utils.safe_key(f, 'sisFilename'), attachment_data))
            attachments = [a for a in attachments if a]
            topics = utils.safe_key(n, 'topics') or []
            topics.sort()
            notes.append(Note({
                'advisor': advisor,
                'attachments': attachments,
                'body': (utils.safe_key(n, 'body') or ''),
                'created_date': n['createdAt'],
                'record_id': f"{n['id']}",
                'subject': (utils.safe_key(n, 'subject') or ''),
                'topics': topics,
                'updated_date': n['updatedAt'],
            }))
        return notes
