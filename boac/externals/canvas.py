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


from boac.lib import http
from boac.lib.mockingbird import fixture
from boac.models.json_cache import stow
from flask import current_app as app


@stow('canvas_course_sections_{course_id}', for_term=True)
def get_course_sections(course_id, term_id):
    return _get_course_sections(course_id)


@fixture('canvas_course_sections_{course_id}')
def _get_course_sections(course_id, mock=None):
    path = f'/api/v1/courses/{course_id}/sections'
    return paged_request(path=path, mock=mock)


def get_student_courses(uid):
    all_canvas_courses = get_all_user_courses(uid)
    # The paged_request wrapper returns either a list of course sites or None to signal HTTP request failure.
    # An empty list should be handled by higher-level logic even though it's falsey.
    if all_canvas_courses is None:
        return None

    def include_course(course):
        include = False
        if course.get('enrollments'):
            blessed_states = ['active', 'completed', 'inactive']
            include = next(
                (e for e in course['enrollments'] if e['type'] == 'student' and e['enrollment_state'] in blessed_states),
                False,
            )
        return include

    return [course for course in all_canvas_courses if include_course(course)]


@stow('canvas_user_courses_{uid}')
def get_all_user_courses(uid):
    return _get_all_user_courses(uid)


@fixture('canvas_user_courses_{uid}')
def _get_all_user_courses(uid, mock=None):
    path = f'/api/v1/users/sis_login_id:{uid}/courses'
    query = {'include': ['term']}
    return paged_request(path=path, query=query, mock=mock)


def build_url(path, query=None):
    working_url = app.config['CANVAS_HTTP_URL'] + path
    return http.build_url(working_url, query)


def authorized_request(url):
    auth_headers = {'Authorization': 'Bearer {}'.format(app.config['CANVAS_HTTP_TOKEN'])}
    return http.request(url, auth_headers)


def paged_request(path, mock, query=None):
    if query is None:
        query = {}
    query['per_page'] = 100
    url = build_url(
        path,
        query,
    )
    results = []
    while url:
        with mock(url):
            response = authorized_request(url)
            if not response:
                return None
            results.extend(response.json())
            url = http.get_next_page(response)
    return results
