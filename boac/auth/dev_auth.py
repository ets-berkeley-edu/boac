from boac.api.errors import ForbiddenRequestError, ResourceNotFoundError
from flask import (
    current_app as app, flash, redirect, request,
)
from flask_login import (
    login_required, login_user, logout_user,
)


@app.route('/devauth/login', methods=['GET', 'POST'])
def dev_login():
    logger = app.logger
    if app.config['DEVELOPER_AUTH_ENABLED']:
        if request.method == 'POST':
            if request.form['password'] != app.config['DEVELOPER_AUTH_PASSWORD']:
                logger.error('Wrong password entered in Developer Auth')
                raise ForbiddenRequestError('Wrong credentials')
            user_id = request.form['uid']
            user = app.login_manager.user_callback(user_id)
            if user is None:
                logger.error('Unauthorized user ID {} entered in Developer Auth'.format(user_id))
                raise ForbiddenRequestError('Unknown account')
            logger.info('Developer Auth used to log in as UID {}'.format(user_id))
            login_user(user)
            flash('Logged in successfully.')
            return redirect('/')
        else:
            return """
                <form method="post">
                    <p>UID: <input type=text name=uid>
                    <p>Password: <input type=password name=password>
                    <p><input type=submit value=Login>
                </form>
            """
    else:
        raise ResourceNotFoundError('Unknown path')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
