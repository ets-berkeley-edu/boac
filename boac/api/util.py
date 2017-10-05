"""Utility module containing standard API-feed translations of data objects."""


def canvas_courses_api_feed(courses):
    if not courses:
        return []

    def course_api_values(course):
        return {
            'canvasCourseId': course.get('id'),
            'courseName': course.get('name'),
            'courseCode': course.get('course_code'),
        }
    return [course_api_values(course) for course in courses]


def sis_enrollment_api_feed(enrollment):
    sectionData = enrollment.get('classSection', {})
    classData = sectionData.get('class', {})
    grades = enrollment.get('grades', [])
    return {
        'ccn': sectionData.get('id'),
        'displayName': classData.get('course', {}).get('displayName'),
        'sectionNumber': classData.get('number'),
        'enrollmentStatus': enrollment.get('enrollmentStatus', {}).get('status', {}).get('code'),
        'units': enrollment.get('enrolledUnits', {}).get('taken'),
        'gradingBasis': enrollment.get('gradingBasis', {}).get('code'),
        'grade': next((grade.get('mark') for grade in grades if grade.get('type', {}).get('code') == 'OFFL'), None),
    }
