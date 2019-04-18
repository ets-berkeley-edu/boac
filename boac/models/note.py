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

from datetime import datetime

from boac import db, std_commit
from boac.externals import s3
from boac.models.base import Base
from boac.models.note_attachment import NoteAttachment
from flask import current_app as app
import pytz
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import text


class Note(Base):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    author_uid = db.Column(db.String(255), nullable=False)
    author_name = db.Column(db.String(255), nullable=False)
    author_role = db.Column(db.String(255), nullable=False)
    author_dept_codes = db.Column(ARRAY(db.String), nullable=False)
    sid = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    attachments = db.relationship(
        'NoteAttachment',
        primaryjoin='and_(Note.id==NoteAttachment.note_id, NoteAttachment.deleted_at==None)',
        back_populates='note',
        lazy=True,
    )

    def __init__(self, author_uid, author_name, author_role, author_dept_codes, sid, subject, body):
        self.author_uid = author_uid
        self.author_name = author_name
        self.author_role = author_role
        self.author_dept_codes = author_dept_codes
        self.sid = sid
        self.subject = subject
        self.body = body

    @classmethod
    def find_by_id(cls, note_id):
        return cls.query.filter(and_(cls.id == note_id, cls.deleted_at == None)).first()  # noqa: E711

    @classmethod
    def create(cls, author_uid, author_name, author_role, author_dept_codes, sid, subject, body, attachments=()):
        note = cls(author_uid, author_name, author_role, author_dept_codes, sid, subject, body)
        for byte_stream_bundle in attachments:
            note.attachments.append(
                _create_attachment(
                    note=note,
                    name=byte_stream_bundle['name'],
                    byte_stream=byte_stream_bundle['byte_stream'],
                    uploaded_by=author_uid,
                ),
            )
        db.session.add(note)
        std_commit()
        cls.refresh_search_index()
        return note

    @classmethod
    def search(cls, search_phrase, sid_filter):
        query = text("""
            SELECT notes.* FROM (
                SELECT id, ts_rank(fts_index, plainto_tsquery('english', :search_phrase)) AS rank
                FROM notes_fts_index
                WHERE fts_index @@ plainto_tsquery('english', :search_phrase)
            ) AS fts
            JOIN notes
                ON fts.id = notes.id
                AND notes.sid = ANY(:sid_filter)
            ORDER BY fts.rank DESC, notes.id
        """).bindparams(search_phrase=search_phrase, sid_filter=sid_filter)
        result = db.session.execute(query)
        keys = result.keys()
        return [dict(zip(keys, row)) for row in result.fetchall()]

    @classmethod
    def refresh_search_index(cls):
        db.session.execute(text('REFRESH MATERIALIZED VIEW notes_fts_index'))
        std_commit()

    @classmethod
    def update(cls, note_id, subject, body, attachments=(), delete_attachment_ids=()):
        note = cls.find_by_id(note_id=note_id)
        if note:
            note.subject = subject
            note.body = body
            if delete_attachment_ids:
                for attachment in note.attachments:
                    now = datetime.now()
                    if attachment.id in delete_attachment_ids:
                        attachment.deleted_at = now
            for byte_stream_bundle in attachments:
                note.attachments.append(
                    _create_attachment(
                        note=note,
                        name=byte_stream_bundle['name'],
                        byte_stream=byte_stream_bundle['byte_stream'],
                        uploaded_by=note.author_uid,
                    ),
                )
            std_commit()
            cls.refresh_search_index()
            return note
        else:
            return None

    @classmethod
    def get_notes_by_sid(cls, sid):
        # SQLAlchemy uses "magic methods" to create SQL; it requires '==' instead of 'is'.
        return cls.query.filter(and_(cls.sid == sid, cls.deleted_at == None)).all()  # noqa: E711

    @classmethod
    def delete(cls, note_id):
        note = cls.find_by_id(note_id)
        if note:
            now = datetime.now()
            note.deleted_at = now
            for attachment in note.attachments:
                attachment.deleted_at = now
            std_commit()
            cls.refresh_search_index()

    def to_api_json(self):
        attachments = [a.to_api_json() for a in self.attachments if not a.deleted_at]
        return {
            'id': self.id,
            'attachments': attachments,
            'authorUid': self.author_uid,
            'authorName': self.author_name,
            'authorRole': self.author_role,
            'authorDeptCodes': self.author_dept_codes,
            'sid': self.sid,
            'subject': self.subject,
            'body': self.body,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }


def _create_attachment(note, name, byte_stream, uploaded_by):
    bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
    base_path = app.config['DATA_LOCH_S3_BOA_NOTE_ATTACHMENTS_PATH']
    key_suffix = _localize_datetime(datetime.now()).strftime(f'%Y/%m/%d/{name}')
    key = f'{base_path}/{key_suffix}'
    s3.put_binary_data_to_s3(
        bucket=bucket,
        key=key,
        binary_data=byte_stream,
    )
    return NoteAttachment(
        note_id=note.id,
        path_to_attachment=key,
        uploaded_by_uid=uploaded_by,
    )


def _localize_datetime(dt):
    return dt.astimezone(pytz.timezone(app.config['TIMEZONE']))
