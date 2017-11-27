from boac.api.errors import ForbiddenRequestError, ResourceNotFoundError
from flask import (
    current_app as app, flash, redirect, request,
)
from flask_login import (
    login_user,
)


@app.route('/devauth/login', methods=['POST'])
def dev_login():
    if app.config['DEVELOPER_AUTH_ENABLED']:
        logger = app.logger
        params = request.get_json()
        if params['password'] != app.config['DEVELOPER_AUTH_PASSWORD']:
            logger.error('Wrong password entered in Developer Auth')
            raise ForbiddenRequestError('Wrong credentials')
        user_id = params['uid']
        user = app.login_manager.user_callback(user_id)
        if user is None:
            logger.error('Unauthorized user ID {} entered in Developer Auth'.format(user_id))
            raise ForbiddenRequestError('Unknown account')
        logger.info('Developer Auth used to log in as UID {}'.format(user_id))
        login_user(user)
        flash('Logged in successfully.')
        return redirect('/')
    else:
        raise ResourceNotFoundError('Unknown path')
