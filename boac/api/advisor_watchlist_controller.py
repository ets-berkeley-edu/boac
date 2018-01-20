from boac.lib.http import tolerant_jsonify
from boac.models.student import Student
from flask import current_app as app
from flask_login import current_user, login_required


@app.route('/api/watchlist/my')
@login_required
def my_watchlist():
    watchlist = [student.to_api_json() for student in current_user.watchlist]
    return tolerant_jsonify(sorted(watchlist, key=lambda s: (s['firstName'], s['lastName'])))


@app.route('/api/watchlist/add/<sid>')
@login_required
def add_to_watchlist(sid):
    student = Student.find_by_sid(sid)
    current_user.append_to_watchlist(student)
    return tolerant_jsonify({'message': f'SID {sid} added to watchlist of UID {current_user.uid}'}), 200


@app.route('/api/watchlist/remove/<sid>')
@login_required
def remove_from_watchlist(sid):
    current_user.remove_from_watchlist(sid)
    return tolerant_jsonify({'message': f'SID {sid} removed from watchlist of UID {current_user.uid}'}), 200
