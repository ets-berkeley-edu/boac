from boac.externals import canvas
from flask import current_app as app, jsonify
from flask_login import current_user


@app.route('/api/status')
def app_status():
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

    if current_user.is_active:
        canvas_response = canvas.get_user_for_sis_id(app.canvas_instance, uid)
        if canvas_response:
            resp['canvas_profile'] = canvas_response.json()

    return jsonify(resp)
