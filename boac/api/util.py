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
    sectionData = enrollment.get('classSection', {})
    grades = enrollment.get('grades', [])
    return {
        'ccn': sectionData.get('id'),
        'component': sectionData.get('component', {}).get('code'),
        'sectionNumber': sectionData.get('number'),
        'enrollmentStatus': enrollment.get('enrollmentStatus', {}).get('status', {}).get('code'),
        'units': enrollment.get('enrolledUnits', {}).get('taken'),
        'gradingBasis': enrollment.get('gradingBasis', {}).get('code'),
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
    }


def get(_dict, key, default_value=None):
    value = _dict and key in _dict and _dict[key]
    return value or default_value
