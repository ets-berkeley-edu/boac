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
    return jsonify(cohort)
