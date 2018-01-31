from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

__version__ = '1.1'

db = SQLAlchemy()


def std_commit(allow_test_environment=False):
    """Commit failures in SQLAlchemy must be explicitly handled.

    This function follows the suggested default, which is to roll back and close the active session, letting the pooled
    connection start a new transaction cleanly. WARNING: Session closure will invalidate any in-memory DB entities. Rows
    will have to be reloaded from the DB to be read or updated.
    """
    # Give a hoot, don't pollute.
    if app.config['TESTING'] and not allow_test_environment:
        # When running tests, a session flush generates the id and timestamps that would otherwise show up during a commit.
        db.session.flush()
        return
    successful_commit = False
    try:
        db.session.commit()
        successful_commit = True
    except SQLAlchemyError as exception:
        db.session.rollback()
        raise
    finally:
        if not successful_commit:
            db.session.close()
