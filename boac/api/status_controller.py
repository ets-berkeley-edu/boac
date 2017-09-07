from flask import current_app as app, jsonify
from flask_login import current_user

@app.route('/api/status')
def app_status():
    authn_state = {
        'is_authenticated': current_user.is_authenticated,
        'is_active': current_user.is_active,
        'is_anonymous': current_user.is_anonymous,
        'uid': current_user.get_id()
    }
    # TODO Include Canvas profile if currently authenticated.
    return jsonify({
        'authenticated_as': authn_state
    })
