import json
from boac.api.errors import BadRequestError
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


@app.route('/api/cohort/<code>')
@login_required
def cohort_details(code):
    if code.isdigit():
        uid = current_user.get_id()
        cohort = get_cohort_filter_owned_by(int(code), uid)
    else:
        cohort = get_team_details(code)

    return tolerant_jsonify(cohort)


@app.route('/api/cohort/create', methods=['POST'])
@login_required
def create_cohort_filter():
    form = request.get_json()
    label = form['label']
    team_codes = form['team_codes']
    if not label or not team_codes:
        raise BadRequestError('create_cohort_filter requires \'label\' and \'teams\'')

    cohort_filter = CohortFilter.create(label=label, team_codes=team_codes)
    authorized_user.create_cohort_filter(cohort_filter, current_user.get_id())
    return jsonify({'message': 'cohort_filter created (label={})'.format(label)}), 200


@app.route('/api/cohort/delete/<code>', methods=['DELETE'])
@login_required
def delete_cohort_filter(code):
    cohort_filter_id = int(code)
    uid = current_user.get_id()
    cohort = get_cohort_filter_owned_by(cohort_filter_id, uid)
    if cohort:
        authorized_user.delete_cohort_filter(cohort_filter_id)
        if app.cache:
            app.cache.delete(get_cache_key(code))
        return jsonify({'message': 'cohort_filter deleted (id={})'.format(cohort_filter_id)}), 200
    else:
        raise BadRequestError('User {uid} does not own cohort_filter with id={code}'.format(uid=uid, code=code))


def get_cohort_filter_owned_by(cohort_filter_id, uid):
    cohort = None
    # Cohort must exist and be owned by user
    for cohort_filter in authorized_user.cohort_filters_owned_by(uid):
        if cohort_filter_id == cohort_filter.id:
            members = []
            # Extract team codes from filter_criteria
            filter_criteria = json.loads(cohort_filter.filter_criteria)
            team_codes = []
            for team_code in filter_criteria['teams']:
                team = get_team_details(team_code)
                members += team['members']
                team_codes.append(team_code)
            # Prepare the response
            cohort = {
                'code': cohort_filter.id,
                'name': cohort_filter.label,
                'members': members,
                'team_codes': team_codes,
            }
            break

    return cohort


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
