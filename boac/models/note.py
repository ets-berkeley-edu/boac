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

import json

from boac import db, std_commit
from boac.lib.background import bg_execute
from boac.lib.util import get_benchmarker, put_attachment_to_s3, safe_strftime, utc_now
from boac.models.authorized_user import AuthorizedUser
from boac.models.base import Base
from boac.models.note_attachment import NoteAttachment
from boac.models.note_template_attachment import NoteTemplateAttachment
from boac.models.note_topic import NoteTopic
from dateutil.tz import tzutc
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.sql import text


note_contact_type_enum = ENUM(
    'Email',
    'Phone',
    'Online same day',
    'Online scheduled',
    'In-person same day',
    'In person scheduled',
    'Admin',
    name='note_contact_types',
    create_type=False,
)


class Note(Base):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    author_uid = db.Column(db.String(255), nullable=False)
    author_name = db.Column(db.String(255), nullable=False)
    author_role = db.Column(db.String(255), nullable=False)
    author_dept_codes = db.Column(ARRAY(db.String), nullable=False)
    body = db.Column(db.Text, nullable=False)
    contact_type = db.Column(note_contact_type_enum, nullable=True)
    is_private = db.Column(db.Boolean, nullable=False, default=False)
    set_date = db.Column(db.Date)
    sid = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    topics = db.relationship(
        'NoteTopic',
        primaryjoin='and_(Note.id==NoteTopic.note_id, NoteTopic.deleted_at==None)',
        back_populates='note',
        lazy=True,
    )
    attachments = db.relationship(
        'NoteAttachment',
        primaryjoin='and_(Note.id==NoteAttachment.note_id, NoteAttachment.deleted_at==None)',
        back_populates='note',
        lazy=True,
    )

    def __init__(
        self,
        author_uid,
        author_name,
        author_role,
        author_dept_codes,
        body,
        sid,
        subject,
        contact_type=None,
        is_private=False,
        set_date=None,
    ):
        self.author_dept_codes = author_dept_codes
        self.author_name = author_name
        self.author_role = author_role
        self.author_uid = author_uid
        self.body = body
        self.contact_type = contact_type
        self.is_private = is_private
        self.set_date = set_date
        self.sid = sid
        self.subject = subject

    @classmethod
    def find_by_id(cls, note_id):
        return cls.query.filter(and_(cls.id == note_id, cls.deleted_at == None)).first()  # noqa: E711

    @classmethod
    def create(
            cls,
            author_uid,
            author_name,
            author_role,
            author_dept_codes,
            sid,
            subject,
            body,
            topics=(),
            attachments=(),
            contact_type=None,
            is_private=False,
            set_date=None,
            template_attachment_ids=(),
    ):
        ids_by_sid = cls.create_batch(
            author_id=AuthorizedUser.get_id_per_uid(author_uid),
            author_uid=author_uid,
            author_name=author_name,
            author_role=author_role,
            author_dept_codes=author_dept_codes,
            sids=[sid],
            subject=subject,
            body=body,
            contact_type=contact_type,
            is_private=is_private,
            set_date=set_date,
            topics=topics,
            attachments=attachments,
            template_attachment_ids=template_attachment_ids,
        )

        def _get_note_id():
            values = list(ids_by_sid.values())
            return values[0] if len(values) > 0 else None
        return cls.find_by_id(_get_note_id())

    @classmethod
    def create_batch(
            cls,
            author_id,
            author_uid,
            author_name,
            author_role,
            author_dept_codes,
            body,
            contact_type,
            is_private,
            set_date,
            sids,
            subject,
            attachments=(),
            topics=(),
            template_attachment_ids=(),
    ):
        sid_count = len(sids)
        benchmark = get_benchmarker('begin note creation' if sid_count == 1 else f'begin creation of {sid_count} notes')
        ids_by_sid = _create_notes(
            author_id=author_id,
            author_uid=author_uid,
            author_name=author_name,
            author_role=author_role,
            author_dept_codes=author_dept_codes,
            body=body,
            contact_type=contact_type,
            is_private=is_private,
            set_date=set_date,
            sids=sids,
            subject=subject,
        )
        note_ids = list(ids_by_sid.values())
        benchmark('begin add 1 topic' if len(topics) == 1 else f'begin add {len(topics)} topics')
        _add_topics_to_notes(author_uid=author_uid, note_ids=note_ids, topics=topics)
        benchmark('begin add 1 attachment' if len(attachments) == 1 else f'begin add {len(attachments)} attachments')
        _add_attachments_to_notes(
            attachments=attachments,
            template_attachment_ids=template_attachment_ids,
            author_uid=author_uid,
            note_ids=note_ids,
        )
        benchmark('begin refresh search index')
        cls.refresh_search_index()
        benchmark('end note creation' if sid_count == 1 else f'end creation of {sid_count} notes')
        return ids_by_sid

    @classmethod
    def get_notes_report(cls):
        query = """
            SELECT
              n.author_uid, n.author_name, n.author_role, n.author_dept_codes, n.contact_type, n.is_private, n.set_date,
              n.sid, n.subject, n.created_at, n.updated_at, string_agg(t.topic, ', ') AS topics
            FROM notes n
            LEFT JOIN note_topics t ON (n.id = t.note_id AND t.deleted_at IS NULL)
            WHERE n.deleted_at IS NULL
            GROUP BY
              n.author_uid, n.author_name, n.author_role, n.author_dept_codes, n.contact_type, n.is_private, n.set_date,
              n.sid, n.subject, n.created_at, n.updated_at
            ORDER BY created_at
        """
        tz_utc = tzutc()
        api_json = []
        for row in db.session.execute(query):
            sid = row['sid']
            api_json.append({
                'author_uid': row['author_uid'],
                'author_name': row['author_name'],
                'author_role': row['author_role'],
                'author_dept_codes': f"{','.join(row['author_dept_codes'])}",
                'contact_type': row['contact_type'],
                'is_private': row['is_private'],
                'set_date': row['set_date'],
                'sid': sid,
                'student_first_name': None,
                'student_last_name': None,
                'subject': row['subject'],
                'topics': row['topics'],
                'created_at': row['created_at'].astimezone(tz_utc).isoformat(),
                'updated_at': row['updated_at'].astimezone(tz_utc).isoformat(),
            })
        return api_json

    @classmethod
    def search(
            cls,
            search_phrase,
            author_uid,
            student_csid,
            topic,
            datetime_from,
            datetime_to,
            include_private_notes=False,
    ):
        if search_phrase:
            fts_selector = """SELECT id, ts_rank(fts_index, plainto_tsquery('english', :search_phrase)) AS rank
                FROM notes_fts_index
                WHERE fts_index @@ plainto_tsquery('english', :search_phrase)"""
            params = {
                'search_phrase': search_phrase,
            }
        else:
            fts_selector = 'SELECT id, 0 AS rank FROM notes WHERE deleted_at IS NULL'
            params = {}

        if author_uid:
            author_filter = 'AND notes.author_uid = :author_uid'
            params.update({'author_uid': author_uid})
        else:
            author_filter = ''

        if student_csid:
            student_filter = 'AND notes.sid = :student_csid'
            params.update({'student_csid': student_csid})
        else:
            student_filter = ''

        date_filter = ''
        if datetime_from:
            date_filter += ' AND updated_at >= :datetime_from'
            params.update({'datetime_from': datetime_from})
        if datetime_to:
            date_filter += ' AND updated_at < :datetime_to'
            params.update({'datetime_to': datetime_to})
        if topic:
            topic_join = 'JOIN note_topics nt on nt.topic = :topic AND nt.note_id = notes.id'
            params.update({'topic': topic})
        else:
            topic_join = ''

        where_clause = '' if include_private_notes else 'WHERE notes.is_private IS FALSE'

        query = text(f"""
            SELECT notes.* FROM ({fts_selector}) AS fts
            JOIN notes
                ON fts.id = notes.id
                {author_filter}
                {student_filter}
                {date_filter}
            {topic_join}
            {where_clause}
            ORDER BY fts.rank DESC, notes.id
        """).bindparams(**params)
        result = db.session.execute(query)
        keys = result.keys()
        return [dict(zip(keys, row)) for row in result.fetchall()]

    @classmethod
    def refresh_search_index(cls):
        def _refresh_search_index(db_session):
            db_session.execute(text('REFRESH MATERIALIZED VIEW notes_fts_index'))
            db_session.execute(text('REFRESH MATERIALIZED VIEW advisor_author_index'))
            std_commit(session=db_session)
        bg_execute(_refresh_search_index)

    @classmethod
    def update(cls, note_id, subject, body=None, contact_type=None, is_private=False, set_date=None, topics=()):
        note = cls.find_by_id(note_id=note_id)
        if note:
            note.body = body
            note.contact_type = contact_type
            note.is_private = is_private
            note.set_date = set_date
            note.subject = subject
            cls._update_note_topics(note, topics)
            std_commit()
            db.session.refresh(note)
            cls.refresh_search_index()
            return note
        else:
            return None

    @classmethod
    def add_attachment(cls, note_id, attachment):
        note = cls.find_by_id(note_id=note_id)
        if note:
            cls._add_attachment(note, attachment)
            std_commit()
            return note
        else:
            return None

    @classmethod
    def delete_attachment(cls, note_id, attachment_id):
        note = cls.find_by_id(note_id=note_id)
        if note:
            cls._delete_attachments(note, (attachment_id,))
            std_commit()
            return note
        else:
            return None

    @classmethod
    def _update_note_topics(cls, note, topics):
        modified = False
        now = utc_now()
        topics = set(topics)
        existing_topics = set(note_topic.topic for note_topic in NoteTopic.find_by_note_id(note.id))
        topics_to_delete = existing_topics - topics
        topics_to_add = topics - existing_topics
        for topic in topics_to_delete:
            topic_to_delete = next((t for t in note.topics if t.topic == topic), None)
            if topic_to_delete:
                topic_to_delete.deleted_at = now
                modified = True
        for topic in topics_to_add:
            note.topics.append(
                NoteTopic.create(note, topic, note.author_uid),
            )
            modified = True
        if modified:
            note.updated_at = now

    @classmethod
    def _add_attachment(cls, note, attachment):
        note.attachments.append(
            NoteAttachment.create(
                note_id=note.id,
                name=attachment['name'],
                byte_stream=attachment['byte_stream'],
                uploaded_by=note.author_uid,
            ),
        )
        note.updated_at = utc_now()

    @classmethod
    def _delete_attachments(cls, note, delete_attachment_ids):
        modified = False
        now = utc_now()
        for attachment in note.attachments:
            if attachment.id in delete_attachment_ids:
                attachment.deleted_at = now
                modified = True
        if modified:
            note.updated_at = now

    @classmethod
    def get_notes_by_sid(cls, sid):
        # SQLAlchemy uses "magic methods" to create SQL; it requires '==' instead of 'is'.
        return cls.query.filter(and_(cls.sid == sid, cls.deleted_at == None)).order_by(cls.updated_at, cls.id).all()  # noqa: E711

    @classmethod
    def delete(cls, note_id):
        note = cls.find_by_id(note_id)
        if note:
            now = utc_now()
            note.deleted_at = now
            for attachment in note.attachments:
                attachment.deleted_at = now
            for topic in note.topics:
                topic.deleted_at = now
            std_commit()
            cls.refresh_search_index()

    def to_api_json(self):
        attachments = self.attachments_to_api_json()
        return {
            'id': self.id,
            'attachments': attachments,
            'authorUid': self.author_uid,
            'authorName': self.author_name,
            'authorRole': self.author_role,
            'authorDeptCodes': self.author_dept_codes,
            'body': self.body,
            'contactType': self.contact_type,
            'isPrivate': self.is_private,
            'setDate': safe_strftime(self.set_date, '%Y-%m-%d'),
            'sid': self.sid,
            'subject': self.subject,
            'topics': [topic.topic for topic in self.topics],
            'createdAt': self.created_at,
            'deletedAt': self.deleted_at,
            'updatedAt': self.updated_at,
        }

    def attachments_to_api_json(self):
        return [a.to_api_json() for a in self.attachments if not a.deleted_at]


