"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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


class TimelineRecord(object):

    def __init__(self, data, attachments=None, topics=None):
        self.data = data
        self.attachments = attachments or []
        self.topics = topics or []

    @property
    def record_id(self):
        return self.data.get('record_id')

    @record_id.setter
    def record_id(self, value):
        self.data['record_id'] = value

    @property
    def body(self):
        return self.data.get('body')

    @body.setter
    def body(self, value):
        self.data['body'] = value

    @property
    def created_date(self):
        return self.data.get('created_date')

    @created_date.setter
    def created_date(self, value):
        self.data['created_date'] = value

    @property
    def deleted_date(self):
        return self.data.get('deleted_date')

    @deleted_date.setter
    def deleted_date(self, value):
        self.data['deleted_date'] = value

    @property
    def source(self):
        return self.data.get('source')

    @source.setter
    def source(self, value):
        self.data['source'] = value

    @property
    def student(self):
        return self.data.get('student')

    @student.setter
    def student(self, value):
        self.data['student'] = value

    @property
    def subject(self):
        return self.data.get('subject')

    @subject.setter
    def subject(self, value):
        self.data['subject'] = value

    @property
    def title(self):
        return self.data.get('title')

    @title.setter
    def title(self, value):
        self.data['title'] = value

    @property
    def updated_date(self):
        return self.data.get('updated_date')

    @updated_date.setter
    def updated_date(self, value):
        self.data['updated_date'] = value
