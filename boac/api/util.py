"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


"""Utility module containing standard API-feed translations of data objects."""


def canvas_course_api_feed(course):
    return {
        'canvasCourseId': course.get('id'),
        'courseName': course.get('name'),
        'courseCode': course.get('course_code'),
        'courseTerm': course.get('term', {}).get('name'),
    }


def canvas_courses_api_feed(courses):
    if not courses:
        return []
    return [canvas_course_api_feed(course) for course in courses]


def sis_enrollment_class_feed(enrollment):
    class_data = enrollment.get('classSection', {}).get('class', {})
    return {
        'displayName': class_data.get('course', {}).get('displayName'),
        'title': class_data.get('course', {}).get('title'),
        'canvasSites': [],
        'sections': [],
    }


def sis_enrollment_section_feed(enrollment):
    section_data = enrollment.get('classSection', {})
    grades = enrollment.get('grades', [])
    return {
        'ccn': section_data.get('id'),
        'component': section_data.get('component', {}).get('code'),
        'sectionNumber': section_data.get('number'),
        'enrollmentStatus': enrollment.get('enrollmentStatus', {}).get('status', {}).get('code'),
        'units': enrollment.get('enrolledUnits', {}).get('taken'),
        'gradingBasis': translate_grading_basis(enrollment.get('gradingBasis', {}).get('code')),
        'grade': next((grade.get('mark') for grade in grades if grade.get('type', {}).get('code') == 'OFFL'), None),
        'midtermGrade': next((grade.get('mark') for grade in grades if grade.get('type', {}).get('code') == 'MID'), None),
    }


def student_to_json(student):
    return {
        'sid': student.sid,
        'uid': student.uid,
        'firstName': student.first_name,
        'lastName': student.last_name,
        'name': student.first_name + ' ' + student.last_name,
        'inIntensiveCohort': student.in_intensive_cohort,
        'isActiveAsc': student.is_active_asc,
        'statusAsc': student.status_asc,
    }


def translate_grading_basis(code):
    bases = {
        'CNC': 'C/NC',
        'EPN': 'P/NP',
        'ESU': 'S/U',
        'GRD': 'Letter',
        'LAW': 'Law',
        'PNP': 'P/NP',
        'SUS': 'S/U',
    }
    return bases.get(code) or code


def course_section_to_json(section):
    return {
        'termId': section.term_id,
        'sectionId': section.section_id,
        'deptName': section.dept_name,
        'deptCode': section.dept_code,
        'catalogId': section.catalog_id,
        'displayName': section.display_name,
        'title': section.title,
        'instructionFormat': section.instruction_format,
        'sectionNum': section.section_num,
        'units': section.units,
        'meetingDays': section.meeting_days,
        'meetingTimes': section.meeting_times,
        'locations': section.locations,
        'instructors': section.instructors,
    }
