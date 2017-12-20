from boac.api.errors import ResourceNotFoundError
from boac.lib import util
from boac.lib.http import tolerant_jsonify
from boac.merged import member_details
from boac.models.athletics import Athletics
from flask import current_app as app, jsonify, request
from flask_login import login_required


@app.route('/api/team/<code>')
@login_required
def get_team(code):
    order_by = util.get(request.args, 'orderBy', 'first_name')
    team = Athletics.get_team(code, order_by)
    if team is None:
        raise ResourceNotFoundError('No team found with code ' + code)
    member_details.merge_all(team['members'])
    return tolerant_jsonify(team)


@app.route('/api/team_groups/all')
@login_required
def get_all_team_groups():
    return jsonify(Athletics.all_team_groups())


@app.route('/api/teams/all')
@login_required
def get_all_teams():
    return jsonify(Athletics.all_teams())
