from boac import db
from boac.configs import load_configs
from boac.logger import initialize_logger
from boac.routes import register_routes
from flask import Flask


def create_app():
    """Initialize app with configs."""
    app = Flask(__name__.split('.')[0])

    load_configs(app)
    initialize_logger(app)
    db.init_app(app)

    with app.app_context():
        register_routes(app)

    return app
