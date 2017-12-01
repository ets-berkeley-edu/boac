import inspect

from boac import db
from boac.lib.berkeley import term_name_for_sis_id
from boac.models.base import Base
from decorator import decorator
from flask import current_app as app
from sqlalchemy.dialects.postgresql import JSONB


class JsonCache(Base):
    __tablename__ = 'json_cache'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    key = db.Column(db.String, nullable=False, unique=True)
    json = db.Column(JSONB)

    def __init__(self, key, json=None):
        self.key = key
        self.json = json

    def __repr__(self):
        return '<JsonCache {}, json={}, updated={}, created={}>'.format(
            self.key,
            self.json,
            self.updated_at,
            self.created_at,
        )


def clear(key_like):
    matches = db.session.query(JsonCache).filter(JsonCache.key.like(key_like))
    app.logger.info('Will delete {count} entries matching {key_like}'.format(count=matches.count(), key_like=key_like))
    matches.delete(synchronize_session=False)


def clear_other(key_like):
    matches = db.session.query(JsonCache).filter(JsonCache.key.notlike(key_like))
    app.logger.info('Will delete {count} entries not matching {key_like}'.format(count=matches.count(), key_like=key_like))
    matches.delete(synchronize_session=False)


def clear_current_term():
    # Start by deleting cache which is not term-stamped, on the assumption that those feeds may have changed.
    clear_other('term_%')
    db.session.commit()
    clear('term_{}%'.format(app.config['CANVAS_CURRENT_ENROLLMENT_TERM']))
    db.session.commit()


def stow(key_pattern, for_term=False):
    """Uses the Decorator module to preserve the wrapped function's signature,
    allowing easy wrapping by other decorators.
    If the for_term option is enabled, the wrapped function is expected to take a term_id argument.
    TODO Mockingbird does not currently preserve signatures, and so JsonCache
    cannot directly wrap a @fixture.
    """
    @decorator
    def _stow(func, *args, **kw):
        args_dict = _get_args(func, *args, **kw)
        key = key_pattern.format(**args_dict)
        if for_term:
            term_name = term_name_for_sis_id(args_dict.get('term_id'))
            key = 'term_{}-{}'.format(
                term_name,
                key,
            )
        stowed = JsonCache.query.filter_by(key=key).first()
        # Note that the query returns a DB row rather than the value of the JSON column.
        if stowed is not None:
            app.logger.debug('Returning stowed JSON for key {key}'.format(key=key))
            return stowed.json
        else:
            app.logger.info('{key} not found in DB'.format(key=key))
            to_stow = func(*args, **kw)
            if to_stow is not None:
                app.logger.debug('Will stow JSON for key {key}'.format(key=key))
                row = JsonCache(key=key, json=to_stow)
                db.session.add(row)
                # Give a hoot, don't pollute.
                if not app.config['TESTING']:
                    db.session.commit()
            else:
                app.logger.info('{key} not generated and will not be stowed in DB'.format(key=key))
            return to_stow
    return _stow


def _get_args(func, *args, **kw):
    arg_names = inspect.getfullargspec(func)[0]
    args_dict = dict(zip(arg_names, args))
    args_dict.update(kw)
    return args_dict
