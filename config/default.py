"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


import logging
import os


# Base directory for the application (one level up from this config file).
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# When BOAC is in demo-mode all student names and SIDs are blurred in the UI
DEMO_MODE = {
    'blur': False,
    'betaTesting': False,
}

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

# Data Loch Redshift and RDS are treated as readonly Postgres DBs.
DATA_LOCH_URI = 'postgres://nessie:secret@secreturl.com:5432/canvas'
DATA_LOCH_RDS_URI = 'postgres://nessie:secret@secret-rds-url.com:5432/canvas'

DATA_LOCH_ASC_SCHEMA = 'boac_advising_asc'
DATA_LOCH_BOAC_SCHEMA = 'boac_analytics'
DATA_LOCH_COE_SCHEMA = 'boac_advising_coe'
DATA_LOCH_INTERMEDIATE_SCHEMA = 'intermediate'
DATA_LOCH_SIS_SCHEMA = 'sis_data'
DATA_LOCH_STUDENT_SCHEMA = 'student'

DISABLE_MATRIX_VIEW_THRESHOLD = 800

LDAP_HOST = 'nds-test.berkeley.edu'
LDAP_BIND = 'mybind'
LDAP_PASSWORD = 'secret'

CANVAS_CURRENT_ENROLLMENT_TERM = 'Fall 2017'
CANVAS_EARLIEST_TERM = 'Fall 2016'

CAL1CARD_PHOTO_API_URL = 'https://secreturl.berkeley.edu/photos'
CAL1CARD_PHOTO_API_USERNAME = 'secretuser'
CAL1CARD_PHOTO_API_PASSWORD = 'secretpassword'

# Alerts
ALERT_NO_ACTIVITY_ENABLED = True
ALERT_NO_ACTIVITY_DAYS_INTO_SESSION = 14
# Show "no activity" alerts for a course site only if the percentage of students with no activity
# is below this number. Percentile cutoffs for other alert types work likewise.
ALERT_NO_ACTIVITY_PERCENTILE_CUTOFF = 20

ALERT_INFREQUENT_ACTIVITY_ENABLED = True
ALERT_INFREQUENT_ACTIVITY_DAYS = 14
ALERT_INFREQUENT_ACTIVITY_PERCENTILE_CUTOFF = 20

ALERT_HOLDS_ENABLED = True

# Logging
LOGGING_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOGGING_LOCATION = 'boac.log'
LOGGING_LEVEL = logging.DEBUG

# Caching (number of seconds, or false to disable)
CACHE_DEFAULT = False

# If the top decile of any analytics measure is below this number, treat it as zero ("no data").
# At the beginning of a term, the bar may be lowered.
MEANINGFUL_STATS_MINIMUM = 4

BOAC_SUPPORT_EMAIL = 'boac-support@lists.berkeley.edu'
