from boac.api.util import canvas_courses_api_feed
from boac.externals import canvas
from boac.lib.analytics import mean_course_analytics_for_user
from boac.lib.http import tolerant_jsonify
from boac.models.cohort import Cohort

from flask import current_app as app, jsonify
from flask_login import login_required


@app.route('/api/cohorts')
@login_required
def cohorts_list():
    cohorts = Cohort.list_all()
    return jsonify(cohorts)


@app.route('/api/cohort/<cohort_code>')
@login_required
def cohort_details(cohort_code):
    cache_key = 'cohort/{cohort_code}'.format(cohort_code=cohort_code)
    cohort = app.cache.get(cache_key) if (app.cache) else None
    if cohort is None:
        cohort = Cohort.for_code(cohort_code)
        for member in cohort['members']:
            canvas_profile = canvas.get_user_for_uid(member['uid'])
            if canvas_profile:
                profile_json = canvas_profile.json()
                member['avatar_url'] = profile_json['avatar_url']
                canvas_courses = canvas_courses_api_feed(canvas.get_student_courses_in_term(member['uid']))
                if canvas_courses:
                    member['analytics'] = mean_course_analytics_for_user(canvas_courses, profile_json['id'])
        if app.cache:
            app.cache.set(cache_key, cohort)
    return tolerant_jsonify(cohort)
