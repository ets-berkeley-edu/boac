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


@app.route('/api/teams/members', methods=['POST'])
@login_required
def teams_members():
    params = request.get_json()
    team_codes = get_param(params, 'teamCodes', [])
    order_by = get_param(params, 'orderBy', 'member_name')
    offset = get_param(params, 'offset', 0)
    limit = get_param(params, 'limit', 50)
    return jsonify(TeamMember.summarize_team_members(team_codes, order_by, offset, limit))


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


@app.route('/api/cohort/<code>', methods=['POST'])
@login_required
def get_cohort(code):
    params = request.get_json()
    order_by = get_param(params, 'orderBy', 'member_name')
    offset = get_param(params, 'offset', 0)
    limit = get_param(params, 'limit', 50)
    if code.isdigit():
        cohort = CohortFilter.find_by_id(int(code), order_by, offset, limit)
    else:
        cohort = TeamMember.for_code(code, order_by, offset, limit)
        load_member_profiles(cohort)
        # Translate requested order_by to naming convention of TeamMember
        sort_by = 'uid' if order_by == 'member_uid' else 'name'
        cohort['members'].sort(key=lambda member: member[sort_by])

    return tolerant_jsonify(cohort)


@app.route('/api/cohort/create', methods=['POST'])
@login_required
def create_cohort():
    params = request.get_json()
    label = params['label']
    team_codes = params['teamCodes']
    if not label or not team_codes:
        raise BadRequestError('Cohort creation requires \'label\' and \'teams\'')

    cohort = CohortFilter.create(label=label, team_codes=team_codes, uid=current_user.get_id())
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
        raise ForbiddenRequestError('Programmatic deletion of teams is not supported (id={})'.format(cohort_id))


def get_cohort_owned_by(cohort_filter_id, uid):
    return next((c for c in CohortFilter.all_owned_by(uid) if c['id'] == cohort_filter_id), None)


def load_member_profiles(team):
    for member in team['members']:
        uid = member['uid']
        cache_key = 'user/{uid}'.format(uid=uid)
        canvas_profile = app.cache.get(cache_key) if app.cache else None
        if not canvas_profile:
            canvas_profile = canvas.get_user_for_uid(uid)
            # Cache Canvas profiles
            if app.cache and canvas_profile:
                app.cache.set(cache_key, canvas_profile)

        if canvas_profile:
            member['avatar_url'] = canvas_profile['avatar_url']
            student_courses = canvas.get_student_courses(uid)
            current_term = app.config.get('CANVAS_CURRENT_ENROLLMENT_TERM')
            student_courses_in_current_term = [course for course in student_courses if course.get('term', {}).get('name') == current_term]
            canvas_courses = canvas_courses_api_feed(student_courses_in_current_term)
            if canvas_courses:
                member['analytics'] = mean_course_analytics_for_user(canvas_courses, canvas_profile['id'], current_term)


def get_param(params, key, default_value=None):
    return (params and key in params and params[key]) or default_value
