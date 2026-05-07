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

from sqlalchemy.dialects.postgresql import ARRAY

from boac import db
from boac.models.base import Base


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
