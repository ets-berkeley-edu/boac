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

import datetime
import itertools
import json

from bea.models.person import Person
from bea.models.section import Section
from bea.models.section import SectionEnrollment
from bea.models.section import SectionMeeting
from bea.models.student import Student
from bea.models.student_enrollment_data import EnrollmentData
from bea.models.student_profile_data import Profile
from bea.test_utils import utils
from boac.externals import data_loch
from flask import current_app as app


# STUDENTS

def get_all_students(opts=None):
    students = []
    if opts and opts.get('enrolled'):
        clause = f"""
                JOIN student.student_enrollment_terms
                  ON student.student_enrollment_terms.sid = student.student_profile_index.sid
               WHERE student.student_enrollment_terms.term_id = '{utils.get_current_term().code}'
        """
    elif opts and opts.get('include_inactive'):
        clause = ''
    else:
        clause = "WHERE student.student_profile_index.academic_career_status = 'active'"
    sql = f"""SELECT student.student_profile_index.uid AS uid,
                     student.student_profile_index.sid AS sid,
                     student.student_profile_index.first_name AS first_name,
                     student.student_profile_index.last_name AS last_name,
                     student.student_profile_index.email_address AS email,
                     student.student_profile_index.academic_career_status AS status
                FROM student.student_profile_index {clause}
            ORDER BY uid"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    for row in results:
        student = Student({
            'uid': row['uid'],
            'sid': row['sid'],
            'status': row['status'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'full_name': f"{row['first_name']} {row['last_name']}",
            'email': row['email'],
        })
        students.append(student)
    return students


def set_student_profiles(students):
    sids = utils.in_op([stud.sid for stud in students])
    sql = f"""SELECT sid,
                     profile
                FROM student.student_profiles
               WHERE sid IN ({sids})"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    for row in results:
        student = next(filter(lambda s: s.sid == row['sid'], students))
        profile = json.loads(row['profile'])
        student.profile_data = Profile(data=profile)


def set_student_term_enrollments(students):
    sids = utils.in_op([stud.sid for stud in students])
    sql = f"""SELECT sid,
                     term_id,
                     enrollment_term
                FROM student.student_enrollment_terms
               WHERE sid IN ({sids})
            ORDER BY term_id DESC"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    grouped = [list(result) for key, result in itertools.groupby(results, key=lambda r: r['sid'])]
    for group in grouped:
        enrollments = []
        student = next(filter(lambda s: s.sid == group[0]['sid'], students))
        for term in group:
            enrollments.append(json.loads(term['enrollment_term']))
        student.enrollment_data = EnrollmentData(data=enrollments)


def get_all_student_sids():
    sql = 'SELECT sid FROM student.student_profile_index ORDER BY sid ASC;'
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: r['sid'], results))


def get_sids_with_enrollments(term_id):
    sql = f"""SELECT sid
                FROM student.student_enrollment_terms
               WHERE enrolled_units > 0
                 AND term_id = '{term_id}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: r['sid'], results))


def get_sids_with_incomplete_grades(incomplete_grade, term_ids, frozen):
    terms = utils.in_op(term_ids)
    frozen_flag = 'Y' if frozen else 'N'
    sql = f"""SELECT sid
                FROM student.student_enrollment_terms
               WHERE term_id IN ({terms})
                 AND enrollment_term LIKE '%%"incompleteFrozenFlag": "{frozen_flag}"%%'
                 AND enrollment_term LIKE '%%"incompleteStatusCode": "{incomplete_grade.value['code']}"%%'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    sids = list(map(lambda r: r['sid'], results))
    app.logger.info(
        f"There are {len(sids)} students with incomplete status '{incomplete_grade.value['descrip']}' in terms {term_ids}")
    return sids


def get_sids_with_standing(standing, term):
    sql = f"""SELECT DISTINCT student.academic_standing.sid
                FROM student.academic_standing
               WHERE student.academic_standing.acad_standing_status = '{standing.value['code']}'
                 AND student.academic_standing.term_id = '{term.sis_id}';"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    sids = list(map(lambda r: r['sid'], results))
    app.logger.info(
        f"There are {len(sids)} students with academic standing '{standing.value['descrip']}' in term {term.name}")
    return sids


