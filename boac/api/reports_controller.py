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
from flask import current_app as app
from flask_login import current_user


@app.route('/api/reports/boa_usage_summary/<dept_code>')
@admin_or_director_required
def boa_usage_summary(dept_code):
    dept_name = BERKELEY_DEPT_CODE_TO_NAME.get(dept_code and dept_code.upper())
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


def _current_user_is_director_of(dept_code):
    departments = list(filter(lambda d: d['isDirector'], current_user.departments))
    return next((d for d in departments if d['code'] == dept_code), False)
