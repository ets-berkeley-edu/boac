"""Utility module containing standard API-feed translations of data objects."""


def canvas_courses_api_feed(courses):
    if not courses:
        return []

    def course_api_values(course):
        return {
            'canvasCourseId': course.get('id'),
            'courseName': course.get('name'),
            'courseCode': course.get('course_code'),
            'courseTerm': course.get('term', {}).get('name'),
        }
    return [course_api_values(course) for course in courses]


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