# ADMITS

def get_admits():
    admits = []
    sql = """SELECT cs_empl_id AS sid,
                    first_name AS first_name,
                    middle_name AS middle_name,
                    last_name AS last_name,
                    campus_email_1 AS email,
                    current_sir AS is_sir
               FROM boac_advising_oua.student_admits
           ORDER BY sid"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    for row in results:
        admit = Student({
            'sid': row['sid'],
            'first_name': row['first_name'],
            'middle_name': row['middle_name'],
            'last_name': row['last_name'],
            'email': row['email'],
            'is_sir': (row['is_sir'] == 'Yes'),
        })
        admits.append(admit)
    return admits


def get_admit_data(admit):
    sql = f"""SELECT *
                FROM boac_advising_oua.student_admits
               WHERE cs_empl_id = '{admit.sid}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    admit.admit_data = results[0]


def get_admit_data_update_date():
    sql = 'SELECT MAX(updated_at) FROM boac_advising_oua.student_admits'
    app.logger.info(sql)
    result = data_loch.safe_execute_rds(sql)[0]['max']
    return datetime.datetime.strftime(result, '%b %-d, %Y')


# ADVISORS

def get_academic_plans(advisor):
    sql = f"""SELECT DISTINCT boac_advisor.advisor_students.academic_plan_code AS plan_code
                FROM boac_advisor.advisor_students
                JOIN boac_advising_notes.advising_note_authors
                  ON boac_advising_notes.advising_note_authors.uid = '{advisor.uid}'
                 AND boac_advising_notes.advising_note_authors.sid = boac_advisor.advisor_students.advisor_sid
                JOIN student.student_profiles
                  ON student.student_profiles.sid = boac_advisor.advisor_students.student_sid
            ORDER BY boac_advisor.advisor_students.academic_plan_code"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return list(map(lambda r: r['plan_code'], results))


# SECTIONS


def get_sections(term, section_ids, primary_only=False):
    clause = ' AND sis_data.sis_sections.is_primary IS TRUE' if primary_only else ''
    sql = f"""SELECT sis_data.sis_sections.sis_section_id AS ccn,
                     sis_data.sis_sections.is_primary,
                     sis_data.sis_sections.sis_course_name AS code,
                     sis_data.sis_sections.sis_course_title AS title,
                     sis_data.sis_sections.sis_instruction_format AS format,
                     sis_data.sis_sections.sis_section_num AS number,
                     sis_data.sis_sections.instructor_uid AS uid,
                     sis_data.basic_attributes.first_name,
                     sis_data.basic_attributes.last_name,
                     sis_data.sis_sections.instruction_mode AS mode,
                     sis_data.sis_sections.meeting_location AS location,
                     sis_data.sis_sections.meeting_days AS days,
                     sis_data.sis_sections.meeting_start_date AS start_date,
                     sis_data.sis_sections.meeting_start_time AS start_time,
                     sis_data.sis_sections.meeting_end_time AS end_time
                FROM sis_data.sis_sections
                JOIN sis_data.basic_attributes
                  ON sis_data.sis_sections.instructor_uid = sis_data.basic_attributes.ldap_uid
               WHERE sis_data.sis_sections.sis_term_id = '{term.sis_id}'
                 AND sis_data.sis_sections.sis_section_id IN ({utils.in_op(section_ids)}){clause}
            ORDER BY sis_data.sis_sections.sis_course_name ASC,
                     sis_data.sis_sections.sis_instruction_format DESC,
                     sis_data.sis_sections.sis_section_num ASC"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)

    sections = []
    sorted_sections = sorted(results, key=lambda row: row['ccn'])
    section_groups = [list(result) for key, result in itertools.groupby(sorted_sections, key=lambda ro: ro['ccn'])]
    for section_group in section_groups:
        ccn = section_group[0]['ccn']
        code = section_group[0]['code']
        instruction_format = section_group[0]['format']
        is_primary = section_group[0]['is_primary']
        number = section_group[0]['number']
        title = section_group[0]['title']

        meetings = []
        sorted_meets = sorted(section_group, key=lambda sec: [sec['start_date'], sec['location']])
        meet_groups = [list(result) for key, result in itertools.groupby(sorted_meets,
                                                                         key=lambda ro: [ro['ccn'], ro['start_time'],
                                                                                         ro['location']])]
        for meet_group in meet_groups:
            instructors = []
            for meeting in meet_group:
                instructors.append(Person({'first_name': meeting['first_name'], 'last_name': meeting['last_name']}))
            mode = _parse_instruction_mode(meet_group[0]['mode'])
            days = _parse_meeting_days(meet_group[0]['days'])
            start_time = _parse_meeting_time(meet_group[0]['start_time'])
            end_time = _parse_meeting_time(meet_group[0]['end_time'])
            location = meet_group[0]['location']
            meetings.append(SectionMeeting(
                days=days,
                end_time=end_time,
                instructors=instructors,
                location=location,
                mode=mode,
                start_time=start_time,
            ))

        section = Section(
            ccn=ccn,
            code=code,
            instruction_format=instruction_format,
            is_primary=is_primary,
            meetings=meetings,
            number=number,
            term=term,
            title=title,
        )
        get_section_enrollment(section)
        sections.append(section)
    return sections


