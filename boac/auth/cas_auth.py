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


from boac.api.errors import ForbiddenRequestError
from boac.lib.http import tolerant_jsonify
import cas
from flask import (
    current_app as app, flash, redirect, request, url_for,
)
from flask_login import (
    login_required, login_user, logout_user,
)


@app.route('/cas/login_url', methods=['GET'])
def cas_login_url():
    return tolerant_jsonify({
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
    # The 'casLogin' marker is used by googleAnalyticsService to track CAS login events
    return redirect('/?casLogin=true')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return tolerant_jsonify({
        'cas_logout_url': _cas_client().get_logout_url(redirect_url=request.url_root),
    })


def _cas_client():
    cas_server = app.config['CAS_SERVER']
    # One (possible) advantage this has over "request.base_url" is that it embeds the configured SERVER_NAME.
    service_url = url_for('.cas_login', _external=True)
    return cas.CASClientV3(server_url=cas_server, service_url=service_url)
