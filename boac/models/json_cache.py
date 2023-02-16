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


import threading

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


class JsonCache(Base):
    __tablename__ = 'json_cache'
    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    key = db.Column(db.String, nullable=False, unique=True)
    json = db.Column(JSONB)

    def __init__(self, key, json=None):
        self.key = key
        self.json = json

    def __repr__(self):
        return f'<JsonCache {self.key}, json={self.json}>'


def clear(key_like):
    matches = db.session.query(JsonCache).filter(JsonCache.key.like(key_like))
    app.logger.info(f'Will delete {matches.count()} entries matching {key_like}')
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
            key = f'term_{term_name}-{key}'
        stowed = JsonCache.query.filter_by(key=key).first()
        # Note that the query returns a DB row rather than the value of the JSON column.
        if stowed is not None:
            app.logger.debug(f'Returning stowed JSON for key {key}')
            return stowed.json
        else:
            app.logger.info(f'{key} not found in runtime DB')
            to_stow = func(*args, **kw)
            if to_stow is not None:
                app.logger.debug(f'Will stow JSON for key {key}')
                insert_row(key=key, json=to_stow)
            else:
                app.logger.info(f'{key} not generated and will not be stowed in DB')
            return to_stow
    return _stow


def fetch(key, term_id=None):
    """Query the cache for a given key with optional term specification."""
    if term_id:
        term_name = term_name_for_sis_id(term_id)
        key = f'term_{term_name}-{key}'
    stowed = JsonCache.query.filter_by(key=key).first()
    if stowed is not None:
        return stowed.json


def fetch_bulk(keys):
    stowed_results = JsonCache.query.filter(JsonCache.key.in_(keys))
    return {r.key: r.json for r in stowed_results}


def insert_row(key, json):
    """Insert new cache row with conflict checks."""
    row = JsonCache(key=key, json=json)
    try:
        db.session.add(row)
        std_commit()
    except IntegrityError:
        app.logger.warn(f'Conflict for key {key}; will attempt to return stowed JSON')
        stowed = JsonCache.query.filter_by(key=key).first()
        if stowed is not None:
            return stowed.json


def update_jsonb_row(stowed):
    """Jump through some hoops to commit changes to a JSONB column."""
    flag_modified(stowed, 'json')
    db.session.merge(stowed)
    std_commit()


def log_table_sizes():
    sql = """
        SELECT table_name, pg_size_pretty(total_bytes) AS total FROM (
            SELECT c.oid, nspname, relname AS table_name,
                pg_total_relation_size(c.oid) AS total_bytes
            FROM pg_class c
                LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE relkind = 'r'
                    AND nspname = 'public'
                    AND relname in ('json_cache')
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
