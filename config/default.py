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

import logging
import os

# Base directory for the application (one level up from this config file).
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# In demo mode, student profile pictures and sensitive data will be blurred.
DEMO_MODE_AVAILABLE = False

# These "INDEX_HTML" defaults are good in boac-dev, boac-qa, etc. See development.py for appropriate local configs.
INDEX_HTML = 'dist/static/index.html'

# This base-URL config should only be non-None in the "local" env where the Vue front-end runs on port 8080.
VUE_LOCALHOST_BASE_URL = None

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

ABBREVIATED_WORDS = ['APR', 'EAP', 'PNP', 'SAP']

# Set to a nice long chaotic string to enable scripted access to APIs.
API_KEY = None

# BOAC-specific AWS credentials.
AWS_APP_ROLE_ARN = 'aws:arn::<account>:role/<app_boa_role>'

CAS_SERVER = 'https://auth-test.berkeley.edu/cas/'
CAS_LOGOUT_URL = 'https://auth-test.berkeley.edu/cas/logout'

# Enable with a valid Google id. For example, 'UA-999999999-1'
GOOGLE_ANALYTICS_ID = False

# Data Loch Redshift and RDS are treated as readonly Postgres DBs.
DATA_LOCH_URI = 'postgres://nessie:secret@secreturl.com:5432/canvas'
DATA_LOCH_RDS_URI = 'postgres://nessie:secret@secret-rds-url.com:5432/canvas'

DATA_LOCH_ADVISING_NOTES_SCHEMA = 'boac_advising_notes'
DATA_LOCH_ASC_ADVISING_NOTES_SCHEMA = 'asc_advising_notes'
DATA_LOCH_ASC_SCHEMA = 'boac_advising_asc'
DATA_LOCH_BOAC_SCHEMA = 'boac_analytics'
DATA_LOCH_COE_SCHEMA = 'boac_advising_coe'
DATA_LOCH_INTERMEDIATE_SCHEMA = 'intermediate'
DATA_LOCH_L_S_SCHEMA = 'boac_advising_l_s'
DATA_LOCH_PHYSICS_SCHEMA = 'boac_advising_physics'
DATA_LOCH_SIS_SCHEMA = 'sis_data'
DATA_LOCH_STUDENT_SCHEMA = 'student'

DATA_LOCH_S3_REGION = 'us-west-2'
DATA_LOCH_S3_ENCRYPTION = 'AES256'
DATA_LOCH_S3_ADVISING_NOTE_BUCKET = 'advising-note-bucket'
DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH = 'attachment-path'
DATA_LOCH_S3_BOA_NOTE_ATTACHMENTS_PATH = 'boa-attachment-path'
DATA_LOCH_S3_PHOTO_BUCKET = 'photo-bucket'
DATA_LOCH_S3_PHOTO_PATH = 'photo-path'

DISABLE_MATRIX_VIEW_THRESHOLD = 800

LDAP_HOST = 'ldap-test.berkeley.edu'
LDAP_BIND = 'mybind'
LDAP_PASSWORD = 'secret'

CANVAS_CURRENT_ENROLLMENT_TERM = 'Fall 2017'
CANVAS_EARLIEST_TERM = 'Fall 2016'
CANVAS_FUTURE_ENROLLMENT_TERM = 'Spring 2018'
LEGACY_EARLIEST_TERM = 'Fall 2001'

# Default is 15 minutes
PHOTO_SIGNED_URL_EXPIRES_IN_SECONDS = 15 * 60

# Alerts
ALERT_NO_ACTIVITY_ENABLED = True
ALERT_NO_ACTIVITY_DAYS_INTO_SESSION = 14
# Show "no activity" alerts for a course site only if the percentage of students with no activity
# is below this number. Percentile cutoffs for other alert types work likewise.
ALERT_NO_ACTIVITY_PERCENTILE_CUTOFF = 20

ALERT_INFREQUENT_ACTIVITY_ENABLED = True
ALERT_INFREQUENT_ACTIVITY_DAYS = 14
ALERT_INFREQUENT_ACTIVITY_PERCENTILE_CUTOFF = 20

ALERT_WITHDRAWAL_ENABLED = True

# Logging
LOGGING_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOGGING_LOCATION = 'boac.log'
LOGGING_LEVEL = logging.DEBUG

# Flask-caching (number of seconds, or False to disable)
CACHE_DEFAULT_TIMEOUT = False
CACHE_TYPE = 'null'

# If the top decile of any analytics measure is below this number, treat it as zero ("no data").
# At the beginning of a term, the bar may be lowered.
MEANINGFUL_STATS_MINIMUM = 4

NOTES_SEARCH_RESULT_SNIPPET_PADDING = 29
NOTES_ATTACHMENTS_MAX_PER_NOTE = 5

BOAC_SUPPORT_EMAIL = 'boahelp@berkeley.edu'
