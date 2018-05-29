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
from boac.externals import data_loch
from boac.lib import analytics
from boac.lib import util
from boac.lib.http import tolerant_jsonify
from boac.merged import student_details
from boac.models.normalized_cache_enrollment import NormalizedCacheEnrollment
from flask import current_app as app, request
from flask_login import login_required


@app.route('/api/section/<term_id>/<section_id>')
@login_required
def get_section(term_id, section_id):
    section = NormalizedCacheEnrollment.get_course_section(term_id=term_id, section_id=section_id)
    if not section:
        raise ResourceNotFoundError(f'No section {section_id} in term {term_id}')
    students = section.get('students', [])
    student_details.merge_all(students, section['termId'])
    for student in students:
        # Cherry-pick enrollment of section requested
        student_term = student.get('term')
        if not student_term:
            continue
        for enrollment in student_term.get('enrollments', []):
            if enrollment['displayName'] == section['displayName']:
                student['enrollment'] = enrollment
    if students and util.to_bool_or_none(request.args.get('includeAverage')):
        section['averageStudent'] = {
            'canvasCourseId': 0,
            'cumulativeGPA': _get_student_average('cumulativeGPA', students),
            'cumulativeUnits': _get_student_average('cumulativeUnits', students),
            'enrollment': {
                'canvasSites': [],
                'grade': None,
                'gradingBasis': None,
            },
            'isClassAverage': True,
            'lastName': 'Class Average',
            'sid': 0,
            'uid': 0,
        }
        canvas_sites = _filter_canvas_sites_per_section_id(students, term_id, section_id)
        for canvas_site in canvas_sites:
            _analytics = analytics.get_student_averages(
                term_id=term_id,
                canvas_course_id=canvas_site['canvasCourseId'],
            )
            section['averageStudent']['enrollment']['canvasSites'].append({
                'analytics': _analytics,
                'canvasCourseId': canvas_site['canvasCourseId'],
                'courseCode': canvas_site['courseCode'],
                'courseName': canvas_site['courseName'],
                'courseTerm': canvas_site['courseTerm'],
            })
    return tolerant_jsonify(section)


@app.route('/api/sections/ids_per_term')
@login_required
def summarize_sections_in_cache():
    return tolerant_jsonify(NormalizedCacheEnrollment.summarize_sections_in_cache())


def _filter_canvas_sites_per_section_id(students, term_id, section_id):
    canvas_sites_dict = _canvas_sites_dict(students[0])
    for student in students[1:]:
        for course_id, canvas_site in _canvas_sites_dict(student).items():
            canvas_sites_dict[course_id] = canvas_site
    canvas_sites = []
    for canvas_site in list(canvas_sites_dict.values()):
        canvas_course_id = canvas_site['canvasCourseId']
        sections = data_loch.get_sis_sections_in_canvas_course(canvas_course_id, term_id)
        for section in sections:
            # Is this an official course section, linked to the SIS?
            if section['sis_section_id']:
                canvas_sites.append(canvas_site)
                break
    # Remove students' extraneous canvas sites
    canvas_course_ids = [s['canvasCourseId'] for s in canvas_sites]
    for student in students:
        sites = student.get('enrollment', {}).get('canvasSites', [])
        if sites:
            sites = [s for s in sites if s['canvasCourseId'] in canvas_course_ids]
            student['enrollment']['canvasSites'] = sites
    return canvas_sites


def _canvas_sites_dict(student):
    canvas_sites = student.get('enrollment', {}).get('canvasSites', [])
    return {str(canvas_site['canvasCourseId']): canvas_site for canvas_site in canvas_sites}


def _get_student_average(attribute, students):
    _students = [s for s in students if s.get(attribute)]
    sum(s[attribute] for s in _students) / len(_students) if _students else None
