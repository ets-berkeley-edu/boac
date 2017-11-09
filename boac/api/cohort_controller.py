import json
from boac.api.util import canvas_courses_api_feed
from boac.externals import canvas
from boac.lib.analytics import mean_course_analytics_for_user
from boac.lib.http import tolerant_jsonify
from boac.models import authorized_user
from boac.models.team_member import TeamMember
from flask import current_app as app, jsonify
from flask_login import current_user, login_required


@app.route('/api/teams')
@login_required
def teams_list():
    return jsonify(TeamMember.list_all())


@app.route('/api/cohort/<cohort_code>')
@login_required
def cohort_details(cohort_code):
    cohort = None
    if cohort_code.isdigit():
        uid = current_user.get_id()
        cohort_filter_id = int(cohort_code)
        # Find matching cohort_filter owned by user
        for cohort_filter in authorized_user.cohort_filters_owned_by(uid):
            if cohort_filter_id == cohort_filter.id:
                members = []
                # Extract team codes from filter_criteria
                filter_criteria = json.loads(cohort_filter.filter_criteria)
                for team_code in filter_criteria['teams']:
                    team = get_team_details(team_code)
                    members.append(team['members'])
                # Prepare the response
                cohort = {
                    'code': cohort_filter.id,
                    'name': cohort_filter.label,
                    'members': members,
                }
    else:
        cohort = get_team_details(cohort_code)

    return tolerant_jsonify(cohort)


def get_team_details(team_code):
    cache_key = 'cohort/{team_code}'.format(team_code=team_code)
    cohort = app.cache.get(cache_key) if app.cache else None
    if cohort is None:
        cohort = TeamMember.for_code(team_code)
        for member in cohort['members']:
            canvas_profile = canvas.get_user_for_uid(member['uid'])
            if canvas_profile:
                member['avatar_url'] = canvas_profile['avatar_url']
                canvas_courses = canvas_courses_api_feed(canvas.get_student_courses_in_term(member['uid']))
                if canvas_courses:
                    member['analytics'] = mean_course_analytics_for_user(canvas_courses, canvas_profile['id'])
        if app.cache:
            app.cache.set(cache_key, cohort)

    return cohort
