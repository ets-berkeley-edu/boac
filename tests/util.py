"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

import itertools
from contextlib import contextmanager

import boto3
import moto
from botocore.exceptions import ClientError

from boac.lib.util import localized_timestamp_to_utc
from boac.models.comment_parent import CommentParent


def _ensure_bucket(s3, bucket, region):
    """Create the bucket if it doesn't already exist.

    Since moto 5, all AWS services share a single mock backend that stays active for the whole test
    session (see the 'fake_aws' fixture in conftest.py), so buckets created by one test persist into
    the next. Explicitly checking first keeps these helpers idempotent across tests.
    """
    try:
        s3.meta.client.head_bucket(Bucket=bucket)
    except ClientError:
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': region})


@contextmanager
def mock_eop_note_attachment(app):
    with moto.mock_aws():
        bucket = app.config['DATA_LOCH_S3_EOP_ADVISING_NOTE_BUCKET']
        s3 = boto3.resource('s3', app.config['AWS_REGION'])
        _ensure_bucket(s3, bucket, app.config['AWS_REGION'])
        key = f"{app.config['DATA_LOCH_S3_EOP_NOTE_ATTACHMENTS_PATH']}/eop_advising_note_101_i am attached.txt"
        s3.Object(bucket, key).put(Body="A wizard's job is to vex chumps quickly in fog.")
        yield s3


@contextmanager
def mock_legacy_appointment_attachment(app):
    with moto.mock_aws():
        bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
        s3 = boto3.resource('s3', app.config['AWS_REGION'])
        _ensure_bucket(s3, bucket, app.config['AWS_REGION'])
        key = f"{app.config['DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH']}/9100000000/9100000000_00010_1.pdf"
        s3.Object(bucket, key).put(Body='01001000 01100101 01101100 01101100 01101111 00100000 01010111 01101111 01110010 01101100 01100100')
        yield s3


@contextmanager
def mock_sis_note_attachment(app):
    with moto.mock_aws():
        bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
        s3 = boto3.resource('s3', app.config['AWS_REGION'])
        _ensure_bucket(s3, bucket, app.config['AWS_REGION'])
        key = f"{app.config['DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH']}/9000000000/9000000000_00002_1.pdf"
        s3.Object(bucket, key).put(Body='When in the course of human events, it becomes necessarf arf woof woof woof')
        yield s3


@contextmanager
def mock_advising_note_s3_bucket(app):
    with moto.mock_aws():
        bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
        s3 = boto3.resource('s3', app.config['AWS_REGION'])
        _ensure_bucket(s3, bucket, app.config['AWS_REGION'])
        yield s3


@contextmanager
def override_config(app, key, value):
    """Temporarily override an app config value."""
    old_value = app.config[key]
    app.config[key] = value
    try:
        yield
    finally:
        app.config[key] = old_value


@contextmanager
def pause_mock_sts():
    """Temporarily pause moto's AWS mock, which can get in the way of tests incorporating other external services, such as CAS."""
    moto.mock_aws().stop()
    try:
        yield
    finally:
        moto.mock_aws().start()

