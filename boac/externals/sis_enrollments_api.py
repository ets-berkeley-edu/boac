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


"""Official access to student enrollment data."""

from boac.lib import http
from boac.lib.mockingbird import fixture
from flask import current_app as app


def get_drops_and_midterms(cs_id, term_id):
    """Obtain dropped classes and midterm deficient grades for the term."""
    response = get_enrollments(cs_id, term_id)
    if not response:
        return response
    enrollments = response.get('studentEnrollments', [])
    dropped_classes = []
    midterm_grades = {}
    for enrollment in enrollments:
        enrollment_status = enrollment.get('enrollmentStatus', {}).get('status', {}).get('code')
        if enrollment_status == 'D' and enrollment.get('gradingBasis', {}).get('code') != 'NON':
            dropped_classes.append({
                'displayName': enrollment.get('classSection', {}).get('class', {}).get('course', {}).get('displayName'),
                'component': enrollment.get('classSection', {}).get('component', {}).get('code'),
                'sectionNumber': enrollment.get('classSection', {}).get('number'),
            })
        grades = enrollment.get('grades', [])
        midterm = next((grade.get('mark') for grade in grades if grade.get('type', {}).get('code') == 'MID'), None)
        if midterm:
            midterm_grades[enrollment['classSection']['id']] = midterm
    return {
        'droppedPrimarySections': dropped_classes,
        'midtermGrades': midterm_grades,
    }


def get_enrollments(cs_id, term_id):
    response = _get_enrollments(cs_id, term_id)
    if response and hasattr(response, 'json'):
        return response.json().get('apiResponse', {}).get('response', {})
    else:
        if hasattr(response, 'raw_response') and hasattr(response.raw_response, 'status_code') and response.raw_response.status_code == 404:
            return False
        else:
            return None


@fixture('sis_enrollments_api_{cs_id}_{term_id}')
def _get_enrollments(cs_id, term_id, mock=None):
    query = {
        'term-id': term_id,
        'page-size': 50,
    }
    url = http.build_url(app.config['ENROLLMENTS_API_URL'] + '/' + str(cs_id), query)
    with mock(url):
        return authorized_request(url)


def authorized_request(url):
    auth_headers = {
        'app_id': app.config['ENROLLMENTS_API_ID'],
        'app_key': app.config['ENROLLMENTS_API_KEY'],
        'Accept': 'application/json',
    }
    return http.request(url, auth_headers)