def _create_notes(
        author_id,
        author_uid,
        author_name,
        author_role,
        author_dept_codes,
        body,
        contact_type,
        is_private,
        set_date,
        sids,
        subject,
):
    ids_by_sid = {}
    now = utc_now().strftime('%Y-%m-%dT%H:%M:%S+00')
    # The syntax of the following is what Postgres expects in json_populate_recordset(...)
    joined_author_dept_codes = '{' + ','.join(author_dept_codes) + '}'
    count_per_chunk = 10000
    for chunk in range(0, len(sids), count_per_chunk):
        sids_subset = sids[chunk:chunk + count_per_chunk]
        query = """
            INSERT INTO notes (author_dept_codes, author_name, author_role, author_uid, body, contact_type, is_private, set_date, sid, subject,
                               created_at, updated_at)
            SELECT author_dept_codes, author_name, author_role, author_uid, body, contact_type, is_private, set_date, sid, subject,
                   created_at, updated_at
            FROM json_populate_recordset(null::notes, :json_dumps)
            RETURNING id, sid;
        """
        data = [
            {
                'author_uid': author_uid,
                'author_name': author_name,
                'author_role': author_role,
                'author_dept_codes': joined_author_dept_codes,
                'sid': sid,
                'subject': subject,
                'body': body,
                'contact_type': contact_type,
                'is_private': is_private,
                'set_date': set_date,
                'created_at': now,
                'updated_at': now,
            } for sid in sids_subset
        ]
        results_of_chunk_query = {}
        for row in db.session.execute(query, {'json_dumps': json.dumps(data)}):
            sid = row['sid']
            results_of_chunk_query[sid] = row['id']
        # Yes, the note author has read the note.
        notes_read_query = """
            INSERT INTO notes_read (note_id, viewer_id, created_at)
            SELECT note_id, viewer_id, created_at
            FROM json_populate_recordset(null::notes_read, :json_dumps)
        """
        notes_read_data = [
            {
                'note_id': note_id,
                'viewer_id': author_id,
                'created_at': now,
            } for note_id in results_of_chunk_query.values()
        ]
        db.session.execute(notes_read_query, {'json_dumps': json.dumps(notes_read_data)})
        ids_by_sid.update(results_of_chunk_query)
    return ids_by_sid