def refresh_loch_appointment_search_index(app, comment=None, deleted_comment=None):
    from sqlalchemy import create_engine
    from sqlalchemy.sql import text
    engine = create_engine(app.config['DATA_LOCH_RDS_URI'])
    try:
        with engine.begin() as conn:
            if comment:
                parent_appointment = CommentParent.find_by_id(comment.comment_parent_id)
                searchable_text = f"{comment.body or ''} {comment.author_name or ''}"
                values = [{
                    'parent_appointment_id': parent_appointment.parent_id,
                    'boa_id': comment.id,
                    'author_uid': comment.author_uid,
                    'author_name': comment.author_name,
                    'author_role': comment.author_role,
                    'author_dept_codes': comment.author_dept_codes,
                    'body': comment.body.replace("'", r"''") if comment.body else None,
                    'created_at': comment.created_at,
                    'updated_at': comment.updated_at,
                    'searchable_text': searchable_text,
                }]
                sql = """INSERT INTO boa_app_rds_data.advising_appointment_comments
                    (parent_appointment_id, boa_id, author_uid, author_name, author_role,
                    author_dept_codes, body, created_at, updated_at)
                  VALUES (
                    :parent_appointment_id, :boa_id, :author_uid, :author_name, :author_role,
                    CAST(:author_dept_codes AS varchar[]), :body, :created_at, :updated_at)
                  ON CONFLICT (boa_id)
                  DO UPDATE SET
                    parent_appointment_id = EXCLUDED.parent_appointment_id,
                    author_uid = EXCLUDED.author_uid,
                    author_name = EXCLUDED.author_name,
                    author_role = EXCLUDED.author_role,
                    author_dept_codes = EXCLUDED.author_dept_codes,
                    body = EXCLUDED.body,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at;
                  INSERT INTO boa_app_rds_data.advising_appointment_comments_search_index
                    (parent_appointment_id, boa_id, fts_index)
                  VALUES (:parent_appointment_id, :boa_id, TO_TSVECTOR('english', :searchable_text))
                  ON CONFLICT(boa_id)
                  DO UPDATE SET
                    parent_appointment_id = EXCLUDED.parent_appointment_id,
                    fts_index = EXCLUDED.fts_index;"""
                conn.execute(text(sql), values)
            if deleted_comment:
                params = {
                    'delete_id': deleted_comment.id,
                }
                sql = """DELETE FROM boa_app_rds_data.advising_appointment_comments
                      WHERE boa_id = :delete_id;
                    DELETE FROM boa_app_rds_data.advising_appointment_comments_search_index
                      WHERE boa_id = :delete_id;"""
                conn.execute(text(sql), params)
    finally:
            engine.dispose()

def refresh_loch_eform_search_index(app, comment=None, deleted_comment=None):
    from sqlalchemy import create_engine
    from sqlalchemy.sql import text
    engine = create_engine(app.config['DATA_LOCH_RDS_URI'])
    try:
        with engine.begin() as conn:
            if comment:
                parent_eform = CommentParent.find_by_id(comment.comment_parent_id)
                searchable_text = f"{comment.body or ''} {comment.author_name or ''}"
                values = [{
                    'parent_eform_id': parent_eform.parent_id,
                    'boa_id': comment.id,
                    'author_uid': comment.author_uid,
                    'author_name': comment.author_name,
                    'author_role': comment.author_role,
                    'author_dept_codes': comment.author_dept_codes,
                    'body': comment.body.replace("'", r"''") if comment.body else None,
                    'created_at': comment.created_at,
                    'updated_at': comment.updated_at,
                    'searchable_text': searchable_text,
                }]
                sql = """INSERT INTO boa_app_rds_data.eform_comments
                    (parent_eform_id, boa_id, author_uid, author_name, author_role,
                    author_dept_codes, body, created_at, updated_at)
                  VALUES (
                    :parent_eform_id, :boa_id, :author_uid, :author_name, :author_role,
                    CAST(:author_dept_codes AS varchar[]), :body, :created_at, :updated_at)
                  ON CONFLICT (boa_id)
                  DO UPDATE SET
                    parent_eform_id = EXCLUDED.parent_eform_id,
                    author_uid = EXCLUDED.author_uid,
                    author_name = EXCLUDED.author_name,
                    author_role = EXCLUDED.author_role,
                    author_dept_codes = EXCLUDED.author_dept_codes,
                    body = EXCLUDED.body,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at;
                  INSERT INTO boa_app_rds_data.eform_comments_search_index
                    (parent_eform_id, boa_id, fts_index)
                  VALUES (:parent_eform_id, :boa_id, TO_TSVECTOR('english', :searchable_text))
                  ON CONFLICT(boa_id)
                  DO UPDATE SET
                    parent_eform_id = EXCLUDED.parent_eform_id,
                    fts_index = EXCLUDED.fts_index;"""
                conn.execute(text(sql), values)
            if deleted_comment:
                params = {
                    'delete_id': deleted_comment.id,
                }
                sql = """DELETE FROM boa_app_rds_data.eform_comments
                      WHERE boa_id = :delete_id;
                    DELETE FROM boa_app_rds_data.eform_comments_search_index
                      WHERE boa_id = :delete_id;"""
                conn.execute(text(sql), params)
    finally:
            engine.dispose()

