from boac.api.errors import ResourceNotFoundError
import boac.api.util as api_util
from boac.lib.http import tolerant_jsonify
from boac.merged import member_details
from boac.models.athletics import Athletics
from boac.models.student import Student
from flask import current_app as app, jsonify, request
from flask_login import login_required


@app.route('/api/team/<code>')
@login_required
def get_team(code):
    order_by = api_util.get(request.args, 'orderBy', 'first_name')
    team = Athletics.get_team(code, order_by)
    if team is None:
        raise ResourceNotFoundError('No team found with code ' + code)
    member_details.merge_all(team['members'])
    return tolerant_jsonify(team)


@app.route('/api/team_groups/members')
@login_required
def get_team_groups_members():
    group_codes = request.args.getlist('groupCodes')
    order_by = api_util.get(request.args, 'orderBy', None)
    offset = api_util.get(request.args, 'offset', 0)
    limit = api_util.get(request.args, 'limit', 50)
    results = Student.get_students(group_codes, order_by, offset, limit)
    member_details.merge_all(results['students'])
    return jsonify({
        'members': results['students'],
        'totalMemberCount': results['totalStudentCount'],
    })


@app.route('/api/team_groups/all')
@login_required
def get_all_team_groups():
    return jsonify(Athletics.all_team_groups())


@app.route('/api/teams/all')
@login_required
def get_all_teams():
    return jsonify(Athletics.all_teams())
