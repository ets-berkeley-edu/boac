import json
from boac.api.errors import BadRequestError
from boac.api.errors import ForbiddenRequestError
from boac.api.util import canvas_courses_api_feed
from boac.externals import canvas
from boac.lib.analytics import mean_course_analytics_for_user
from boac.lib.http import tolerant_jsonify
from boac.models import authorized_user
from boac.models.authorized_user import CohortFilter
from boac.models.team_member import TeamMember
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required


@app.route('/api/teams')
@login_required
def teams_list():
    return jsonify(TeamMember.list_all())


@app.route('/api/cohorts/my')
@login_required
def my_cohorts():
    uid = current_user.get_id()
    return jsonify(get_cohorts_owned_by(uid))


@app.route('/api/cohort/<code>')
@login_required
def get_cohort(code):
    if code.isdigit():
        uid = current_user.get_id()
        cohort = get_cohort_owned_by(int(code), uid)
    else:
        cohort = get_team_details(code)

    return tolerant_jsonify(cohort)


@app.route('/api/cohort/create', methods=['POST'])
@login_required
def create_cohort_filter():
    params = request.get_json()
    label = params['label']
    team_codes = params['team_codes']
    if not label or not team_codes:
        raise BadRequestError('create_cohort_filter requires \'label\' and \'teams\'')

    cohort_filter = CohortFilter.create(label=label, team_codes=team_codes)
    authorized_user.create_cohort_filter(cohort_filter, current_user.get_id())
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

    authorized_user.update_cohort(cohort_id=cohort['id'], label=label)
    return jsonify({'message': 'Cohort updated (label: {})'.format(label)}), 200


@app.route('/api/cohort/delete/<cohort_id>', methods=['DELETE'])
@login_required
def delete_cohort(cohort_id):
    if cohort_id.isdigit():
        cohort_id = int(cohort_id)
        uid = current_user.get_id()
        cohort = get_cohort_owned_by(cohort_id, uid)
        if cohort:
            authorized_user.delete_cohort(cohort_id)
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
    for cohort in authorized_user.load_cohorts_owned_by(uid):
        if cohort_filter_id == cohort.id:
            result = summarize(cohort)
            break

    return result


def get_cohorts_owned_by(uid):
    cohorts = []
    # Cohort must exist and be owned by user
    for cohort in authorized_user.load_cohorts_owned_by(uid):
        cohorts.append(summarize(cohort))
    return cohorts


def summarize(cohort):
    members = []
    # Extract team members per cohort team codes, etc.
    filter_criteria = json.loads(cohort.filter_criteria)
    teams = []
    for code in filter_criteria['teams']:
        team = get_team_details(code)
        members += team['members']
        teams.append({
            'code': code,
            'name': team['name'],
            'member_count': len(team['members']),
        })
    # Create a serializable object
    return {
        'id': cohort.id,
        'label': cohort.label,
        'members': members,
        'teams': teams,
    }


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
