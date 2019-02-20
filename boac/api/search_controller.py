"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

from itertools import islice

from boac.api.errors import BadRequestError, ForbiddenRequestError
from boac.api.util import add_alert_counts, is_unauthorized_search
from boac.externals.data_loch import get_enrolled_primary_sections
from boac.lib import util
from boac.lib.berkeley import current_term_id
from boac.lib.http import tolerant_jsonify
from boac.merged.student import search_advising_notes, search_for_students
from boac.models.alert import Alert
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/search', methods=['POST'])
@login_required
def search():
    params = util.remove_none_values(request.get_json())
    order_by = util.get(params, 'orderBy', None)
    if is_unauthorized_search(list(params.keys()), order_by):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    search_phrase = util.get(params, 'searchPhrase', '').strip()
    if not len(search_phrase):
        raise BadRequestError('Invalid or empty search input')
    domain = {
        'students': util.get(params, 'students'),
        'courses': util.get(params, 'courses'),
        'notes': util.get(params, 'notes'),
    }
    if not domain['students'] and not domain['courses'] and not domain['notes']:
        raise BadRequestError('No search domain specified')

    feed = {}

    if domain['students']:
        student_results = search_for_students(
            include_profiles=True,
            search_phrase=search_phrase.replace(',', ' '),
            order_by=order_by,
            offset=util.get(params, 'offset', 0),
            limit=util.get(params, 'limit', 50),
        )
        alert_counts = Alert.current_alert_counts_for_viewer(current_user.id)
        students = student_results['students']
        add_alert_counts(alert_counts, students)
        feed.update({
            'students': students,
            'totalStudentCount': student_results['totalStudentCount'],
        })

    if domain['courses']:
        alphanumeric_search_phrase = ''.join(e for e in search_phrase if e.isalnum()).upper()
        courses = []
        if alphanumeric_search_phrase:
            course_rows = get_enrolled_primary_sections(current_term_id(), alphanumeric_search_phrase)
            for row in islice(course_rows, 50):
                courses.append({
                    'termId': row['term_id'],
                    'sectionId': row['sis_section_id'],
                    'courseName': row['sis_course_name'],
                    'courseTitle': row['sis_course_title'],
                    'instructionFormat': row['sis_instruction_format'],
                    'sectionNum': row['sis_section_num'],
                    'instructors': row['instructors'],
                })
        else:
            course_rows = []
        feed['courses'] = courses
        feed['totalCourseCount'] = len(course_rows)

    if domain['notes']:
        notes_results = search_advising_notes(
            search_phrase=search_phrase,
            limit=20,
        )
        if notes_results:
            feed['notes'] = notes_results

    return tolerant_jsonify(feed)
