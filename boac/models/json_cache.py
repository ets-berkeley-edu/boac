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


import threading
import time

from boac import db, std_commit
from boac.lib.berkeley import term_name_for_sis_id
from boac.lib.util import get_args_dict
from boac.models.base import Base
from decorator import decorator
from flask import current_app as app
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql import text

cache_thread = threading.local()


# When staging, all keys point to the staging table except JobStatus and ASC synch records, which always use
# the normal json_cache table.
class JsonCacheBase(object):
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


class JsonCache(JsonCacheBase, Base):
    __tablename__ = 'json_cache'


class JsonCacheStaging(JsonCacheBase, Base):
    __tablename__ = 'json_cache_staging'


def is_staging():
    cache_type = getattr(cache_thread, 'type', None)
    if cache_type is None:
        cache_thread.type = 'normal'
    return cache_thread.type == 'staging'


def set_staging(enabled):
    if enabled:
        cache_thread.type = 'staging'
    else:
        cache_thread.type = 'normal'


def working_cache():
    if is_staging():
        return JsonCacheStaging
    else:
        return JsonCache


def clear(key_like):
    matches = db.session.query(JsonCache).filter(JsonCache.key.like(key_like))
    app.logger.info('Will delete {count} entries matching {key_like}'.format(count=matches.count(), key_like=key_like))
    matches.delete(synchronize_session=False)


def stow(key_pattern, for_term=False):
    """Use Decorator module to preserve the wrapped function's signature, allowing easy wrapping by other decorators.

    If the for_term option is enabled, the wrapped function is expected to take a term_id argument.
    TODO Mockingbird does not currently preserve signatures, and so JsonCache cannot directly wrap a @fixture.
    """
    @decorator
    def _stow(func, *args, **kw):
        args_dict = get_args_dict(func, *args, **kw)
        key = key_pattern.format(**args_dict)
        if for_term:
            term_name = term_name_for_sis_id(args_dict.get('term_id'))
            key = 'term_{}-{}'.format(
                term_name,
                key,
            )
        stowed = working_cache().query.filter_by(key=key).first()
        # Note that the query returns a DB row rather than the value of the JSON column.
        if stowed is not None:
            app.logger.debug('Returning stowed JSON for key {key}'.format(key=key))
            return stowed.json
        else:
            app.logger.info('{key} not found in DB'.format(key=key))
            to_stow = func(*args, **kw)
            if to_stow is not None:
                app.logger.debug('Will stow JSON for key {key}'.format(key=key))
                row = working_cache()(key=key, json=to_stow)
                try:
                    db.session.add(row)
                    std_commit()
                except IntegrityError:
                    app.logger.warn('Conflict for key {key}; will attempt to return stowed JSON'.format(key=key))
                    stowed = working_cache().query.filter_by(key=key).first()
                    if stowed is not None:
                        return stowed.json
            else:
                app.logger.info('{key} not generated and will not be stowed in DB'.format(key=key))
            return to_stow
    return _stow


def update_jsonb_row(stowed):
    """Jump through some hoops to commit changes to a JSONB column."""
    flag_modified(stowed, 'json')
    db.session.merge(stowed)
    std_commit()


def create_staging_table(exclusions_select):
    sql = f"""
        CREATE UNLOGGED TABLE json_cache_staging (LIKE json_cache INCLUDING ALL);
        INSERT INTO json_cache_staging SELECT * from json_cache WHERE
            {exclusions_select};
        """
    started = time.perf_counter()
    try:
        db.engine.connect().execute(text(sql))
        std_commit()
    except SQLAlchemyError as err:
        app.logger.error(f'SQL {sql} threw {err}')
    elapsed = round(time.perf_counter() - started, 2)
    app.logger.info(f'JSON Cache Staging table created in {elapsed} secs')
    log_table_sizes()


def staging_table_exists():
    return db.engine.dialect.has_table(db.engine, 'json_cache_staging')


def drop_staging_table():
    sql = 'DROP TABLE IF EXISTS json_cache_staging CASCADE;'
    try:
        db.engine.connect().execute(text(sql))
        std_commit()
    except SQLAlchemyError as err:
        app.logger.error(f'SQL {sql} threw {err}')


def refresh_from_staging(inclusions_select):
    # Refuse to follow through if the staging table does not appear to have been loaded.
    count = JsonCacheStaging.query.filter(text(inclusions_select)).count()
    std_commit()
    if count == 0:
        app.logger.warn(f'Will not refresh; staging cache has no matches for {inclusions_select}')
        return 0
    app.logger.info(f'Will refresh cache from {count} matches on {inclusions_select}')
    started = time.perf_counter()
    sql = f"""
        BEGIN;
        SET LOCAL lock_timeout = '10s';
        LOCK TABLE json_cache;
        DELETE FROM json_cache WHERE {inclusions_select};
        INSERT INTO json_cache SELECT * FROM json_cache_staging WHERE {inclusions_select};
        COMMIT;
    """
    try:
        db.engine.connect().execute(text(sql))

        # Like some other DDL commands, 'VACUUM' can only be managed by psycopg2 if the connection
        # isolation level is set to autocommit. SQLalchemy's autocommit flag is not sufficient.
        sql = 'VACUUM ANALYZE json_cache'
        db.engine.connect().execution_options(isolation_level='AUTOCOMMIT').execute(text(sql))

        elapsed = round(time.perf_counter() - started, 2)
        app.logger.info(f'JSON Cache refreshed and vacuumed in {elapsed} secs')
        log_table_sizes()

        return count
    except SQLAlchemyError as err:
        app.logger.error(f'SQL {sql} threw {err}')
        return 0


def log_table_sizes():
    sql = """
        SELECT table_name, pg_size_pretty(total_bytes) AS total FROM (
            SELECT c.oid, nspname, relname AS table_name,
                pg_total_relation_size(c.oid) AS total_bytes
            FROM pg_class c
                LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE relkind = 'r'
                    AND nspname = 'public'
                    AND relname in ('json_cache', 'json_cache_staging')
        ) a;
    """
    try:
        dbresp = db.engine.connect().execute(text(sql))
        std_commit()
        sizes = [dict(r) for r in dbresp.fetchall()]
        for s in sizes:
            app.logger.info('Table ' + s['table_name'] + ' currently uses ' + s['total'])
        return sizes
    except SQLAlchemyError as err:
        app.logger.error(f'SQL {sql} threw {err}')
        return None
