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

from boac import db, std_commit
from boac.lib.util import titleize, utc_now, vacuum_whitespace
from boac.models.authorized_user import AuthorizedUser
from boac.models.base import Base
from boac.models.note_draft_attachment import NoteDraftAttachment
from boac.models.note_draft_topic import NoteDraftTopic
from dateutil.tz import tzutc
from sqlalchemy import and_, text
from sqlalchemy.dialects.postgresql import ARRAY


class NoteDraft(Base):
    __tablename__ = 'note_drafts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    body = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    sids = db.Column(ARRAY(db.String(80)), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    topics = db.relationship(
        'NoteDraftTopic',
        primaryjoin='and_(NoteDraft.id==NoteDraftTopic.note_draft_id)',
        back_populates='note_draft',
        lazy=True,
    )
    attachments = db.relationship(
        'NoteDraftAttachment',
        primaryjoin='and_(NoteDraft.id==NoteDraftAttachment.note_draft_id, NoteDraftAttachment.deleted_at==None)',
        back_populates='note_draft',
        lazy=True,
    )

    __table_args__ = (db.UniqueConstraint(
        'creator_id',
        'title',
        'deleted_at',
        name='student_groups_owner_id_name_unique_constraint',
    ),)

    def __init__(self, body, creator_id, sids, subject, title):
        self.body = body
        self.creator_id = creator_id
        self.sids = sids
        self.subject = subject
        self.title = title

    @classmethod
    def create(
            cls,
            creator_id,
            sids,
            subject,
            title,
            attachments=(),
            body='',
            topics=(),
    ):
        creator = AuthorizedUser.find_by_id(creator_id)
        if creator:
            note_draft = cls(
                body=body,
                creator_id=creator_id,
                sids=sids,
                subject=subject,
                title=title,
            )
            for topic in topics:
                note_draft.topics.append(
                    NoteDraftTopic.create(note_draft.id, titleize(vacuum_whitespace(topic))),
                )
            for byte_stream_bundle in attachments:
                note_draft.attachments.append(
                    NoteDraftAttachment.create(
                        note_draft_id=note_draft.id,
                        name=byte_stream_bundle['name'],
                        byte_stream=byte_stream_bundle['byte_stream'],
                        uploaded_by=creator.uid,
                    ),
                )
            db.session.add(note_draft)
            std_commit()
            return note_draft

    @classmethod
    def find_by_id(cls, note_draft_id):
        return cls.query.filter(and_(cls.id == note_draft_id, cls.deleted_at == None)).first()  # noqa: E711

    @classmethod
    def get_drafts_created_by(cls, creator_id):
        return cls.query.filter_by(creator_id=creator_id, deleted_at=None).order_by(cls.title).all()

    @classmethod
    def get_draft_note_count(cls, user_id=None):
        sql = 'SELECT count(*) FROM note_drafts WHERE deleted_at IS NULL'
        if user_id:
            sql += ' AND creator_id = :creator_id'
        results = db.session.execute(text(sql), {'creator_id': user_id})
        return results.first()['count']

    @classmethod
    def rename(cls, note_draft_id, title):
        note_draft = cls.find_by_id(note_draft_id)
        if note_draft:
            note_draft.title = title
            std_commit()
            return note_draft
        else:
            return None

    @classmethod
    def update(
            cls,
            body,
            note_draft_id,
            sids,
            subject,
            attachments=(),
            delete_attachment_ids=(),
            topics=(),
    ):
        note_draft = cls.find_by_id(note_draft_id)
        if note_draft:
            creator = AuthorizedUser.find_by_id(note_draft.creator_id)
            note_draft.body = body
            note_draft.sids = sids
            note_draft.subject = subject
            cls._update_note_draft_topics(note_draft, topics)
            if delete_attachment_ids:
                cls._delete_attachments(note_draft, delete_attachment_ids)
            for byte_stream_bundle in attachments:
                cls._add_attachment(note_draft, byte_stream_bundle, creator.uid)
            std_commit()
            db.session.refresh(note_draft)
            return note_draft
        else:
            return None

    @classmethod
    def delete(cls, note_draft_id):
        note_draft = cls.find_by_id(note_draft_id)
        if note_draft:
            now = utc_now()
            note_draft.deleted_at = now
            for attachment in note_draft.attachments:
                attachment.deleted_at = now
            for topic in note_draft.topics:
                db.session.delete(topic)
            std_commit()

    def to_api_json(self):
        attachments = [a.to_api_json() for a in self.attachments if not a.deleted_at]
        topics = [t.to_api_json() for t in self.topics]
        return {
            'id': self.id,
            'attachments': attachments,
            'body': self.body,
            'sids': self.sids,
            'subject': self.subject,
            'title': self.title,
            'topics': topics,
            'createdAt': self.created_at.astimezone(tzutc()).isoformat(),
            'updatedAt': self.updated_at.astimezone(tzutc()).isoformat(),
        }

    @classmethod
    def _update_note_draft_topics(cls, note_draft, topics):
        modified = False
        now = utc_now()
        topics = set([titleize(vacuum_whitespace(topic)) for topic in topics])
        existing_topics = set(note_topic.topic for note_topic in NoteDraftTopic.find_by_note_draft_id(note_draft.id))
        topics_to_delete = existing_topics - topics
        topics_to_add = topics - existing_topics
        for topic in topics_to_delete:
            topic_to_delete = next((t for t in note_draft.topics if t.topic == topic), None)
            if topic_to_delete:
                NoteDraftTopic.delete(topic_to_delete.id)
                modified = True
        for topic in topics_to_add:
            note_draft.topics.append(
                NoteDraftTopic.create(note_draft, topic),
            )
            modified = True
        if modified:
            note_draft.updated_at = now

    @classmethod
    def _add_attachment(cls, note_draft, attachment, uploaded_by_uid):
        note_draft.attachments.append(
            NoteDraftAttachment.create(
                note_draft_id=note_draft.id,
                name=attachment['name'],
                byte_stream=attachment['byte_stream'],
                uploaded_by=uploaded_by_uid,
            ),
        )
        note_draft.updated_at = utc_now()

    @classmethod
    def _delete_attachments(cls, note_draft, delete_attachment_ids):
        modified = False
        now = utc_now()
        for attachment in note_draft.attachments:
            if attachment.id in delete_attachment_ids:
                attachment.deleted_at = now
                modified = True
        if modified:
            note_draft.updated_at = now