def refresh_loch_note_search_index(app, notes=None, deleted_notes=None):
    from sqlalchemy import create_engine
    from sqlalchemy.sql import text
    engine = create_engine(app.config['DATA_LOCH_RDS_URI'])
    try:
        with engine.begin() as conn:
            if notes:
                notes_insert_values = []
                topics_insert_values = []
                for note in notes:
                    note_id = f'boa-{note.sid}-{note.id}'
                    name_parts = (note.author_name or '').split(maxsplit=1)
                    advisor_first_name = name_parts[0] if name_parts else None
                    advisor_last_name = name_parts[1] if len(name_parts) > 1 else None
                    searchable_body = note.body if note.body and not note.is_private else ''
                    searchable_topics = ' '.join([t.topic for t in note.topics]) if note.topics else ''
                    searchable_text = f"{note.subject or ''} {searchable_body} {searchable_topics} {note.author_name or ''}"

                    notes_insert_values.append({
                        'id': note_id,
                        'student_sid': note.sid,
                        'boa_id': note.id,
                        'advisor_uid': note.author_uid,
                        'author_name': note.author_name,
                        'advisor_first_name': advisor_first_name,
                        'advisor_last_name': advisor_last_name,
                        'author_dept_codes': note.author_dept_codes,
                        'subject': note.subject,
                        'note_body': note.body.replace("'", r"''") if note.body else None,
                        'is_private': note.is_private,
                        'contact_type': note.contact_type,
                        'set_date': note.set_date,
                        'parent_note_id': note.parent_note_id,
                        'peer_advising_department_id': note.peer_advising_department_id,
                        'created_at': note.created_at,
                        'updated_at': note.updated_at,
                        'searchable_text': searchable_text,
                    })
                    if note.topics:
                        for t in note.topics:
                            topics_insert_values.append({
                                'id': note_id,
                                'boa_id': note.id,
                                'sid': note.sid,
                                'topic': t.topic,
                            })
                notes_insert_sql = """INSERT INTO boa_app_rds_data.advising_notes
                    (id, student_sid, boa_id, advisor_uid, author_name, advisor_first_name, advisor_last_name,
                    author_dept_codes, subject, note_body, is_private, contact_type, set_date,
                    parent_note_id, peer_advising_department_id, created_at, updated_at)
                  VALUES (
                    :id, :student_sid, :boa_id, :advisor_uid, :author_name, :advisor_first_name, :advisor_last_name,
                    CAST(:author_dept_codes AS varchar[]), :subject, :note_body, :is_private, :contact_type, :set_date,
                    :parent_note_id, :peer_advising_department_id, :created_at, :updated_at)
                  ON CONFLICT (id)
                  DO UPDATE SET
                    student_sid = EXCLUDED.student_sid,
                    boa_id = EXCLUDED.boa_id,
                    advisor_uid = EXCLUDED.advisor_uid,
                    author_name = EXCLUDED.author_name,
                    advisor_first_name = EXCLUDED.advisor_first_name,
                    advisor_last_name = EXCLUDED.advisor_last_name,
                    author_dept_codes = EXCLUDED.author_dept_codes,
                    subject = EXCLUDED.subject,
                    note_body = EXCLUDED.note_body,
                    is_private = EXCLUDED.is_private,
                    contact_type = EXCLUDED.contact_type,
                    set_date = EXCLUDED.set_date,
                    parent_note_id = EXCLUDED.parent_note_id,
                    peer_advising_department_id = EXCLUDED.peer_advising_department_id,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at;
                  INSERT INTO boa_app_rds_data.advising_notes_search_index
                    (id, fts_index)
                  VALUES (:id, TO_TSVECTOR('english', :searchable_text))
                  ON CONFLICT(id)
                  DO UPDATE SET
                    fts_index = EXCLUDED.fts_index;
                  INSERT INTO boa_app_rds_data.advising_note_authors_index
                    (advisor_name, advisor_uid)
                  VALUES (:author_name, :advisor_uid)
                  ON CONFLICT(advisor_name)
                  DO UPDATE SET
                    advisor_uid = EXCLUDED.advisor_uid;"""
                conn.execute(text(notes_insert_sql), notes_insert_values)

                if len(topics_insert_values):
                    topics_insert_sql = """INSERT INTO boa_app_rds_data.advising_note_topics
                          (id, boa_id, sid, topic)
                        VALUES (:id, :boa_id, :sid, :topic)"""
                    conn.execute(text(topics_insert_sql), topics_insert_values)

            if deleted_notes:
                params = {
                    'delete_ids': [f'boa-{note.sid}-{note.id}' for note in deleted_notes],
                }
                sql = """DELETE FROM boa_app_rds_data.advising_notes
                      WHERE id = ANY(:delete_ids);
                    DELETE FROM boa_app_rds_data.advising_notes_search_index
                      WHERE id = ANY(:delete_ids);
                    DELETE FROM boa_app_rds_data.advising_note_topics
                      WHERE id = ANY(:delete_ids)"""
                conn.execute(text(sql), params)
    finally:
        engine.dispose()


