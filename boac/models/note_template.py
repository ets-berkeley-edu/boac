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

from boac import db, std_commit
from boac.lib.util import titleize, vacuum_whitespace
from boac.models.authorized_user import AuthorizedUser
from boac.models.base import Base
from boac.models.note_template_attachment import NoteTemplateAttachment
from boac.models.note_template_topic import NoteTemplateTopic
from dateutil.tz import tzutc
from sqlalchemy import and_


class NoteTemplate(Base):
    __tablename__ = 'note_templates'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    creator_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    topics = db.relationship(
        'NoteTemplateTopic',
        primaryjoin='and_(NoteTemplate.id==NoteTemplateTopic.note_template_id)',
        back_populates='note_template',
        lazy=True,
    )
    attachments = db.relationship(
        'NoteTemplateAttachment',
        primaryjoin='and_(NoteTemplate.id==NoteTemplateAttachment.note_template_id, NoteTemplateAttachment.deleted_at==None)',
        back_populates='note_template',
        lazy=True,
    )

    __table_args__ = (db.UniqueConstraint(
        'creator_id',
        'title',
        name='student_groups_owner_id_name_unique_constraint',
    ),)

    def __init__(self, creator_id, title, subject, body):
        self.creator_id = creator_id
        self.title = title
        self.subject = subject
        self.body = body

    @classmethod
    def create(cls, creator_id, title, subject, body='', topics=(), attachments=()):
        creator = AuthorizedUser.find_by_id(creator_id)
        if creator:
            note_template = cls(creator_id, title, subject, body)
            for topic in topics:
                note_template.topics.append(
                    NoteTemplateTopic.create(note_template.id, titleize(vacuum_whitespace(topic))),
                )
            for byte_stream_bundle in attachments:
                note_template.attachments.append(
                    NoteTemplateAttachment.create(
                        note_template_id=note_template.id,
                        name=byte_stream_bundle['name'],
                        byte_stream=byte_stream_bundle['byte_stream'],
                        uploaded_by=creator.uid,
                    ),
                )
            db.session.add(note_template)
            std_commit()
            return note_template

    @classmethod
    def find_by_id(cls, note_template_id):
        return cls.query.filter(and_(cls.id == note_template_id, cls.deleted_at == None)).first()  # noqa: E711

    def to_api_json(self):
        attachments = [a.to_api_json() for a in self.attachments if not a.deleted_at]
        topics = [t.to_api_json() for t in self.topics if not t.deleted_at]
        return {
            'id': self.id,
            'attachments': attachments,
            'title': self.title,
            'subject': self.subject,
            'body': self.body,
            'topics': topics,
            'createdAt': self.created_at.astimezone(tzutc()).isoformat(),
            'updatedAt': self.updated_at.astimezone(tzutc()).isoformat(),
        }
