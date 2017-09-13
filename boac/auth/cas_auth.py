from boac.api.errors import ForbiddenRequestError
import cas
from flask import (
    current_app as app, flash, jsonify, redirect, request, url_for,
)
from flask_login import (
    login_required, login_user, logout_user,
)


@app.route('/cas/login_url', methods=['GET'])
def cas_login_url():
    return jsonify({
        'cas_login_url': _cas_client().get_login_url(),
    })


@app.route('/cas/callback', methods=['GET', 'POST'])
def cas_login():
    logger = app.logger
    ticket = request.args['ticket']
    user_id, attributes, proxy_granting_ticket = _cas_client().verify_ticket(ticket)
    logger.info('Logged into CAS as user {}'.format(user_id))
    user = app.login_manager.user_callback(user_id)
    if user is None:
        logger.error('Unauthorized UID {}'.format(user_id))
        raise ForbiddenRequestError('Unknown account')
    login_user(user)
    flash('Logged in successfully.')
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({
        'cas_logout_url': _cas_client().get_logout_url(redirect_url=request.url_root),
    })


def _cas_client():
    cas_server = app.config['CAS_SERVER']
    # One (possible) advantage this has over "request.base_url" is that it embeds the configured SERVER_NAME.
    service_url = url_for('.cas_login', _external=True)
    return cas.CASClientV3(server_url=cas_server, service_url=service_url)
