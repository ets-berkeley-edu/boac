"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


from boac.lib.http import tolerant_jsonify
from boac.models.alert import Alert
from boac.models.student import Student
from flask import current_app as app
from flask_login import current_user, login_required


@app.route('/api/watchlist/my')
@login_required
def my_watchlist():
    watchlist = [student.to_api_json() for student in current_user.watchlist]
    watchlist_by_sid = {student['sid']: student for student in watchlist}
    alert_counts = Alert.current_alert_counts_for_sids(current_user.id, list(watchlist_by_sid.keys()))
    for result in alert_counts:
        watchlist_by_sid[result['sid']].update({
            'alertCount': result['alertCount'],
        })
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
