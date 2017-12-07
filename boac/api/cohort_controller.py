from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.lib.http import tolerant_jsonify
from boac.models.cohort_filter import CohortFilter
from boac.models.team_member import TeamMember
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required


@app.route('/api/team/<code>')
@login_required
def get_team(code):
    order_by = get_param(request.args, 'orderBy', 'member_name')
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    team = TeamMember.get_team(code, order_by, offset, limit)
    if team is None:
        raise ResourceNotFoundError('No team found with code ' + code)
    # Translate requested order_by to naming convention of TeamMember
    sort_by = 'uid' if order_by == 'member_uid' else 'name'
    team['members'].sort(key=lambda member: member[sort_by])
    return tolerant_jsonify(team)


@app.route('/api/teams/all')
@login_required
def get_all_teams():
    return jsonify(TeamMember.all_teams())


@app.route('/api/team_groups/all')
@login_required
def get_all_team_groups():
    return jsonify(TeamMember.all_team_groups())


@app.route('/api/team_groups/members')
@login_required
def get_team_groups_members():
    team_group_codes = request.args.getlist('teamGroupCodes')
    order_by = get_param(request.args, 'orderBy', 'member_name')
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    return jsonify(TeamMember.get_athletes(team_group_codes, True, order_by, offset, limit))


@app.route('/api/cohorts/all')
@login_required
def all_cohorts():
    cohorts = {}
    for cohort in CohortFilter.all():
        for uid in cohort['owners']:
            if uid not in cohorts:
                cohorts[uid] = []
            cohorts[uid].append(cohort)
    return jsonify(cohorts)


@app.route('/api/cohorts/my')
@login_required
def my_cohorts():
    return jsonify(CohortFilter.all_owned_by(current_user.get_id()))


@app.route('/api/intensive_cohort')
@login_required
def get_intensive_cohort():
    order_by = get_param(request.args, 'orderBy', 'member_name')
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    return tolerant_jsonify(CohortFilter.get_intensive_cohort(order_by=order_by, offset=offset, limit=limit))


@app.route('/api/cohort/<cohort_id>')
@login_required
def get_cohort(cohort_id):
    order_by = get_param(request.args, 'orderBy', 'member_name')
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    cohort = CohortFilter.find_by_id(int(cohort_id), order_by, int(offset), int(limit))
    if not cohort:
        raise ResourceNotFoundError('No cohort found with identifier: {}'.format(cohort_id))
    return tolerant_jsonify(cohort)


@app.route('/api/cohort/create', methods=['POST'])
@login_required
def create_cohort():
    params = request.get_json()
    label = params['label']
    team_group_codes = params['teamGroupCodes']
    if not label or not team_group_codes:
        raise BadRequestError('Cohort creation requires \'label\' and \'teamGroupCodes\'')

    cohort = CohortFilter.create(label=label, team_group_codes=team_group_codes, uid=current_user.get_id())
    return tolerant_jsonify(cohort)


@app.route('/api/cohort/update', methods=['POST'])
@login_required
def update_cohort():
    params = request.get_json()
    uid = current_user.get_id()
    label = params['label']
    if not label:
        raise BadRequestError('Requested cohort label is empty or invalid')

    cohort = get_cohort_owned_by(params['id'], uid)
    if not cohort:
        raise BadRequestError('Cohort does not exist or is not owned by {}'.format(uid))

    CohortFilter.update(cohort_id=cohort['id'], label=label)
    return jsonify({'message': 'Cohort updated (label: {})'.format(label)}), 200


@app.route('/api/cohort/delete/<cohort_id>', methods=['DELETE'])
@login_required
def delete_cohort(cohort_id):
    if cohort_id.isdigit():
        cohort_id = int(cohort_id)
        uid = current_user.get_id()
        cohort = get_cohort_owned_by(cohort_id, uid)
        if cohort:
            CohortFilter.delete(cohort_id)
            return jsonify({'message': 'Cohort deleted (id={})'.format(cohort_id)}), 200
        else:
            raise BadRequestError('User {uid} does not own cohort_filter with id={id}'.format(uid=uid, id=cohort_id))
    else:
        raise ForbiddenRequestError('Programmatic deletion of canned cohorts is not allowed (id={})'.format(cohort_id))


def get_cohort_owned_by(cohort_filter_id, uid):
    return next((c for c in CohortFilter.all_owned_by(uid) if c['id'] == cohort_filter_id), None)


def get_param(params, key, default_value=None):
    return (params and key in params and params[key]) or default_value
