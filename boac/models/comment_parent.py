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

from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ENUM

from boac import db, std_commit

comment_parent_type_enum = ENUM(
    'appointment',
    'course_load_eform',
    'cpp_change_eform',
    'late_drop_eform',
    name='comment_parent_types',
    create_type=False,
)


class CommentParent(db.Model):
    __tablename__ = 'comment_parents'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    parent_id = db.Column(db.String(255), nullable=False)
    parent_type = db.Column(comment_parent_type_enum, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    @classmethod
    def find_by_type_and_parent_id(cls, parent_type, parent_id):
        return cls.query.filter(
            and_(
                cls.parent_type == parent_type,
                cls.parent_id == str(parent_id),
                cls.deleted_at == None,  # noqa: E711
            ),
        ).first()

    @classmethod
    def find_or_create(cls, parent_type, parent_id):
        parent = cls.find_by_type_and_parent_id(parent_type=parent_type, parent_id=parent_id)
        if parent:
            return parent
        parent = CommentParent(
            parent_id=str(parent_id),
            parent_type=parent_type,
        )
        db.session.add(parent)
        std_commit()
        db.session.refresh(parent)
        return parent
