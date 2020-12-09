"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.lib.util import titleize, utc_now, vacuum_whitespace
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
        'deleted_at',
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

    @classmethod
    def get_templates_created_by(cls, creator_id):
        return cls.query.filter_by(creator_id=creator_id, deleted_at=None).order_by(cls.title).all()

    @classmethod
    def rename(cls, note_template_id, title):
        note_template = cls.find_by_id(note_template_id)
        if note_template:
            note_template.title = title
            std_commit()
            return note_template
        else:
            return None

    @classmethod
    def update(cls, note_template_id, subject, body, topics=(), attachments=(), delete_attachment_ids=()):
        note_template = cls.find_by_id(note_template_id)
        if note_template:
            creator = AuthorizedUser.find_by_id(note_template.creator_id)
            note_template.subject = subject
            note_template.body = body
            cls._update_note_template_topics(note_template, topics)
            if delete_attachment_ids:
                cls._delete_attachments(note_template, delete_attachment_ids)
            for byte_stream_bundle in attachments:
                cls._add_attachment(note_template, byte_stream_bundle, creator.uid)
            std_commit()
            db.session.refresh(note_template)
            return note_template
        else:
            return None

    @classmethod
    def delete(cls, note_template_id):
        note_template = cls.find_by_id(note_template_id)
        if note_template:
            now = utc_now()
            note_template.deleted_at = now
            for attachment in note_template.attachments:
                attachment.deleted_at = now
            for topic in note_template.topics:
                db.session.delete(topic)
            std_commit()

    def to_api_json(self):
        attachments = [a.to_api_json() for a in self.attachments if not a.deleted_at]
        topics = [t.to_api_json() for t in self.topics]
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

    @classmethod
    def _update_note_template_topics(cls, note_template, topics):
        modified = False
        now = utc_now()
        topics = set([titleize(vacuum_whitespace(topic)) for topic in topics])
        existing_topics = set(note_topic.topic for note_topic in NoteTemplateTopic.find_by_note_template_id(note_template.id))
        topics_to_delete = existing_topics - topics
        topics_to_add = topics - existing_topics
        for topic in topics_to_delete:
            topic_to_delete = next((t for t in note_template.topics if t.topic == topic), None)
            if topic_to_delete:
                NoteTemplateTopic.delete(topic_to_delete.id)
                modified = True
        for topic in topics_to_add:
            note_template.topics.append(
                NoteTemplateTopic.create(note_template, topic),
            )
            modified = True
        if modified:
            note_template.updated_at = now

    @classmethod
    def _add_attachment(cls, note_template, attachment, uploaded_by_uid):
        note_template.attachments.append(
            NoteTemplateAttachment.create(
                note_template_id=note_template.id,
                name=attachment['name'],
                byte_stream=attachment['byte_stream'],
                uploaded_by=uploaded_by_uid,
            ),
        )
        note_template.updated_at = utc_now()

    @classmethod
    def _delete_attachments(cls, note_template, delete_attachment_ids):
        modified = False
        now = utc_now()
        for attachment in note_template.attachments:
            if attachment.id in delete_attachment_ids:
                attachment.deleted_at = now
                modified = True
        if modified:
            note_template.updated_at = now
