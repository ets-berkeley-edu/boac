"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from urllib.parse import urlencode, urljoin, urlparse

from boac.api.errors import ResourceNotFoundError
from boac.api.util import admin_required, get_current_user_profile
from boac.lib.http import add_param_to_url, tolerant_jsonify
from boac.merged.user_session import UserSession
from boac.models.authorized_user import AuthorizedUser
from boac.models.user_login import UserLogin
import cas
from flask import abort, current_app as app, flash, redirect, request, url_for
from flask_login import current_user, login_required, login_user, logout_user


@app.route('/cas/login_url', methods=['GET'])
def cas_login_url():
    target_url = request.referrer or None
    return tolerant_jsonify({
        'casLoginUrl': _cas_client(target_url).get_login_url(),
    })


@app.route('/cas/callback', methods=['GET', 'POST'])
def cas_login():
    logger = app.logger
    ticket = request.args['ticket']
    target_url = request.args.get('url')
    uid, attributes, proxy_granting_ticket = _cas_client(target_url).verify_ticket(ticket)
    logger.info(f'Logged into CAS as user {uid}')
    user_id = AuthorizedUser.get_id_per_uid(uid)

    if user_id is None:
        logger.error(f'UID {uid} is not an authorized user.')
        param = ('error', f"""
            Sorry, you are not registered to use BOA.
            Please <a href="mailto:{app.config['BOAC_SUPPORT_EMAIL']}">email us</a> for assistance.
        """)
        redirect_url = add_param_to_url('/', param)

    else:
        user = UserSession(user_id=user_id, flush_cached=True)
        if not user.is_active:
            logger.error(f'UID {uid} is in the BOA db but is not authorized to use the tool.')
            param = ('error', f"""
                Sorry, you are not registered to use BOA.
                Please <a href="mailto:{app.config['BOAC_SUPPORT_EMAIL']}">email us</a> for assistance.
            """)
            redirect_url = add_param_to_url('/', param)
        else:
            login_user(user)
            flash('Logged in successfully.')
            UserLogin.record_user_login(uid)

            # Check if url is safe for redirects per https://flask-login.readthedocs.io/en/latest/
            if not _is_safe_url(request.args.get('next')):
                return abort(400)
            if not target_url:
                target_url = '/'
            # Our googleAnalyticsService uses 'casLogin' marker to track CAS login events
            redirect_url = add_param_to_url(target_url, ('casLogin', 'true'))

    return redirect(redirect_url)


@app.route('/api/auth/dev_auth_login', methods=['POST'])
def dev_auth_login():
    params = request.get_json() or {}
    return _dev_auth_login(params.get('uid'), params.get('password'))


@app.route('/api/auth/become_user', methods=['POST'])
@admin_required
def become():
    _logout_user()
    params = request.get_json() or {}
    return _dev_auth_login(params.get('uid'), app.config['DEVELOPER_AUTH_PASSWORD'])


@app.route('/api/auth/logout')
@login_required
def logout():
    _logout_user()
    redirect_url = app.config['VUE_LOCALHOST_BASE_URL'] or request.url_root
    cas_logout_url = _cas_client().get_logout_url(redirect_url=redirect_url)
    return tolerant_jsonify({
        'casLogoutUrl': cas_logout_url,
        **current_user.to_api_json(),
    })


def _cas_client(target_url=None):
    cas_server = app.config['CAS_SERVER']
    # One (possible) advantage this has over "request.base_url" is that it embeds the configured SERVER_NAME.
    service_url = url_for('.cas_login', _external=True)
    if target_url:
        service_url = service_url + '?' + urlencode({'url': target_url})
    return cas.CASClientV3(server_url=cas_server, service_url=service_url)


def _dev_auth_login(uid, password):
    if app.config['DEVELOPER_AUTH_ENABLED']:
        logger = app.logger
        if password != app.config['DEVELOPER_AUTH_PASSWORD']:
            logger.error('Dev-auth: Wrong password')
            return tolerant_jsonify({'message': 'Invalid credentials'}, 401)
        user_id = AuthorizedUser.get_id_per_uid(uid)
        if user_id is None:
            logger.error(f'Dev-auth: User with UID {uid} is not registered in BOA.')
            return tolerant_jsonify({'message': f'Sorry, user with UID {uid} is not registered to use BOA.'}, 403)

        user = UserSession(user_id=user_id, flush_cached=True)
        if not user.is_active:
            logger.error(f'Dev-auth: UID {uid} is registered with BOA but not active.')
            return tolerant_jsonify({'message': f'Sorry, user with UID {uid} is not authorized to use BOA.'}, 403)
        logger.info(f'Dev-auth used to log in as UID {uid}')

        login_user(user, force=True, remember=True)
        UserLogin.record_user_login(uid)
        return tolerant_jsonify(get_current_user_profile())
    else:
        raise ResourceNotFoundError('Unknown path')


def _is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def _logout_user():
    if current_user:
        current_user.flush_cached()
    logout_user()
