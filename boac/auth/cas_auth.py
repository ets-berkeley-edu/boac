from flask import (
    current_app as app, flash, redirect, request, url_for
)
from flask_login import (
    login_user
)
import cas

from boac.api.errors import ForbiddenRequestError


@app.route('/cas/login', methods=['GET', 'POST'])
def cas_login():
    logger = app.logger
    cas_server = app.config['CAS_SERVER']
    # One (possible) advantage this has over "request.base_url" is that it embeds the configured SERVER_NAME.
    cas_service_url = url_for('.cas_login', _external=True)
    client = cas.CASClientV3(
        server_url=cas_server,
        service_url=cas_service_url
    )
    if 'ticket' in request.args:
        ticket = request.args['ticket']
        user_id, attributes, proxy_granting_ticket = client.verify_ticket(ticket)
        logger.info('Logged into CAS as user {} with attributes {}'.format(user_id, repr(attributes)))
        user = app.login_manager.user_callback(user_id)
        if user is None:
            logger.error('Unauthorized UID {}'.format(user_id))
            raise ForbiddenRequestError('Unknown account')
        login_user(user)
        flash('Logged in successfully.')
        return redirect('/')
    else:
        cas_login = client.get_login_url()
        logger.info('Redirecting to ' + cas_login)
        return redirect(cas_login)
