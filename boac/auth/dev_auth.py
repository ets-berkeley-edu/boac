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
