import logging
import os


# Base directory for the application (one level up from this config file).
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# The 'dist' version of index.html will force browsers to pick up new JS, HTML, CSS files
INDEX_HTML = 'dist/templates/index.html'

# Directory to search for mock fixtures, if running in "test" or "demo" mode.
FIXTURES_PATH = None

# Save DB changes at the end of a request.
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

# Disable an expensive bit of the ORM.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# A common configuration; one request thread, one background worker thread.
THREADS_PER_PAGE = 2

# Some defaults.
CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'
# Used to encrypt session cookie.
SECRET_KEY = 'secret'

TIMEZONE = 'America/Los_Angeles'

# Override in local configs.
SQLALCHEMY_DATABASE_URI = 'postgres://boac:boac@localhost:5432/boac'

HOST = '0.0.0.0'
PORT = 5000

DEVELOPER_AUTH_ENABLED = False
DEVELOPER_AUTH_PASSWORD = 'another secret'

# Set to a nice long chaotic string to enable scripted access to APIs.
API_KEY = None

CAS_SERVER = 'https://auth-test.berkeley.edu/cas/'
CAS_LOGOUT_URL = 'https://auth-test.berkeley.edu/cas/logout'

# Enable with a valid Google id. For example, 'UA-999999999-1'
GOOGLE_ANALYTICS_ID = False

# Data Loch is treated as a readonly Postgres DB.
DATA_LOCH_URI = 'postgres://nessie:secret@secreturl.com:5432/canvas'

LDAP_HOST = 'nds-test.berkeley.edu'
LDAP_BIND = 'mybind'
LDAP_PASSWORD = 'secret'

# Canvas APIs
CANVAS_HTTP_URL = 'https://wottsamatta.instructure.com'
CANVAS_HTTP_TOKEN = 'yet another secret'

CANVAS_CURRENT_ENROLLMENT_TERM = 'Fall 2017'
CANVAS_EARLIEST_TERM = 'Fall 2016'

# SIS APIs
ATHLETE_API_ID = 'secretid'
ATHLETE_API_KEY = 'secretkey'
ATHLETE_API_URL = 'https://secreturl.berkeley.edu/athletes'

ENROLLMENTS_API_ID = 'secretid'
ENROLLMENTS_API_KEY = 'secretkey'
ENROLLMENTS_API_URL = 'https://secreturl.berkeley.edu/enrollments'

STUDENT_API_ID = 'secretid'
STUDENT_API_KEY = 'secretkey'
STUDENT_API_URL = 'https://secreturl.berkeley.edu/students'

DEGREE_PROGRESS_API_URL = 'https://secreturl.berkeley.edu/PSFT_CS'
DEGREE_PROGRESS_API_USERNAME = 'secretuser'
DEGREE_PROGRESS_API_PASSWORD = 'secretpassword'

CAL1CARD_PHOTO_API_URL = 'https://secreturl.berkeley.edu/photos'
CAL1CARD_PHOTO_API_USERNAME = 'secretuser'
CAL1CARD_PHOTO_API_PASSWORD = 'secretpassword'

ASC_ATHLETES_API_URL = 'https://secreturl.berkeley.edu/intensives.php?AcadYr=2017-18'
ASC_ATHLETES_API_KEY = 'secret'

# Logging
LOGGING_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOGGING_LOCATION = 'boac.log'
LOGGING_LEVEL = logging.DEBUG

# Caching (number of seconds, or false to disable)
CACHE_DEFAULT = False

# If the top decile of any analytics measure is below this number, treat it as zero ("no data").
# At the beginning of a term, the bar may be lowered.
MEANINGFUL_STATS_MINIMUM = 4
