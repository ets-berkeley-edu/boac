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
from boac.lib import util
from boac.lib.berkeley import get_dept_codes
from boac.lib.http import tolerant_jsonify
from boac.merged import athletics
from boac.merged.student import get_summary_student_profiles
from flask import current_app as app, request
from flask_login import current_user, login_required


def authorized():
    return current_user.is_admin or 'UWASC' in get_dept_codes(current_user)


@app.route('/api/team/<code>')
@login_required
def get_team(code):
    if not authorized():
        raise ResourceNotFoundError('Unknown path')
    order_by = util.get(request.args, 'orderBy', 'first_name')
    team = athletics.get_team(code, order_by)
    if team is None:
        raise ResourceNotFoundError('No team found with code ' + code)
    sids = [s['sid'] for s in team['students']]
    team['students'] = get_summary_student_profiles(sids)
    return tolerant_jsonify(team)


@app.route('/api/team_groups/all')
@login_required
def get_all_team_groups():
    # TODO: Give unauthorized user a 404 without disrupting COE advisors on the filtered-cohort view.
    data = athletics.all_team_groups() if authorized() else []
    return tolerant_jsonify(data)


@app.route('/api/teams/all')
@login_required
def get_all_teams():
    if not authorized():
        raise ResourceNotFoundError('Unknown path')
    return tolerant_jsonify(athletics.all_teams())
