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

from datetime import datetime

from sqlalchemy import and_, text

from boac import db, std_commit


class NoteRead(db.Model):
    __tablename__ = 'notes_read'

    viewer_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False, primary_key=True)
    note_id = db.Column(db.String(255), nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    __table_args__ = (db.UniqueConstraint(
        'viewer_id',
        'note_id',
        name='notes_read_viewer_id_note_id_unique_constraint',
    ),)

    def __init__(self, viewer_id, note_id):
        self.viewer_id = viewer_id
        self.note_id = note_id

    @classmethod
    def delete_for_note(cls, note_id, except_viewer_id=None):
        criteria = [
            cls.note_id == str(note_id),
        ]
        if except_viewer_id:
            criteria.append(cls.viewer_id != except_viewer_id)

        for row in cls.query.filter(and_(*criteria)).all():
            db.session.delete(row)
        std_commit()

    @classmethod
    def find_or_create(cls, viewer_id, note_ids):
        params = {
            'viewer_id': viewer_id,
        }
        values = []
        for index, note_id in enumerate(note_ids):
            values.append(f'(now(), :note_id_{index}, :viewer_id)')
            params[f'note_id_{index}'] = note_id

        sql = f"""INSERT INTO notes_read (created_at, note_id, viewer_id) VALUES
                  {', '.join(values)}
            ON CONFLICT DO NOTHING;"""
        db.session.execute(text(sql), params)
        std_commit()
        return cls.query.filter(NoteRead.viewer_id == viewer_id, NoteRead.note_id.in_([str(note_id) for note_id in note_ids])).all()

    @classmethod
    def get_notes_read_by_user(cls, viewer_id, note_ids):
        return cls.query.filter(NoteRead.viewer_id == viewer_id, NoteRead.note_id.in_([str(note_id) for note_id in note_ids])).all()

    @classmethod
    def when_user_read_note(cls, viewer_id, note_id):
        note_read = cls.query.filter(NoteRead.viewer_id == viewer_id, NoteRead.note_id == note_id).first()
        return note_read and note_read.created_at
