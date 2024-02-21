"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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


from flask import current_app as app
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

__version__ = '6.0'

db = SQLAlchemy()

# TODO: Flask-caching and Amazon ElastiCache for route caching?
# Use @cache.cached() and @cache.memoize to cache routes and functions, respectively
cache = Cache()


def std_commit(allow_test_environment=False, session=None):
    """Commit failures in SQLAlchemy must be explicitly handled.

    This function follows the suggested default, which is to roll back and close the active session, letting the pooled
    connection start a new transaction cleanly. WARNING: Session closure will invalidate any in-memory DB entities. Rows
    will have to be reloaded from the DB to be read or updated.
    """
    # Give a hoot, don't pollute.
    if session is None:
        session = db.session
    if app.config['TESTING'] and not allow_test_environment:
        # When running tests, session flush generates id and timestamps that would otherwise show up during a commit.
        session.flush()
        return
    successful_commit = False
    try:
        session.commit()
        successful_commit = True
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        if not successful_commit:
            session.close()
