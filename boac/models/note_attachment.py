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
import re

from boac import db
from boac.externals import s3
from flask import current_app as app
import pytz
from sqlalchemy import and_


class NoteAttachment(db.Model):
    __tablename__ = 'note_attachments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    path_to_attachment = db.Column('path_to_attachment', db.String(255), nullable=False)
    uploaded_by_uid = db.Column('uploaded_by_uid', db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted_at = db.Column(db.DateTime)
    note = db.relationship('Note', back_populates='attachments')

    def __init__(self, note_id, path_to_attachment, uploaded_by_uid):
        self.note_id = note_id
        self.path_to_attachment = path_to_attachment
        self.uploaded_by_uid = uploaded_by_uid

    @classmethod
    def create_attachment(cls, note, name, byte_stream, uploaded_by):
        return NoteAttachment(
            note_id=note.id,
            path_to_attachment=cls.put_attachment_to_s3(name=name, byte_stream=byte_stream),
            uploaded_by_uid=uploaded_by,
        )

    @classmethod
    def put_attachment_to_s3(cls, name, byte_stream):
        bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
        base_path = app.config['DATA_LOCH_S3_BOA_NOTE_ATTACHMENTS_PATH']
        key_suffix = _localize_datetime(datetime.now()).strftime(f'%Y/%m/%d/%Y%m%d_%H%M%S_{name}')
        key = f'{base_path}/{key_suffix}'
        s3.put_binary_data_to_s3(
            bucket=bucket,
            key=key,
            binary_data=byte_stream,
        )
        return key

    @classmethod
    def find_by_id(cls, attachment_id):
        return cls.query.filter(and_(cls.id == attachment_id, cls.deleted_at == None)).first()  # noqa: E711

    @classmethod
    def find_by_note_id(cls, note_id):
        return cls.query.filter(and_(cls.note_id == note_id, cls.deleted_at == None)).all()  # noqa: E711

    def get_user_filename(self):
        raw_filename = self.path_to_attachment.rsplit('/', 1)[-1]
        match = re.match(r'\A\d{8}_\d{6}_(.+)\Z', raw_filename)
        if match:
            return match[1]
        else:
            app.logger.warn(f'Note attachment S3 filename did not match expected format: ID = {self.id}, filename = {raw_filename}')
            return raw_filename

    def to_api_json(self):
        filename = self.get_user_filename()
        return {
            'id': self.id,
            'displayName': filename,
            'filename': filename,
            'noteId': self.note_id,
            'uploadedBy': self.uploaded_by_uid,
        }


def _localize_datetime(dt):
    return dt.astimezone(pytz.timezone(app.config['TIMEZONE']))
