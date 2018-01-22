from boac.models.authorized_user import AuthorizedUser
from flask import make_response, request
import flask_login


def register_routes(app):
    """Register app routes."""
    # Register authentication modules. This should be done before
    # any authentication-protected routes are registered.
    login_manager = flask_login.LoginManager()
    login_manager.user_loader(AuthorizedUser.find_by_uid)
    login_manager.init_app(app)
    import boac.auth.dev_auth
    import boac.auth.cas_auth

    # Register API routes.
    import boac.api.admin_controller
    import boac.api.advisor_watchlist_controller
    import boac.api.athletics_controller
    import boac.api.cohort_controller
    import boac.api.config_controller
    import boac.api.status_controller
    import boac.api.user_controller

    # Register error handlers.
    import boac.api.error_handlers

    # Unmatched API routes return a 404.
    @app.route('/api/<path:path>')
    def handle_unmatched_api_route(**kwargs):
        app.logger.error('The requested resource could not be found.')
        raise boac.api.errors.ResourceNotFoundError('The requested resource could not be found.')

    # Non-API routes are handled by the front end.
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def front_end_route(**kwargs):
        return make_response(open(app.config['INDEX_HTML']).read())

    @app.after_request
    def log_api_requests(response):
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
