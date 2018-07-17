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
from boac.api.util import sort_students_by_name
from boac.externals import data_loch
from boac.lib.http import tolerant_jsonify
from boac.merged.sis_sections import get_sis_section
from boac.merged.student import get_student_query_scope, get_summary_student_profiles
from flask import current_app as app
from flask_login import login_required


@app.route('/api/section/<term_id>/<section_id>')
@login_required
def get_section(term_id, section_id):
    section = get_sis_section(term_id, section_id)
    if not section:
        raise ResourceNotFoundError(f'No section {section_id} in term {term_id}')
    sids = [str(r['sid']) for r in data_loch.get_sis_section_enrollments(term_id, section_id, get_student_query_scope())]
    students = get_summary_student_profiles(sids, section['termId'])
    for student in students:
        print(student)
        # Cherry-pick enrollment of section requested
        student_term = student.get('term')
        if not student_term:
            continue
        for enrollment in student_term.get('enrollments', []):
            _section = next((s for s in enrollment['sections'] if str(s['ccn']) == section_id), None)
            if _section:
                student['enrollment'] = {
                    'canvasSites': enrollment.get('canvasSites', None),
                    'enrollmentStatus': _section.get('enrollmentStatus', None),
                    'grade': enrollment.get('grade', None),
                    'gradingBasis': enrollment.get('gradingBasis', None),
                }
    section['students'] = sort_students_by_name(students)
    return tolerant_jsonify(section)
