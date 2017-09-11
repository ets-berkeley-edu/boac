import urllib

from boac.lib import http
from boac.lib.mockingbird import fixture, mockable, mocking, paged_fixture


@mockable
def get_user_for_sis_id(canvas_instance, sis_id, mock=None):
    url = build_url(canvas_instance, '/api/v1/users/sis_user_id:UID:{}'.format(sis_id))
    with mock(url):
        return authorized_request(canvas_instance, url)


@mocking(get_user_for_sis_id)
def get_user_for_sis_id_fixture(canvas_instance, sis_id):
    return fixture('canvas_user_for_sis_id_{}.json'.format(sis_id))


@mockable
def get_student_summaries(canvas_instance, course_id, mock=None):
    url = build_url(
        canvas_instance,
        '/api/v1/courses/{}/analytics/student_summaries'.format(course_id),
        {'per_page': 100},
    )
    results = []
    while url:
        with mock(url):
            response = authorized_request(canvas_instance, url)
            if not response:
                return response
            results.extend(response.json())
            if response.links and 'next' in response.links:
                url = response.links['next'].get('url')
            else:
                url = None
    return results


@mocking(get_student_summaries)
def get_student_summaries_fixtures(canvas_instance, course_id):
    return paged_fixture('canvas_student_summaries_for_course_{}'.format(course_id))


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
