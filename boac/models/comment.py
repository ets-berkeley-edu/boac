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

from collections import defaultdict

from sqlalchemy import func, tuple_
from sqlalchemy.dialects.postgresql import ARRAY

from boac import db, std_commit
from boac.lib.util import to_iso_format, utc_now
from boac.merged.advising_note import get_note_author_summary
from boac.models.base import Base
from boac.models.comment_attachment import CommentAttachment
from boac.models.comment_parent import CommentParent


class Comment(Base):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    comment_parent_id = db.Column(db.Integer, db.ForeignKey('comment_parents.id'), nullable=False)
    author_uid = db.Column(db.String(255), nullable=False)
    author_name = db.Column(db.String(255), nullable=False)
    author_role = db.Column(db.String(255), nullable=False)
    author_dept_codes = db.Column(ARRAY(db.String), nullable=False)
    body = db.Column(db.Text, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    attachments = db.relationship(
        'CommentAttachment',
        primaryjoin='and_(Comment.id==CommentAttachment.comment_id, CommentAttachment.deleted_at==None)',
        back_populates='comment',
        lazy=True,
    )

    @classmethod
    def find_by_id(cls, comment_id):
        return cls.query.filter_by(id=comment_id).filter(cls.deleted_at == None).first()  # noqa: E711

    @classmethod
    def search_by_parent_types(
            cls,
            parent_types,
            search_phrases=None,
            author_uid=None,
            datetime_from=None,
            datetime_to=None,
            offset=0,
            limit=20,
    ):
        if not parent_types:
            return {'rows': [], 'total_matching_count': 0}

        query = (
            db.session.query(cls, CommentParent.parent_type, CommentParent.parent_id)
            .join(CommentParent, cls.comment_parent_id == CommentParent.id)
            .filter(
                cls.deleted_at == None,  # noqa: E711
                CommentParent.deleted_at == None,  # noqa: E711
                CommentParent.parent_type.in_(parent_types),
            )
        )
        if search_phrases:
            for phrase in search_phrases:
                query = query.filter(cls.body.ilike(f'%{phrase}%'))
        if author_uid:
            query = query.filter(cls.author_uid == author_uid)
        if datetime_from:
            query = query.filter(cls.created_at >= datetime_from)
        if datetime_to:
            query = query.filter(cls.created_at < datetime_to)

        total_matching_count = query.with_entities(func.count(cls.id)).scalar() or 0
        rows = (
            query.order_by(cls.created_at.desc(), cls.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {
            'rows': rows,
            'total_matching_count': total_matching_count,
        }

    @classmethod
    def get_comments_by_parents(cls, pairs):
        normalized = [(pt, str(pid)) for pt, pid in pairs if pt and pid is not None]
        grouped = defaultdict(list)
        if not normalized:
            return grouped
        rows = (
            db.session.query(cls, CommentParent.parent_type, CommentParent.parent_id)
            .join(CommentParent, cls.comment_parent_id == CommentParent.id)
            .filter(
                cls.deleted_at == None,  # noqa: E711
                CommentParent.deleted_at == None,  # noqa: E711
                tuple_(CommentParent.parent_type, CommentParent.parent_id).in_(normalized),
            )
            .order_by(cls.created_at.asc(), cls.id.asc())
            .all()
        )
        for comment, parent_type, parent_id in rows:
            grouped[(parent_type, parent_id)].append(comment)
        return grouped

    @classmethod
    def create(
            cls,
            comment_parent_id,
            author_uid,
            author_name,
            author_role,
            author_dept_codes,
            body,
            attachments=(),
    ):
        comment = Comment(
            comment_parent_id=comment_parent_id,
            author_uid=author_uid,
            author_name=author_name,
            author_role=author_role,
            author_dept_codes=author_dept_codes,
            body=body,
        )
        db.session.add(comment)
        std_commit()
        db.session.refresh(comment)
        for attachment in attachments:
            comment.attachments.append(
                CommentAttachment.create(
                    comment_id=comment.id,
                    name=attachment['name'],
                    byte_stream=attachment['byte_stream'],
                    uploaded_by=author_uid,
                ),
            )
        std_commit()
        db.session.refresh(comment)
        return comment

    def update(self, body, delete_attachment_ids=(), new_attachments=()):
        now = utc_now()
        delete_attachment_ids = set(delete_attachment_ids)
        for attachment in self.attachments:
            if attachment.id in delete_attachment_ids:
                attachment.deleted_at = now
        self.body = body
        self.updated_at = now
        for attachment in new_attachments:
            self.attachments.append(
                CommentAttachment.create(
                    comment_id=self.id,
                    name=attachment['name'],
                    byte_stream=attachment['byte_stream'],
                    uploaded_by=self.author_uid,
                ),
            )
        std_commit()
        db.session.refresh(self)
        return self

    def soft_delete(self):
        now = utc_now()
        for attachment in CommentAttachment.query.filter(
            CommentAttachment.comment_id == self.id,
            CommentAttachment.deleted_at == None,  # noqa: E711
        ).all():
            attachment.deleted_at = now
        self.deleted_at = now
        std_commit()
        db.session.refresh(self)
        return self

    def to_api_json(self, read=False):
        return {
            'id': self.id,
            'commentParentId': self.comment_parent_id,
            'author': get_note_author_summary({
                'authorUid': self.author_uid,
                'authorName': self.author_name,
                'authorRole': self.author_role,
                'authorDeptCodes': self.author_dept_codes,
            }),
            'body': self.body,
            'message': self.body,
            'attachments': [a.to_api_json() for a in self.attachments if not a.deleted_at],
            'createdAt': to_iso_format(self.created_at),
            'updatedAt': self.resolve_updated_at(),
            'deletedAt': to_iso_format(self.deleted_at),
            'read': bool(read),
        }

    def resolve_updated_at(self):
        if self.created_at and self.updated_at and (self.updated_at - self.created_at).seconds:
            return to_iso_format(self.updated_at)
