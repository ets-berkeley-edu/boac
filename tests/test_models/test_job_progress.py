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


from datetime import date

from boac.models.job_progress import JobProgress
import pytest


@pytest.mark.usefixtures('db_session')
class TestJobProgress:
    """Background job process tracker."""

    def test_start_and_end(self):
        assert JobProgress().get() is None
        progress = JobProgress().start()
        assert progress['start'].startswith(str(date.today()))
        assert progress['end'] is None
        progress = JobProgress().end()
        assert progress['end'].startswith(str(date.today()))

    def test_does_not_update_an_unstarted_job(self):
        assert JobProgress().get() is None
        progress = JobProgress().update('False step')
        assert progress is False

    def test_updates_a_started_job(self):
        assert JobProgress().start()
        progress = JobProgress().update('First step')
        assert len(progress['steps']) == 1
        assert progress['steps'][0].startswith(str(date.today()))
        assert progress['steps'][0].endswith('First step')
        progress = JobProgress().update('Next step')
        assert len(progress['steps']) == 2
        assert progress['steps'][1].endswith('Next step')

    def test_does_not_update_an_ended_job(self):
        assert JobProgress().start()
        assert JobProgress().end()
        progress = JobProgress().update('Into the wall')
        assert progress is False

    def test_delete_job(self):
        assert JobProgress().start()
        assert JobProgress().start() is False
        assert JobProgress().delete()
        assert JobProgress().start()

    def test_multiple_job_names(self):
        assert JobProgress('alphonse').start()
        assert JobProgress('alphonse').start() is False
        assert JobProgress('gaston').start()
        assert JobProgress('alphonse').delete()
        assert JobProgress('gaston').start() is False

    def test_start_with_stored_properties(self):
        assert JobProgress().get() is None
        JobProgress().start({'term_id': '2178'})
        progress = JobProgress().get()
        assert progress['start'].startswith(str(date.today()))
        assert progress['term_id'] == '2178'
