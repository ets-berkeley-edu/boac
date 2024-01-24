"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

ABBREVIATED_WORDS = ['APR', 'EAP', 'PNP', 'SAP']

# Alerts
ALERT_INFREQUENT_ACTIVITY_DAYS = 14
ALERT_INFREQUENT_ACTIVITY_ENABLED = True
ALERT_INFREQUENT_ACTIVITY_PERCENTILE_CUTOFF = 20

ALERT_NO_ACTIVITY_DAYS_INTO_SESSION = 14
ALERT_NO_ACTIVITY_ENABLED = True

# Show "no activity" alerts for a course site only if the percentage of students with no activity
# is below this number. Percentile cutoffs for other alert types work likewise.
ALERT_NO_ACTIVITY_PERCENTILE_CUTOFF = 20

ALERT_WITHDRAWAL_ENABLED = True

# Set to a nice long chaotic string to enable scripted access to APIs.
API_KEY = None

# For /appt/desk. 60000 ms = 1 minute.
APPT_DESK_REFRESH_INTERVAL = 60000

# BOAC-specific AWS credentials.
AWS_APP_ROLE_ARN = 'aws:arn::<account>:role/<app_boa_role>'

# Time, in seconds, between iterations of background task loop.
BACKGROUND_TASK_LOOP_INTERVAL = 3600

# Spawn asynchronous tasks (e.g., search reindexing) in background theads; disabled in test runs.
BACKGROUND_TASKS = True

# Base directory for the application (one level up from this config file).
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

BOAC_SUPPORT_EMAIL = 'boahelp@berkeley.edu'

# Flask-caching (number of seconds, or False to disable)
CACHE_DEFAULT_TIMEOUT = False
CACHE_TYPE = 'null'

CANVAS_CURRENT_ENROLLMENT_TERM = 'auto'
CANVAS_EARLIEST_TERM = 'Fall 2016'
CANVAS_FUTURE_ENROLLMENT_TERM = 'auto'

CAS_SERVER = 'https://auth-test.berkeley.edu/cas/'
CAS_LOGOUT_URL = 'https://auth-test.berkeley.edu/cas/logout'

COHORT_FILTER_ACADEMIC_STANDING_YEARS_CUTOFF = 5

# Some defaults.
CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'

DATA_LOCH_ADVISING_APPOINTMENTS_SCHEMA = 'boac_advising_appointments'
DATA_LOCH_ADVISING_NOTES_SCHEMA = 'boac_advising_notes'
DATA_LOCH_ADVISOR_SCHEMA = 'boac_advisor'
DATA_LOCH_ASC_SCHEMA = 'boac_advising_asc'
DATA_LOCH_BOAC_SCHEMA = 'boac_analytics'
DATA_LOCH_COE_SCHEMA = 'boac_advising_coe'
DATA_LOCH_DATA_SCIENCE_ADVISING_SCHEMA = 'boac_advising_data_science'
DATA_LOCH_E_I_SCHEMA = 'boac_advising_e_i'
DATA_LOCH_EOP_ADVISING_SCHEMA = 'boac_advising_eop'
DATA_LOCH_HISTORY_DEPT_ADVISING_SCHEMA = 'boac_advising_history_dept'
DATA_LOCH_INTERMEDIATE_SCHEMA = 'intermediate'
DATA_LOCH_OUA_SCHEMA = 'boac_advising_oua'

# The Data Loch provides read-only Postgres access.
DATA_LOCH_RDS_URI = 'postgresql://nessie:secret@secret-rds-url.com:5432/canvas'
DATA_LOCH_MAX_CONNECTIONS = 50

DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH = 'sis-attachment-path'
DATA_LOCH_S3_ADVISING_NOTE_BUCKET = 'advising-note-bucket'
DATA_LOCH_S3_BOA_NOTE_ATTACHMENTS_PATH = 'boa-attachment-path'
DATA_LOCH_S3_ENCRYPTION = 'AES256'
DATA_LOCH_S3_EOP_ADVISING_NOTE_BUCKET = 'eop-advising-note-bucket'
DATA_LOCH_S3_EOP_NOTE_ATTACHMENTS_PATH = 'eop-attachment-path'
DATA_LOCH_S3_PHOTO_BUCKET = 'photo-bucket'
DATA_LOCH_S3_PHOTO_PATH = 'photo-path'
DATA_LOCH_S3_REGION = 'us-west-2'
DATA_LOCH_SIS_ADVISING_NOTES_SCHEMA = 'sis_advising_notes'
DATA_LOCH_SIS_SCHEMA = 'sis_data'
DATA_LOCH_STUDENT_SCHEMA = 'student'
DATA_LOCH_TERMS_SCHEMA = 'terms'

DISABLE_MATRIX_VIEW_THRESHOLD = 800

# In demo mode, student profile pictures and sensitive data will be blurred.
DEMO_MODE_AVAILABLE = False

DEPARTMENTS_SUPPORTING_DROP_INS = []
DEPARTMENTS_SUPPORTING_SAME_DAY_APPTS = []

DEVELOPER_AUTH_ENABLED = False
DEVELOPER_AUTH_PASSWORD = 'another secret'

FEATURE_FLAG_ADMITTED_STUDENTS = False

# Notify BOA users when they are accessing boa-dev, boa-qa, and boa-demo. Unlike service announcements, this
# warning can only be unpublished by setting config to None.
FIXED_WARNING_ON_ALL_PAGES = None

# Directory to search for mock fixtures, if running in "test" or "demo" mode.
FIXTURES_PATH = None

# Minutes of inactivity before session cookie is destroyed
INACTIVE_SESSION_LIFETIME = 20

# These "INDEX_HTML" defaults are good in boac-dev, boac-qa, etc. See development.py for appropriate local configs.
INDEX_HTML = 'dist/static/index.html'

LDAP_HOST = 'ldap-test.berkeley.edu'
LDAP_BIND = 'mybind'
LDAP_PASSWORD = 'secret'

LEGACY_EARLIEST_TERM = 'Fall 2001'

# Logging
LOGGING_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOGGING_LOCATION = 'boa.log'
LOGGING_LEVEL = logging.DEBUG
LOGGING_PROPAGATION_LEVEL = logging.INFO

# If the top decile of any analytics measure is below this number, treat it as zero ("no data").
# At the beginning of a term, the bar may be lowered.
MEANINGFUL_STATS_MINIMUM = 4

NOTES_ATTACHMENTS_MAX_PER_NOTE = 10
# During edit of draft note, we continually save changes via background thread. (This config is in milliseconds.)
NOTES_DRAFT_AUTO_SAVE_INTERVAL = 10000
NOTES_SEARCH_RESULT_SNIPPET_PADDING = 29

# Default is 15 minutes
PHOTO_SIGNED_URL_EXPIRES_IN_SECONDS = 15 * 60

# Millisecond interval for request to keep session alive
PING_FREQUENCY = 900000

# Used to encrypt session cookie.
SECRET_KEY = 'secret'

# Save DB changes at the end of a request.
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

# Override in local configs.
SQLALCHEMY_DATABASE_URI = 'postgresql://boac:boac@localhost:5432/boac'

# Disable an expensive bit of the ORM.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# A common configuration; one request thread, one background worker thread.
THREADS_PER_PAGE = 2

TIMEZONE = 'America/Los_Angeles'

USER_SEARCH_HISTORY_MAX_SIZE = 5

# This base-URL config should only be non-None in the "local" env where the Vue front-end runs on port 8080.
VUE_LOCALHOST_BASE_URL = None

# We keep these out of alphabetical sort above for readability's sake.
HOST = '0.0.0.0'
PORT = 5000
