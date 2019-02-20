"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.models.authorized_user import AuthorizedUser
from flask import jsonify, make_response, redirect, request
from flask_login import LoginManager


def register_routes(app):
    """Register app routes."""
    # Register authentication modules. This should be done before
    # any authentication-protected routes are registered.
    login_manager = LoginManager()
    login_manager.user_loader(AuthorizedUser.find_by_uid)
    login_manager.init_app(app)

    # Register API routes.
    import boac.api.admin_controller
    import boac.api.alerts_controller
    import boac.api.auth_controller
    import boac.api.cohort_controller
    import boac.api.config_controller
    import boac.api.course_controller
    import boac.api.curated_group_controller
    import boac.api.menu_controller
    import boac.api.notes_controller
    import boac.api.search_controller
    import boac.api.student_controller
    import boac.api.status_controller
    import boac.api.user_controller

    # Register error handlers.
    import boac.api.error_handlers

    @app.login_manager.unauthorized_handler
    def unauthorized_handler():
        return jsonify(success=False, data={'login_required': True}, message='Unauthorized'), 401

    # Unmatched API routes return a 404.
    @app.route('/api/<path:path>')
    def handle_unmatched_api_route(**kwargs):
        app.logger.error('The requested resource could not be found.')
        raise boac.api.errors.ResourceNotFoundError('The requested resource could not be found.')

    # Non-API routes are handled by the front end.
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def front_end_route(**kwargs):
        vue_base_url = app.config['VUE_LOCALHOST_BASE_URL']
        if vue_base_url:
            app.logger.debug(f'Redirecting to {vue_base_url}{request.full_path}')
            return redirect(vue_base_url + request.full_path)
        else:
            index_html = app.config['INDEX_HTML']
            app.logger.debug(f'The page at {request.full_path} will be served with INDEX_HTML={index_html}')
            return make_response(open(index_html).read())

    @app.after_request
    def after_api_request(response):
        if app.config['BOAC_ENV'] == 'development':
            # In development the response can be shared with requesting code from any local origin.
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.headers['Access-Control-Allow-Origin'] = app.config['VUE_LOCALHOST_BASE_URL']
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        if request.full_path.startswith('/api'):
            log_message = ' '.join([
                request.remote_addr,
                request.method,
                request.full_path,
                response.status,
            ])
            if response.status_code >= 500:
                app.logger.error(log_message)
            elif response.status_code >= 400:
                app.logger.warning(log_message)
            else:
                app.logger.debug(log_message)
        return response
