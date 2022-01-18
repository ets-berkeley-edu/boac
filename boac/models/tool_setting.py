"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.lib.util import camelize
from boac.models.base import Base


class ToolSetting(Base):
    __tablename__ = 'tool_settings'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    key = db.Column(db.String(255), nullable=False, unique=True)
    value = db.Column(db.String(255), nullable=False)

    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'<ToolSettings {self.key}, value={self.value}>'

    @classmethod
    def get_tool_setting(cls, key):
        setting = cls.query.filter(cls.key == key).first()
        return setting and setting.value

    @classmethod
    def upsert(cls, key, value):
        tool_setting = cls.query.filter_by(key=key).first()
        if tool_setting:
            tool_setting.value = str(value)
        else:
            tool_setting = cls(key=key, value=str(value))
            db.session.add(tool_setting)
        std_commit()
        return tool_setting

    def to_api_json(self):
        return {camelize(self.key): self.value}
