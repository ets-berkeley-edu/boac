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

from boac.merged import sis_terms
from tests.util import override_config


class TestSisTerms:

    def test_get_current_term_index(self):
        """Gets the current and future terms."""
        index = sis_terms.get_current_term_index()
        assert index['current_term_name'] == 'Fall 2017'
        assert index['future_term_name'] == 'Spring 2018'

    def test_all_term_ids(self):
        """Returns SIS IDs of each term covered by BOAC, from current to oldest."""
        assert sis_terms.all_term_ids() == ['2178', '2175', '2172', '2168']

    def test_current_term_id(self):
        """Returns the current term ID."""
        assert sis_terms.current_term_id() == '2178'

    def test_current_term_id_caching(self):
        """Fetches current term ID from the loch instead of cache when asked."""
        import json
        from boac.models import json_cache
        from boac.models.json_cache import JsonCache

        index_row = JsonCache.query.filter_by(key='current_term_index').first()
        index_row.json = json.loads('{"current_term_name": "Spring 2020"}')
        json_cache.update_jsonb_row(index_row)

        assert sis_terms.current_term_id() == '2202'
        assert sis_terms.current_term_id(use_cache=False) == '2178'

    def test_current_term_id_from_config(self, app):
        """Falls back on configured current term ID when not set to auto."""
        with override_config(app, 'CANVAS_CURRENT_ENROLLMENT_TERM', 'Summer 1969'):
            assert sis_terms.current_term_id() == '1695'

    def test_current_term_name(self):
        """Returns the current term name."""
        assert sis_terms.current_term_name() == 'Fall 2017'

    def test_current_term_name_from_config(self, app):
        """Falls back on configured current term name when not set to auto."""
        with override_config(app, 'CANVAS_CURRENT_ENROLLMENT_TERM', 'Summer 1969'):
            assert sis_terms.current_term_name() == 'Summer 1969'

    def test_future_term_id(self):
        """Returns the future term id."""
        assert sis_terms.future_term_id() == '2182'

    def test_future_term_id_from_config(self, app):
        """Falls back on configured future term ID when not set to auto."""
        with override_config(app, 'CANVAS_FUTURE_ENROLLMENT_TERM', 'Summer 1969'):
            assert sis_terms.future_term_id() == '1695'
