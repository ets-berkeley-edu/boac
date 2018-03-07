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
from boac.lib.http import tolerant_jsonify
from boac.merged import member_details
from boac.models.normalized_cache_enrollment import NormalizedCacheEnrollment
from flask import current_app as app
from flask_login import login_required


@app.route('/api/section/<term_id>/<section_id>')
@login_required
def get_section(term_id, section_id):
    row = NormalizedCacheEnrollment.get_course_section(term_id=term_id, section_id=section_id)
    if not row:
        raise ResourceNotFoundError(f'No section {section_id} in term {term_id}')

    section = api_util.course_section_to_json(term_id=term_id, section=row)
    if 'students' in section:
        member_details.merge_all(section['students'], section['termId'])
    return tolerant_jsonify(section)


@app.route('/api/sections/ids_per_term')
@login_required
def summarize_sections_in_cache():
    return tolerant_jsonify(NormalizedCacheEnrollment.summarize_sections_in_cache())
