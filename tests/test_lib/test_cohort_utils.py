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

from boac.lib.cohort_utils import grading_terms
from tests.util import override_config


class TestGradingTerms:
    """EPN/CPN Grading Option cohort filter options."""

    def test_two_terms(self, app):
        """Contains two items when current and future terms are consecutive."""
        with override_config(app, 'CANVAS_CURRENT_ENROLLMENT_TERM', 'Summer 2021'), \
                override_config(app, 'CANVAS_FUTURE_ENROLLMENT_TERM', 'Fall 2021'):
            options = grading_terms()
            assert options == [
                {'name': 'Summer 2021 (active)', 'value': '2215'},
                {'name': 'Fall 2021 (future)', 'value': '2218'},
            ]

    def test_three_terms(self, app):
        """Contains three items when a term exists between the current and future terms."""
        with override_config(app, 'CANVAS_CURRENT_ENROLLMENT_TERM', 'Spring 2021'), \
                override_config(app, 'CANVAS_FUTURE_ENROLLMENT_TERM', 'Fall 2021'):
            options = grading_terms()
            assert options == [
                {'name': 'Spring 2021 (active)', 'value': '2212'},
                {'name': 'Summer 2021 (future)', 'value': '2215'},
                {'name': 'Fall 2021 (future)', 'value': '2218'},
            ]
