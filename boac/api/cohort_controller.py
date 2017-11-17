import json
from boac.api.errors import BadRequestError
from boac.api.errors import ForbiddenRequestError
from boac.api.util import canvas_courses_api_feed
from boac.externals import canvas
from boac.lib.analytics import mean_course_analytics_for_user
from boac.lib.http import tolerant_jsonify
from boac.models.cohort_filter import CohortFilter
from boac.models.team_member import TeamMember
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required


@app.route('/api/teams')
@login_required
def teams_list():
    return jsonify(TeamMember.all_teams())


@app.route('/api/cohorts/all')
@login_required
def all_cohorts():
    saved_cohorts = {}
    for cohort in CohortFilter.all():
        summary = summarize_list_item(cohort)
        for uid in summary['owners']:
            if uid not in saved_cohorts:
                saved_cohorts[uid] = []
            saved_cohorts[uid].append(summary)

    return jsonify(saved_cohorts)


@app.route('/api/cohorts/my')
@login_required
def my_cohorts():
    uid = current_user.get_id()
    cohorts = []
    for cohort in get_cohorts_owned_by(uid):
        cohorts.append(summarize_list_item(cohort))

    return jsonify(cohorts)


@app.route('/api/cohort/<code>')
@login_required
def get_cohort(code):
    if code.isdigit():
        cohort = summarize(CohortFilter.find_by_id(int(code)))
    else:
        cohort = get_team_details(code)

    return tolerant_jsonify(cohort)


@app.route('/api/cohort/create', methods=['POST'])
@login_required
def create_cohort():
    params = request.get_json()
    label = params['label']
    team_codes = params['team_codes']
    if not label or not team_codes:
        raise BadRequestError('Cohort creation requires \'label\' and \'teams\'')

    CohortFilter.create(label=label, team_codes=team_codes, uid=current_user.get_id())
    return jsonify({'message': 'Cohort created (label={})'.format(label)}), 200


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
            if app.cache:
                app.cache.delete(get_cache_key(cohort_id))
            return jsonify({'message': 'Cohort deleted (id={})'.format(cohort_id)}), 200
        else:
            raise BadRequestError('User {uid} does not own cohort_filter with id={id}'.format(uid=uid, id=cohort_id))
    else:
        raise ForbiddenRequestError('Programmatic deletion of teams is not supported (id={})'.format(cohort_id))


def get_cohort_owned_by(cohort_filter_id, uid):
    result = None
    # Cohort must exist and be owned by user
    for cohort in CohortFilter.all_owned_by(uid):
        if cohort_filter_id == cohort.id:
            result = summarize(cohort)
            break

    return result


def get_cohorts_owned_by(uid):
    cohorts = []
    # Cohort must exist and be owned by user
    for cohort in CohortFilter.all_owned_by(uid):
        cohorts.append(summarize(cohort))
    return cohorts


def summarize_list_item(cohort):
    member_count = 0
    team_codes = [team['code'] for team in cohort['teams']]
    for team_code in team_codes:
        team = TeamMember.for_code(team_code)
        member_count += len(team['members'])
    return {
        'id': cohort['id'],
        'label': cohort['label'],
        'memberCount': member_count,
        'owners': cohort['owners'],
    }


def summarize(cohort):
    members = []
    teams = []
    for code in get_team_codes(cohort):
        team = get_team_details(code)
        members += team['members']
        teams.append({
            'code': code,
            'name': team['name'],
        })
    # Create a serializable object
    return {
        'id': cohort.id,
        'label': cohort.label,
        'members': members,
        'memberCount': len(members),
        'owners': [user.uid for user in cohort.owners],
        'teams': teams,
    }


def get_team_codes(cohort):
    filter_criteria = json.loads(cohort.filter_criteria)
    return filter_criteria['teams']


def get_team_details(team_code):
    cache_key = get_cache_key(code=team_code)
    team = app.cache.get(cache_key) if app.cache else None
    if team is None:
        team = TeamMember.for_code(team_code)
        for member in team['members']:
            canvas_profile = canvas.get_user_for_uid(member['uid'])
            if canvas_profile:
                member['avatar_url'] = canvas_profile['avatar_url']
                canvas_courses = canvas_courses_api_feed(canvas.get_student_courses_in_term(member['uid']))
                if canvas_courses:
                    member['analytics'] = mean_course_analytics_for_user(canvas_courses, canvas_profile['id'])
        if app.cache:
            app.cache.set(cache_key, team)

    return team


def get_cache_key(code):
    return 'cohort/{code}'.format(code=code)
