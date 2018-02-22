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


from boac import db
from boac.externals import data_loch
from boac.lib.http import tolerant_jsonify
from flask import current_app as app
from flask_login import current_user


@app.route('/api/ping')
def app_status():
    def db_status():
        try:
            db.session.execute('SELECT 1')
            return True
        except Exception:
            app.logger.exception('Database connection error')
            return False

    def data_loch_status():
        try:
            data_loch.execute('SELECT 1')
            return True
        except Exception:
            app.logger.exception('Data Loch connection error')
            return False

    resp = {
        'app': True,
        'db': db_status(),
        'data_loch': data_loch_status(),
    }
    return tolerant_jsonify(resp)


@app.route('/api/status')
def user_status():
    uid = current_user.get_id()
    authn_state = {
        'is_authenticated': current_user.is_authenticated,
        'is_active': current_user.is_active,
        'is_anonymous': current_user.is_anonymous,
        'uid': uid,
    }
    resp = {
        'authenticated_as': authn_state,
    }
    return tolerant_jsonify(resp)
