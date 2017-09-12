import importlib.util
import os


def load_configs(app):
    """
    On app creation, load and and override configs in the following order:
     - config/default.py
     - config/{BOAC_ENV}.py
     - {BOAC_LOCAL_CONFIGS}/{BOAC_ENV}-local.py (excluded from version control; sensitive values go here)
    """
    load_module_config(app, 'default')
    # BOAC_ENV defaults to 'development'.
    app_env = os.environ.get('BOAC_ENV', 'development')
    load_module_config(app, app_env)
    load_local_config(app, '{}-local.py'.format(app_env))
    app.config['BOAC_ENV'] = app_env
    app.canvas_instance = CanvasInstance(app)


def load_module_config(app, config_name):
    """Load an individual module-hosted configuration file if it exists."""
    config_path = 'config.{}'.format(config_name)
    if importlib.util.find_spec(config_path) is not None:
        app.config.from_object(config_path)


def load_local_config(app, config_name):
    """Load the local configuration file (if any) from a location outside the package."""
    configs_location = os.environ.get('BOAC_LOCAL_CONFIGS') or '../config'
    config_path = configs_location + '/' + config_name
    app.config.from_pyfile(config_path, silent=True)


class CanvasInstance(object):
    def __init__(self, app):
        self.scheme = app.config['CANVAS_HTTP_SCHEME']
        self.domain = app.config['CANVAS_HTTP_DOMAIN']
        self.token = app.config['CANVAS_HTTP_TOKEN']
