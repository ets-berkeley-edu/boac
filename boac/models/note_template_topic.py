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
from sqlalchemy import and_


class NoteTemplateTopic(db.Model):
    __tablename__ = 'note_template_topics'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    note_template_id = db.Column(db.Integer, db.ForeignKey('note_templates.id'), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    note_template = db.relationship('NoteTemplate', back_populates='topics')

    def __init__(self, note_template_id, topic):
        self.note_template_id = note_template_id
        self.topic = topic

    @classmethod
    def create(cls, note_template_id, topic):
        return cls(note_template_id=note_template_id, topic=topic)

    @classmethod
    def find_by_note_template_id(cls, note_template_id):
        return cls.query.filter(and_(cls.note_template_id == note_template_id)).all()

    @classmethod
    def delete(cls, topic_id):
        topic = cls.query.filter_by(id=topic_id).first()
        db.session.delete(topic)
        std_commit()

    def to_api_json(self):
        return self.topic
