"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.errors import ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import advisor_required
from boac.lib import util
from boac.lib.http import tolerant_jsonify
from boac.merged.sis_sections import get_sis_section
from boac.merged.student import get_course_student_profiles
from boac.models.alert import Alert
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/section/<term_id>/<section_id>')
@advisor_required
def get_section(term_id, section_id):
    if not current_user.can_access_canvas_data:
        raise ForbiddenRequestError('Unauthorized to view course data')
    offset = util.get(request.args, 'offset', None)
    if offset:
        offset = int(offset)
    limit = util.get(request.args, 'limit', None)
    if limit:
        limit = int(limit)
    featured = util.get(request.args, 'featured', None)
    section = get_sis_section(term_id, section_id)
    if not section:
        raise ResourceNotFoundError(f'No section {section_id} in term {term_id}')
    student_profiles = get_course_student_profiles(term_id, section_id, offset=offset, limit=limit, featured=featured)
    section.update(student_profiles)
    Alert.include_alert_counts_for_students(viewer_user_id=current_user.get_id(), group=student_profiles)
    return tolerant_jsonify(section)
