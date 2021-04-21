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
from boac.models.base import Base
from dateutil.tz import tzutc


class DegreeProgressNote(Base):
    __tablename__ = 'degree_progress_notes'

    body = db.Column(db.Text, nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('degree_progress_templates.id'), nullable=False, primary_key=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)

    template = db.relationship('DegreeProgressTemplate', back_populates='note')

    def __init__(self, body, template_id, updated_by):
        self.body = body
        self.template_id = template_id
        self.updated_by = updated_by

    def __repr__(self):
        return f"""<DegreeProgressTemplate template_id={self.template_id},
                    body={self.body},
                    created_at={self.created_at},
                    updated_at={self.updated_at},
                    updated_by={self.updated_by}>"""

    @classmethod
    def upsert(
            cls,
            body,
            template_id,
            updated_by,
    ):
        note = cls.query.filter_by(template_id=template_id).first()
        if note:
            note.body = body
            note.updated_by = updated_by
        else:
            note = cls(
                body=body,
                template_id=template_id,
                updated_by=updated_by,
            )
            db.session.add(note)
        std_commit()
        return note

    def to_api_json(self):
        return {
            'body': self.body,
            'createdAt': _isoformat(self.created_at),
            'templateId': self.template_id,
            'updatedAt': _isoformat(self.updated_at),
            'updatedBy': self.updated_by,
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
