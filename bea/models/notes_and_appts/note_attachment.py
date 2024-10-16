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


class NoteAttachment(object):

    def __init__(self, data):
        self.data = data

    @property
    def attachment_id(self):
        return self.data.get('attachment_id')

    @attachment_id.setter
    def attachment_id(self, value):
        self.data['attachment_id'] = value

    @property
    def deleted_at(self):
        return self.data.get('deleted_at')

    @deleted_at.setter
    def deleted_at(self, value):
        self.data['deleted_at'] = value

    @property
    def file_name(self):
        return self.data.get('file_name')

    @file_name.setter
    def file_name(self, value):
        self.data['file_name'] = value

    @property
    def file_size(self):
        return self.data.get('file_size')

    @file_size.setter
    def file_size(self, value):
        self.data['file_size'] = value

    @property
    def sis_file_name(self):
        return self.data.get('sis_file_name')

    @sis_file_name.setter
    def sis_file_name(self, value):
        self.data['sis_file_name'] = value
