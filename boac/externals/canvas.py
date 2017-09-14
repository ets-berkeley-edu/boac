import urllib

from boac.lib import http
from boac.lib.mockingbird import fixture
from flask import current_app as app


@fixture('canvas_user_for_uid_{uid}')
def get_user_for_uid(canvas_instance, uid, mock=None):
    url = build_url(canvas_instance, '/api/v1/users/sis_login_id:{}'.format(uid))
    with mock(url):
        return authorized_request(canvas_instance, url)


@fixture('canvas_user_courses_{uid}')
def get_user_courses(canvas_instance, uid, mock=None):
    path = '/api/v1/users/sis_login_id:{}/courses'.format(uid)
    response = paged_request(canvas_instance, path, mock)
    if not response:
        return response

    def include_course(course):
        # For now, keep things simple by including only student enrollments for the current term as defined in app
        # config.
        if course.get('enrollment_term_id') != app.config.get('CANVAS_CURRENT_ENROLLMENT_TERM'):
            return False
        if not course['enrollments'] or not next((e for e in course['enrollments'] if e['type'] == 'student'), None):
            return False
        return True
    return [course for course in response if include_course(course)]


@fixture('canvas_student_summaries_for_course_{course_id}')
def get_student_summaries(canvas_instance, course_id, mock=None):
    path = '/api/v1/courses/{}/analytics/student_summaries'.format(course_id)
    return paged_request(canvas_instance, path, mock)


def build_url(canvas_instance, path, query=None):
    encoded_query = urllib.parse.urlencode(query, doseq=True) if query else ''
    return urllib.parse.urlunparse([
        canvas_instance.scheme,
        canvas_instance.domain,
        urllib.parse.quote(path),
        '',
        encoded_query,
        '',
    ])


def authorized_request(canvas_instance, url):
    auth_headers = {'Authorization': 'Bearer {}'.format(canvas_instance.token)}
    return http.request(url, auth_headers)


def paged_request(canvas_instance, path, mock):
    url = build_url(
        canvas_instance,
        path,
        {'per_page': 100},
    )
    results = []
    while url:
        with mock(url):
            response = authorized_request(canvas_instance, url)
            if not response:
                return response
            results.extend(response.json())
            url = http.get_next_page(response)
    return results
