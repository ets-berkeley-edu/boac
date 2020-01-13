"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.api.util import admin_or_director_required
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.http import tolerant_jsonify
from boac.models.university_dept_member import UniversityDeptMember
from flask import current_app as app
from flask_login import current_user


@app.route('/api/reports/boa_usage_summary/<dept_code>')
@admin_or_director_required
def boa_usage_summary(dept_code):
    dept_code = dept_code.upper()
    dept_name = BERKELEY_DEPT_CODE_TO_NAME.get(dept_code)
    if dept_name:
        if current_user.is_admin or _current_user_is_director_of(dept_code):
            return tolerant_jsonify({
                'dept': {
                    'code': dept_code,
                    'name': dept_name,
                },
            })
        else:
            raise ForbiddenRequestError(f'You are unauthorized to view {dept_name} reports')
    else:
        raise ResourceNotFoundError(f'Unrecognized department code {dept_code}')


@app.route('/api/reports/available_departments')
@admin_or_director_required
def available_dept_codes():
    if current_user.is_admin:
        dept_codes = UniversityDeptMember.get_distinct_departments()
    else:
        dept_codes = UniversityDeptMember.get_distinct_departments(
            authorized_user_id=current_user.get_id(),
            is_director=True,
        )

    def _to_json(row):
        dept_code = row.upper()
        return {
            'code': dept_code,
            'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code),
        }
    return tolerant_jsonify([_to_json(d) for d in dept_codes])


def _current_user_is_director_of(dept_code):
    departments = list(filter(lambda d: d['isDirector'], current_user.departments))
    return next((d for d in departments if d['code'] == dept_code), False)
