"""
Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.

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

from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ENUM

from boac import db, std_commit
from boac.lib.util import to_iso_format, utc_now
from boac.models.base import Base

user_tag_object_type_enum = ENUM(
    'note',
    'comment',
    name='user_tag_object_types',
    create_type=False,
)


class UserTag(Base):
    """A mention of a BOA user in a note or comment. The text lives in notes or comments; this row links the two."""

    __tablename__ = 'user_tags'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    # Points to notes.id or comments.id depending on object_type. The database also keeps generated note_id and
    # comment_id columns, which carry the real foreign keys; they are never written from here.
    object_id = db.Column(db.Integer, nullable=False)
    object_type = db.Column(user_tag_object_type_enum, nullable=False)
    email_notification_sent = db.Column(db.Boolean, nullable=False, default=False)
    read_by_user = db.Column(db.Boolean, nullable=False, default=False)
    archived_by_user = db.Column(db.Boolean, nullable=False, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, user_id, object_id, object_type):
        self.user_id = user_id
        self.object_id = object_id
        self.object_type = object_type

    def __repr__(self):
        return f"""<UserTag id={self.id},
                    user_id={self.user_id},
                    object_id={self.object_id},
                    object_type={self.object_type},
                    email_notification_sent={self.email_notification_sent},
                    read_by_user={self.read_by_user},
                    archived_by_user={self.archived_by_user},
                    created_at={self.created_at},
                    updated_at={self.updated_at},
                    deleted_at={self.deleted_at}>"""

    @classmethod
    def create(cls, user_id, object_id, object_type):
        _validate_object_type(object_type)
        # Saving a note or comment again with the same mention must not tag the user twice.
        user_tag = cls.find(user_id=user_id, object_id=object_id, object_type=object_type)
        if user_tag:
            return user_tag
        user_tag = cls(user_id=user_id, object_id=object_id, object_type=object_type)
        db.session.add(user_tag)
        std_commit()
        return user_tag

    @classmethod
    def delete(cls, user_id, object_id, object_type):
        # For a mention removed from a note or comment that is otherwise still there.
        _validate_object_type(object_type)
        user_tag = cls.find(user_id=user_id, object_id=object_id, object_type=object_type)
        if user_tag:
            user_tag.deleted_at = utc_now()
            std_commit()
            return True
        return False

    @classmethod
    def delete_for_object(cls, object_id, object_type, except_user_ids=()):
        # For a deleted note or comment. Pass except_user_ids to keep the tags that are still in an edited text.
        _validate_object_type(object_type)
        criteria = [
            cls.object_id == int(object_id),
            cls.object_type == object_type,
            cls.deleted_at == None,  # noqa: E711
        ]
        if except_user_ids:
            criteria.append(cls.user_id.notin_(except_user_ids))
        now = utc_now()
        user_tags = cls.query.filter(and_(*criteria)).all()
        for user_tag in user_tags:
            user_tag.deleted_at = now
        std_commit()
        return len(user_tags)

    @classmethod
    def find(cls, user_id, object_id, object_type):
        return cls.query.filter(
            and_(
                cls.user_id == user_id,
                cls.object_id == int(object_id),
                cls.object_type == object_type,
                cls.deleted_at == None,  # noqa: E711
            ),
        ).first()

    @classmethod
    def get_all_for_user(cls, user_id, archived=False):
        return cls.query.filter(
            and_(cls.user_id == user_id, cls.deleted_at == None, cls.archived_by_user == archived),  # noqa: E711
        ).order_by(cls.created_at.desc(), cls.id.desc()).all()

    def to_api_json(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'objectId': self.object_id,
            'objectType': self.object_type,
            'emailNotificationSent': self.email_notification_sent,
            'readByUser': self.read_by_user,
            'archivedByUser': self.archived_by_user,
            'createdAt': to_iso_format(self.created_at),
            'updatedAt': to_iso_format(self.updated_at),
        }


def _validate_object_type(object_type):
    if object_type not in user_tag_object_type_enum.enums:
        raise ValueError(f'Invalid user tag object type: {object_type}')