# Helpers for the search (notes, appointents, eforms) tests.

def _search_filter_combinations(filters):
    names = list(filters)
    return [combo for count in range(len(names) + 1) for combo in itertools.combinations(names, count)]


def active_search_criteria(filters, active_filters):
    criteria = {}
    for name in active_filters:
        value = filters[name]
        if name in ('datetime_from', 'datetime_to'):
            value = localized_timestamp_to_utc(f'{value}T00:00:00')
        criteria[name] = value
    if 'search_phrases' not in filters:
        criteria.setdefault('search_phrase', None)
    return criteria

def assert_every_search_filter_combination(filters, search, expected_keys, limit):
    """Run the search once per combination of search filters, and report every combination whose results are wrong."""
    combinations = _search_filter_combinations(filters)
    assert len(combinations) == 2 ** len(filters)
    failures = []
    for active_filters in combinations:
        criteria = active_search_criteria(filters, active_filters)
        expected = sorted(expected_keys(**criteria), key=repr)
        assert len(expected) < limit, 'Expected results exceed one page; raise the limit or narrow the fixture data.'
        results = search(criteria)
        actual = sorted([row['id'] for row in results['rows']], key=repr)
        if actual != expected or results['total'] != len(expected):
            failures.append(
                f"{' + '.join(active_filters) or 'no search filters'}: "
                f"total_matching_count={results['total']}, "
                f'missing={[k for k in expected if k not in actual]}, '
                f'unexpected={[k for k in actual if k not in expected]}, '
                f'duplicates={sorted({k for k in actual if actual.count(k) > 1}, key=repr)}',
            )
    assert not failures, f'{len(failures)} of {len(combinations)} search filter combinations failed:\n' + '\n'.join(failures)


def assert_search_filters_not_vacuous(filters, expected_keys_fn):
    all_keys = set(expected_keys_fn(**active_search_criteria(filters, ())))
    for name in filters:
        filtered_keys = set(expected_keys_fn(**active_search_criteria(filters, (name,))))
        assert filtered_keys, f'Filter {name} matches nothing'
        assert filtered_keys < all_keys, f'Filter {name} excludes nothing'

def expected_fts_results(index_table, id_column, search_phrase, execute):
    """Return IDs matching the search phrase, or None when there is no phrase to match."""
    if not search_phrase:
        return None
    sql = f"SELECT {id_column} AS id FROM {index_table} WHERE fts_index @@ plainto_tsquery('english', %(search_phrase)s)"
    return {row['id'] for row in execute(sql, search_phrase=search_phrase)}


def in_date_range(timestamp, datetime_from, datetime_to):
    if datetime_from and (timestamp is None or timestamp < datetime_from):
        return False
    return not (datetime_to and (timestamp is None or timestamp >= datetime_to))


def legacy_advisor_match(row, advisor_uids, advisor_sid):
    if not advisor_uids and not advisor_sid:
        return True
    uid_match = bool(advisor_uids) and (row['created_by'] in advisor_uids or row['advisor_uid'] in advisor_uids)
    sid_match = bool(advisor_sid) and row['advisor_sid'] == advisor_sid
    return uid_match or sid_match


def legacy_timestamp(row):
    # UCBCONVERSION rows have no meaningful updated_at, so they are filtered on created_at.
    return row['created_at'] if row['created_by'] == 'UCBCONVERSION' else row['updated_at']


def get_topic_matches(topics_table, topic, execute):
    """Return IDs of notes or appointments tagged with the topic, or None when there is no topic to match."""
    if not topic:
        return None
    return {row['id'] for row in execute(f'SELECT id FROM {topics_table} WHERE topic = %(topic)s', topic=topic)}
