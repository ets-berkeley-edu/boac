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
    app.logger.info(f"There are {len(sids)} students with incomplete status '{incomplete_grade.value['descrip']}' in terms {term_ids}")
    return sids


def get_sids_with_standing(standing, term):
    sql = f"""SELECT DISTINCT student.academic_standing.sid
                FROM student.academic_standing
               WHERE student.academic_standing.acad_standing_status = '{standing.value['code']}'
                 AND student.academic_standing.term_id = '{term.sis_id}';"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    sids = list(map(lambda r: r['sid'], results))
    app.logger.info(f"There are {len(sids)} students with academic standing '{standing.value['descrip']}' in term {term.name}")
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
