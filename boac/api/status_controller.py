from boac import db
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
    resp = {
        'app': True,
        'db': db_status(),
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
