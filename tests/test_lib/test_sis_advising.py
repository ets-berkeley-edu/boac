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

from boac.lib.sis_advising import get_legacy_attachment_stream
from tests.util import mock_legacy_appointment_attachment, mock_sis_note_attachment


coe_advisor = '1133399'


class TestGetLegacyAttachmentStream:
    """Streams legacy note and appointment attachment files from S3."""

    def test_stream_appointment_attachment(self, app, fake_auth):
        with mock_legacy_appointment_attachment(app):
            fake_auth.login(coe_advisor)
            stream = get_legacy_attachment_stream('9100000000_00010_1.pdf')['stream']
            body = b''
            for chunk in stream:
                body += chunk
            assert body == b'01001000 01100101 01101100 01101100 01101111 00100000 01010111 01101111 01110010 01101100 01100100'

    def test_stream_note_attachment(self, app, fake_auth):
        with mock_sis_note_attachment(app):
            fake_auth.login(coe_advisor)
            stream = get_legacy_attachment_stream('9000000000_00002_1.pdf')['stream']
            body = b''
            for chunk in stream:
                body += chunk
            assert body == b'When in the course of human events, it becomes necessarf arf woof woof woof'

    def test_stream_attachment_handles_malformed_filename(self, app):
        with mock_sis_note_attachment(app):
            assert get_legacy_attachment_stream('h0ax.lol') is None

    def test_stream_attachment_handles_file_not_in_database(self, app, fake_auth, caplog):
        with mock_sis_note_attachment(app):
            fake_auth.login(coe_advisor)
            assert get_legacy_attachment_stream('11667051_00002_1.pdf') is None

    def test_stream_attachment_handles_file_not_in_s3(self, app, fake_auth, caplog):
        with mock_sis_note_attachment(app):
            fake_auth.login(coe_advisor)
            assert get_legacy_attachment_stream('11667051_00001_1.pdf')['stream'] is None
            assert "the s3 key 'sis-attachment-path/11667051/11667051_00001_1.pdf' does not exist, or is forbidden" in caplog.text