def get_section_enrollment(section, students=None):
    sql = f"""SELECT sis_data.sis_enrollments.ldap_uid AS uid,
                     sis_data.basic_attributes.sid,
                     sis_data.sis_enrollments.sis_enrollment_status AS status
                FROM sis_data.sis_enrollments
                JOIN sis_data.basic_attributes
                  ON sis_data.basic_attributes.ldap_uid = sis_data.sis_enrollments.ldap_uid
               WHERE sis_data.sis_enrollments.sis_section_id = '{section.ccn}'
                 AND sis_data.sis_enrollments.sis_term_id = '{section.term.sis_id}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    enrollments = []
    for row in results:
        if row['status'] == 'E':
            status = 'Enrolled'
        elif row['status'] == 'W':
            status = 'Waitlisted'
        else:
            status = None
        enrollments.append(SectionEnrollment(sid=row['sid'], status=status, uid=row['uid']))
    section.enrollments = enrollments


def _parse_instruction_mode(mode_code):
    if mode_code == 'EF':
        return 'Flexible'
    elif mode_code == 'EH':
        return 'Hybrid'
    elif mode_code == 'ER':
        return 'Remote'
    elif mode_code == 'O':
        return 'Online'
    elif mode_code == 'P':
        return 'In-person'
    elif mode_code == 'W':
        return 'Web-based'
    else:
        return f'({mode_code})'


def _parse_meeting_days(days_string):
    if days_string:
        converted_days = []
        days_of_week = [(days_string[i:i + 2]) for i in range(0, len(days_string), 2)]
        days_count = len(days_of_week)
        for day in days_of_week:
            if day == 'MO':
                converted_days.append('Monday' if days_count == 1 else 'Mon')
            elif day == 'TU':
                converted_days.append('Tuesday' if days_count == 1 else 'Tue')
            elif day == 'WE':
                converted_days.append('Wednesday' if days_count == 1 else 'Wed')
            elif day == 'TH':
                converted_days.append('Thursday' if days_count == 1 else 'Thu')
            elif day == 'FR':
                converted_days.append('Friday' if days_count == 1 else 'Fri')
            elif day == 'SA':
                converted_days.append('Saturday' if days_count == 1 else 'Sat')
            else:
                converted_days.append('Sunday' if days_count == 1 else 'Sun')
        converted_days = ', '.join(converted_days)
    else:
        converted_days = None
    return converted_days


def _parse_meeting_time(time_string):
    if time_string:
        return datetime.datetime.strptime(time_string, '%H:%M').strftime('%l:%M %p').lower().strip()
    else:
        return None
