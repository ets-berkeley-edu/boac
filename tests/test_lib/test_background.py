"""
Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.

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

import sched
from unittest import mock

from boac.lib import background


class TestScheduledExecution:
    """Background scheduler loop."""

    def test_runs_method_and_schedules_next_iteration(self, app):
        scheduler = sched.scheduler()
        method = mock.Mock()
        with mock.patch.dict(app.config, {'BACKGROUND_TASKS': True}):
            background.execute_scheduled(method, scheduler, app)
        method.assert_called_once_with()
        assert len(scheduler.queue) == 1

    def test_failing_method_does_not_stop_the_loop(self, app):
        scheduler = sched.scheduler()
        method = mock.Mock(side_effect=RuntimeError('Task failed'))
        with mock.patch.dict(app.config, {'BACKGROUND_TASKS': True}):
            background.execute_scheduled(method, scheduler, app)
        method.assert_called_once_with()
        assert len(scheduler.queue) == 1

    def test_does_nothing_when_background_tasks_are_disabled(self, app):
        scheduler = sched.scheduler()
        method = mock.Mock()
        assert app.config['BACKGROUND_TASKS'] is False
        background.execute_scheduled(method, scheduler, app)
        method.assert_not_called()
        assert len(scheduler.queue) == 0

    def test_loop_does_not_start_without_tasks_or_when_disabled(self, app):
        with mock.patch.object(background, 'Thread') as thread, mock.patch.object(background, 'scheduled_methods', return_value=[mock.Mock()]):
            # Disabled in the test config, even with a task registered.
            background.initialize_scheduler_loop(app)
            thread.assert_not_called()
            with mock.patch.dict(app.config, {'BACKGROUND_TASKS': True}):
                background.initialize_scheduler_loop(app)
                thread.assert_called_once()
        with mock.patch.object(background, 'Thread') as thread, mock.patch.dict(app.config, {'BACKGROUND_TASKS': True}):
            # No tasks registered yet, so no idle thread.
            background.initialize_scheduler_loop(app)
            thread.assert_not_called()
