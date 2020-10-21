"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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

from threading import Thread

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def bg_execute(method):
    from flask import current_app as app
    if app.config['BACKGROUND_TASKS']:
        app.logger.debug('Launching background task.')
        t = Thread(
            target=_bg_executor,
            daemon=True,
            kwargs={
                'app': app._get_current_object(),
                'method': method,
            },
        )
        t.start()
    else:
        from boac import db
        app.logger.debug('Background tasks disabled, will run task in foreground.')
        method(db_session=db.session)


# Database engine and session factory for background threads, distinct from the request-bound Flask-SQLAlchemy db object.
engine = None
session_factory = None


def get_engine(app):
    global engine
    if engine is None:
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    return engine


BACKGROUND_THREAD_LOCK_ID = 1000


def _bg_executor(app, method):
    global session_factory
    with app.app_context():
        app.logger.debug('Started background thread.')
        # Only one background session at a time, please.
        db_engine = get_engine(app)
        with db_engine.connect() as lock_connection:
            # Detaching will protect the server-session PID from action in the yield block.
            # Because detached connections are permanently removed from the pool, it also
            # ensures that the lock will be released when the connection is closed.
            lock_connection.detach()
            locked = try_advisory_lock(app, lock_connection, BACKGROUND_THREAD_LOCK_ID)
            if locked:
                try:
                    if session_factory is None:
                        session_factory = sessionmaker(bind=db_engine)
                    session = scoped_session(session_factory)
                    method(db_session=session)
                except Exception as e:
                    app.logger.exception(e)
                    raise e
                finally:
                    advisory_unlock(app, lock_connection, BACKGROUND_THREAD_LOCK_ID)
                    app.logger.debug('Background task complete.')
            else:
                app.logger.warn('Was not granted advisory lock, will not run background method.')


def try_advisory_lock(app, connection, lock_id):
    result = connection.execute(f'SELECT pg_try_advisory_lock({lock_id}) as locked, pg_backend_pid() as pid')
    (locked, pid) = next(result)
    if locked:
        app.logger.info(f'Granted advisory lock {lock_id} for PID {pid}')
    else:
        app.logger.warn(f'Was not granted advisory lock {lock_id} for PID {pid}')
    return locked


def advisory_unlock(app, connection, lock_id):
    result = connection.execute(f'SELECT pg_advisory_unlock({lock_id}) as unlocked, pg_backend_pid() as pid')
    (unlocked, pid) = next(result)
    if unlocked:
        app.logger.info(f'Released advisory lock {lock_id} for PID {pid}')
    else:
        app.logger.error(f'Failed to release advisory lock {lock_id} for PID {pid}')
    # Guard against the possibility of duplicate successful lock requests from this connection.
    while unlocked:
        result = connection.execute(f'SELECT pg_advisory_unlock({lock_id}) as unlocked')
        unlocked = next(result).unlocked
