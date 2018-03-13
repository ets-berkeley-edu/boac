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


from boac.api.errors import ResourceNotFoundError
import boac.api.util as api_util
from boac.lib import util
from boac.lib.http import tolerant_jsonify
from boac.merged import member_details
from boac.models.normalized_cache_enrollment import NormalizedCacheEnrollment
from flask import current_app as app, request
from flask_login import login_required


@app.route('/api/section/<term_id>/<section_id>')
@login_required
def get_section(term_id, section_id):
    row = NormalizedCacheEnrollment.get_course_section(term_id=term_id, section_id=section_id)
    if not row:
        raise ResourceNotFoundError(f'No section {section_id} in term {term_id}')
    section = api_util.course_section_to_json(term_id=term_id, section=row)
    students = section.get('students', [])
    member_details.merge_all(students, section['termId'])
    for student in students:
        # Cherry-pick enrollment of section requested
        for enrollment in student.get('term', {}).get('enrollments', []):
            if enrollment['displayName'] == section['displayName']:
                student['enrollment'] = enrollment
    if students and util.to_bool_or_none(request.args.get('includeAverage')):
        section['averageStudent'] = _get_average_student(students)
    return tolerant_jsonify(section)


@app.route('/api/sections/ids_per_term')
@login_required
def summarize_sections_in_cache():
    return tolerant_jsonify(NormalizedCacheEnrollment.summarize_sections_in_cache())


def _get_average_student(students):
    average_student = {
        'enrollment': {
            'gradingBasis': 'N/A',
        },
        'isClassAverage': True,
        'lastName': 'Class Average',
        'uid': 0,
    }
    canvas_sites = _get_canvas_sites(students)
    if canvas_sites:
        for canvas_site in canvas_sites:
            # TODO: student_summaries = canvas.get_student_summaries(canvas_site['canvasCourseId'], term_id)
            mock_deciles = [15, 52, 65, 81, 92, 105, 117, 132, 161, 226, 567]
            canvas_site['analytics'] = {
                'assignmentsOnTime': {
                    'courseDeciles': mock_deciles,
                    'displayPercentile': '56th',
                    'student': {
                        'raw': 81,
                    },
                },
                'courseCurrentScore': {
                    'courseDeciles': mock_deciles,
                    'boxPlottable': True,
                    'student': {
                        'raw': 79,
                    },
                },
                'pageViews': {
                    'courseDeciles': mock_deciles,
                    'boxPlottable': True,
                    'student': {
                        'raw': 148,
                    },
                },
            }
    else:
        average_student['warning'] = {
            'message': 'Average cannot be calculated.',
        }
    average_student['enrollment']['canvasSites'] = canvas_sites
    return average_student


def _get_canvas_sites(students):
    canvas_sites_dict = _get_canvas_sites_dict(students[0])
    for student in students[1:]:
        for course_id, canvas_site in _get_canvas_sites_dict(student).items():
            canvas_sites_dict[course_id] = canvas_site
    return list(canvas_sites_dict.values())


def _get_canvas_sites_dict(student):
    canvas_sites = student.get('enrollment', {}).get('canvasSites', [])
    return {str(canvas_site['canvasCourseId']): canvas_site for canvas_site in canvas_sites}
