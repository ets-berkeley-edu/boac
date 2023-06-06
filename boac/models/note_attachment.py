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

from datetime import datetime

from boac import db
from boac.lib.util import get_attachment_filename, note_attachment_to_api_json, put_attachment_to_s3
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
    def create(cls, note_id, name, byte_stream, uploaded_by):
        return NoteAttachment(
            note_id=note_id,
            path_to_attachment=put_attachment_to_s3(name=name, byte_stream=byte_stream),
            uploaded_by_uid=uploaded_by,
        )

    @classmethod
    def find_by_id(cls, attachment_id):
        return cls.query.filter(and_(cls.id == attachment_id, cls.deleted_at == None)).first()  # noqa: E711

    def get_user_filename(self):
        return get_attachment_filename(self.id, self.path_to_attachment)

    def to_api_json(self):
        return note_attachment_to_api_json(self)
