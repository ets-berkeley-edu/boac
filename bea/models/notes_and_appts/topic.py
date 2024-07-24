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

from enum import Enum

from bea.test_utils import utils


class Topic(object):

    def __init__(self, data):
        self.data = data

    @property
    def topic_id(self):
        return utils.safe_key(self.data, 'topic_id')

    @topic_id.setter
    def topic_id(self, value):
        self.data['topic_id'] = value

    @property
    def name(self):
        return utils.safe_key(self.data, 'name')

    @name.setter
    def name(self, value):
        self.data['name'] = value


class Topics(Enum):

    ACADEMIC_DIFFICULTY = {'name': 'Academic Difficulty'}
    ACADEMIC_INTERESTS = {'name': 'Academic Interests'}
    ACADEMIC_PLAN = {'name': 'Academic Plan'}
    ACADEMIC_PROGRESS = {'name': 'Academic Progress'}
    ACADEMIC_PROGRESS_RPT = {'name': 'Academic Progress Report (APR)'}
    ACADEMIC_SUPPORT = {'name': 'Academic Support'}
    ADVISING_HOLDS = {'name': 'Advising Holds'}
    AP_IB_GCE_TEST_UNITS = {'name': 'AP/IB/GCE test units'}
    BREADTH_REQTS = {'name': 'Breadth requirement(s)'}
    CAREER_INTERNSHIP = {'name': 'Career/Internship'}
    CHANGE_GRADING_OPTION = {'name': 'Change Grading Option'}
    CHANGE_OF_COLLEGE = {'name': 'Change of College'}
    CHANGE_OF_MAJOR = {'name': 'Change of Major'}
    COCI = {'name': 'COCI'}
    CONCURRENT_ENROLLMENT = {'name': 'Concurrent Enrollment'}
    CONTINUED_AFTER_DISMISSAL = {'name': 'Continued After Dismissal'}
    COURSE_ADD = {'name': 'Course Add'}
    COURSE_DROP = {'name': 'Course Drop'}
    COURSE_GRADE_OPTION = {'name': 'Course Grade Option'}
    COURSE_SELECTION = {'name': 'Course Selection'}
    COURSE_UNIT_CHANGE = {'name': 'Course Unit Change'}
    CURRENTLY_DISMISSED_PLANNING = {'name': 'Currently Dismissed/Planning'}
    DEAN_APPT = {'name': 'Dean Appointment'}
    DEGREE_CHECK = {'name': 'Degree Check'}
    DEGREE_CHECK_PREP = {'name': 'Degree Check Preparation'}
    DEGRESS_REQTS = {'name': 'Degree Requirements'}
    DISMISSAL = {'name': 'Dismissal'}
    DOUBLE_MAJOR = {'name': 'Double Major'}
    EAP = {'name': 'Education Abroad Program (EAP)'}
    EAP_RECIPROCITY = {'name': 'Education Abroad Program (EAP) Reciprocity'}
    EDUCATIONAL_GOALS = {'name': 'Educational Goals'}
    ELIGIBILITY = {'name': 'Eligibility'}
    ENROLLING_ANOTHER_SCHOOL = {'name': 'Enrolling At Another School'}
    EVAL_COURSES_ELSEWHERE = {'name': 'Evaluation of course(s) taken elsewhere'}
    EXCESS_UNITS = {'name': 'Excess Units'}
    FINANCIAL_AID_BUDGETING = {'name': 'Financial Aid/Budgeting'}
    GRADUATION_CHECK = {'name': 'Graduation Check'}
    GRADUATION_PLAN = {'name': 'Graduation Plan'}
    GRADUATION_PROGRESS = {'name': 'Graduation Progress'}
    INCOMPLETES = {'name': 'Incompletes'}
    JOINT_MAJOR = {'name': 'Joint Major'}
    LATE_ENROLLMENT = {'name': 'Late Enrollment'}
    MAJORS = {'name': 'Majors'}
    MIN_UNIT_PROGRAM = {'name': 'Minimum Unit Program'}
    MINORS = {'name': 'Minors'}
    PASS_NO_PASS = {'name': 'Pass / Not Pass (PNP)'}
    PERSONAL = {'name': 'Personal'}
    PETITION = {'name': 'Petition'}
    POST_GRADUATION = {'name': 'Post-Graduation'}
    PRE_MED_PRE_HEALTH = {'name': 'Pre-Med/Pre-Health'}
    PREMED_PRE_HEALTH_ADVISING = {'name': 'Premed/Pre-Health Advising'}
    PROBATION = {'name': 'Probation'}
    PROCTORING = {'name': 'Proctoring'}
    PROGRAM_PLANNING = {'name': 'Program Planning'}
    READING_AND_COMP = {'name': 'Reading & Composition'}
    READMISSION = {'name': 'Readmission'}
    READMISSION_AFTER_DISMISSAL = {'name': 'Readmission After Dismissal'}
    REFER_TO_ACAD_DEPT = {'name': 'Refer to Academic Department'}
    REFER_TO_CAREER_CENTER = {'name': 'Refer to Career Center'}
    REFER_TO_RESOURCES = {'name': 'Refer to Resources'}
    REFER_TO_TANG_CENTER = {'name': 'Refer to The Tang Center'}
    REQUIREMENTS = {'name': 'Requirements'}
    RESEARCH = {'name': 'Research'}
    RETROACTIVE_ADD = {'name': 'Retroactive Add'}
    RETROACTIVE_DROP = {'name': 'Retroactive Drop'}
    RETROACTIVE_UNIT_CHANGE = {'name': 'Retroactive Unit Change'}
    RETROACTIVE_WITHDRAWAL = {'name': 'Retroactive Withdrawal'}
    SAP = {'name': 'SAP'}
    SAT_ACAD_PROGRESS_APPEAL = {'name': 'Satisfactory Academic Progress (SAP) Appeal'}
    SCHEDULE_PLANNING_LATE_ACTION = {'name': 'Schedule Planning, Late Action'}
    SCHEDULING = {'name': 'Scheduling'}
    SEMESTER_OUT_RULE = {'name': 'Semester Out Rule'}
    SENIOR_RESIDENCY = {'name': 'Senior Residency'}
    SIMULTANEOUS_DEGREE = {'name': 'Simultaneous Degree'}
    SPECIAL_STUDIES = {'name': 'Special Studies'}
    STUDENT_CONDUCT = {'name': 'Student Conduct'}
    STUDY_ABROAD = {'name': 'Study Abroad'}
    TRANSFER_COURSEWORK = {'name': 'Transfer Coursework'}
    TRANSITION_SUPPORT = {'name': 'Transition Support'}
    TRAVEL_CONFLICTS = {'name': 'Travel Conflicts'}
    WAIVE_COLLECT_REQT = {'name': 'Waive College Requirement'}
    WITHDRAWAL = {'name': 'Withdrawal'}
    OTHER = {'name': 'Other / Reason not listed'}
