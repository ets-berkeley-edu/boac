from boac import db
from boac.configs import load_configs
from boac.logger import initialize_logger
from boac.routes import register_routes
from flask import Flask
from werkzeug.contrib.cache import SimpleCache


def create_app():
    """Initialize app with configs."""
    app = Flask(__name__.split('.')[0])

    load_configs(app)
    initialize_logger(app)
    db.init_app(app)
    initialize_cache(app)

    with app.app_context():
        register_routes(app)

    return app


def initialize_cache(app):
    """Baby's First Cache."""
    default = app.config['CACHE_DEFAULT']
    if (default):
        app.cache = SimpleCache(default_timeout=default)
    else:
        app.cache = None
    return app.cache
