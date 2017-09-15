from boac.models import authorized_user
from flask import make_response
import flask_login


def register_routes(app):
    """Register app routes."""
    # Register authentication modules. This should be done before
    # any authentication-protected routes are registered.
    login_manager = flask_login.LoginManager()
    login_manager.user_loader(authorized_user.load_user)
    login_manager.init_app(app)
    import boac.auth.dev_auth
    import boac.auth.cas_auth

    # Register API routes.
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
        return make_response(open('boac/templates/index.html').read())
