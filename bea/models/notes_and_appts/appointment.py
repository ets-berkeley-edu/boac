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

from bea.models.notes_and_appts.timeline_note_appt import TimelineNoteAppt


class Appointment(TimelineNoteAppt):

    @property
    def cancel_detail(self):
        return self.data['cancel_detail']

    @cancel_detail.setter
    def cancel_detail(self, value):
        self.data['cancel_detail'] = value

    @property
    def cancel_reason(self):
        return self.data['cancel_reason']

    @cancel_reason.setter
    def cancel_reason(self, value):
        self.data['cancel_reason'] = value

    @property
    def detail(self):
        return self.data['detail']

    @detail.setter
    def detail(self, value):
        self.data['detail'] = value

    @property
    def end_time(self):
        return self.data['end_time']

    @end_time.setter
    def end_time(self, value):
        self.data['end_time'] = value

    @property
    def start_time(self):
        return self.data['start_time']

    @start_time.setter
    def start_time(self, value):
        self.data['start_time'] = value

    @property
    def status(self):
        return self.data['status']

    @status.setter
    def status(self, value):
        self.data['status'] = value

    @property
    def status_date(self):
        return self.data['status_date']

    @status_date.setter
    def status_date(self, value):
        self.data['status_date'] = value