def _add_topics_to_notes(author_uid, note_ids, topics):
    for topic in topics:
        count_per_chunk = 10000
        for chunk in range(0, len(note_ids), count_per_chunk):
            query = """
                INSERT INTO note_topics (author_uid, note_id, topic)
                SELECT author_uid, note_id, topic
                FROM json_populate_recordset(null::note_topics, :json_dumps);
            """
            note_ids_subset = note_ids[chunk:chunk + count_per_chunk]
            data = [
                {
                    'author_uid': author_uid,
                    'note_id': note_id,
                    'topic': topic,
                } for note_id in note_ids_subset
            ]
            db.session.execute(query, {'json_dumps': json.dumps(data)})


def _add_attachments_to_notes(attachments, template_attachment_ids, author_uid, note_ids):
    now = utc_now().strftime('%Y-%m-%d %H:%M:%S')

    def _add_attachment(_s3_path):
        count_per_chunk = 10000
        for chunk in range(0, len(note_ids), count_per_chunk):
            query = """
                INSERT INTO note_attachments (created_at, note_id, path_to_attachment, uploaded_by_uid)
                SELECT created_at, note_id, path_to_attachment, uploaded_by_uid
                FROM json_populate_recordset(null::note_attachments, :json_dumps);
            """
            note_ids_subset = note_ids[chunk:chunk + count_per_chunk]
            data = [
                {
                    'created_at': now,
                    'note_id': note_id,
                    'path_to_attachment': _s3_path,
                    'uploaded_by_uid': author_uid,
                } for note_id in note_ids_subset
            ]
            db.session.execute(query, {'json_dumps': json.dumps(data)})

    for byte_stream_bundle in attachments:
        s3_path = put_attachment_to_s3(name=byte_stream_bundle['name'], byte_stream=byte_stream_bundle['byte_stream'])
        _add_attachment(s3_path)
    if template_attachment_ids:
        for template_attachment in NoteTemplateAttachment.get_attachments(template_attachment_ids):
            _add_attachment(template_attachment.path_to_attachment)
