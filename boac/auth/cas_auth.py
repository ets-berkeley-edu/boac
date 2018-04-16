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


from urllib.parse import urlencode

from boac.lib.http import add_param_to_url, tolerant_jsonify
import cas
from flask import (
    current_app as app, flash, redirect, request, url_for,
)
from flask_login import (
    login_required, login_user, logout_user,
)


@app.route('/cas/login_url', methods=['GET'])
def cas_login_url():
    target_url = request.referrer or None
    return tolerant_jsonify({
        'cas_login_url': _cas_client(target_url).get_login_url(),
    })


@app.route('/cas/callback', methods=['GET', 'POST'])
def cas_login():
    logger = app.logger
    ticket = request.args['ticket']
    target_url = request.args.get('url')
    uid, attributes, proxy_granting_ticket = _cas_client(target_url).verify_ticket(ticket)
    logger.info(f'Logged into CAS as user {uid}')
    user = app.login_manager.user_callback(uid)
    if user is None:
        logger.error(f'Unauthorized UID {uid}')
        param = ('casLoginError', f'Sorry, user with UID {uid} is unauthorized to use BOAC.')
        redirect_url = add_param_to_url('/', param)
    else:
        login_user(user)
        flash('Logged in successfully.')
        if not target_url:
            target_url = '/'
        # Our googleAnalyticsService uses 'casLogin' marker to track CAS login events
        redirect_url = add_param_to_url(target_url, ('casLogin', 'true'))
    return redirect(redirect_url)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return tolerant_jsonify({
        'cas_logout_url': _cas_client().get_logout_url(redirect_url=request.url_root),
    })


def _cas_client(target_url=None):
    cas_server = app.config['CAS_SERVER']
    # One (possible) advantage this has over "request.base_url" is that it embeds the configured SERVER_NAME.
    service_url = url_for('.cas_login', _external=True)
    if target_url:
        service_url = service_url + '?' + urlencode({'url': target_url})
    return cas.CASClientV3(server_url=cas_server, service_url=service_url)
