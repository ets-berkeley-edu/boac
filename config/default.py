import os
import logging


# Base directory.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Disable an expensive bit of the ORM.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# A common configuration; one request thread, one background worker thread.
THREADS_PER_PAGE = 2

# Some defaults.
CSRF_ENABLED = True
CSRF_SESSION_KEY = "secret"
# Used to encrypt session cookie.
SECRET_KEY = "secret"

# Override in local configs.
SQLALCHEMY_DATABASE_URI = 'postgres://boac:boac@localhost:5432/boac'

HOST = '0.0.0.0'
PORT = 5000

DEVELOPER_AUTH_ENABLED = False
DEVELOPER_AUTH_PASSWORD = "another secret"

CAS_SERVER = 'https://auth-test.berkeley.edu/cas/'

CANVAS_HTTP_SCHEME = 'https'
CANVAS_HTTP_DOMAIN = 'wottsamatta.instructure.com'
CANVAS_HTTP_TOKEN = 'yet another secret'

# Logging
LOGGING_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOGGING_LOCATION = 'boac.log'
LOGGING_LEVEL = logging.DEBUG
