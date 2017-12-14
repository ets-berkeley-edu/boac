from boac.models.athletics import Athletics
from flask import current_app as app, jsonify
from flask_login import login_required


@app.route('/api/team_groups/all')
@login_required
def get_all_team_groups():
    return jsonify(Athletics.all_team_groups())


@app.route('/api/teams/all')
@login_required
def get_all_teams():
    return jsonify(Athletics.all_teams())
