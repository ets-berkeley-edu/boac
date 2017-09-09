from boac.configs import load_configs
from boac.db import initialize_db
from boac.logger import initialize_logger
from boac.routes import register_routes
from flask import Flask


def create_app():
    """Initialize app with configs."""
    app = Flask(__name__.split('.')[0])

    load_configs(app)
    initialize_db(app)
    initialize_logger(app)

    with app.app_context():
        register_routes(app)

    return app
