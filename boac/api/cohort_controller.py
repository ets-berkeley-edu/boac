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
    cohort = Cohort.for_code(cohort_code)
    for member in cohort['members']:
        canvas_profile = canvas.get_user_for_uid(app.canvas_instance, member['uid'])
        if canvas_profile:
            member['analytics'] = mean_course_analytics_for_user(member['uid'], canvas_profile.json()['id'])
    return tolerant_jsonify(cohort)
