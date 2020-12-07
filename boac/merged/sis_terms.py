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

from boac.externals import data_loch
from boac.lib.berkeley import previous_term_id, sis_term_id_for_name
from boac.models.json_cache import stow
from flask import current_app as app


@stow('current_term_index')
def get_current_term_index():
    return data_loch.get_current_term_index()


def current_term_id(use_cache=True):
    return sis_term_id_for_name(current_term_name(use_cache))


def current_term_name(use_cache=True):
    term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
    if term_name == 'auto':
        index = get_current_term_index() if use_cache else data_loch.get_current_term_index()
        return index and index['current_term_name']
    return term_name


def future_term_id():
    term_name = app.config['CANVAS_FUTURE_ENROLLMENT_TERM']
    if term_name == 'auto':
        index = get_current_term_index()
        return index and sis_term_id_for_name(index['future_term_name'])
    return sis_term_id_for_name(term_name)


def all_term_ids():
    """Return SIS IDs of each term covered by BOAC, from current to oldest."""
    earliest_term_id = sis_term_id_for_name(app.config['CANVAS_EARLIEST_TERM'])
    term_id = current_term_id()
    ids = []
    while int(term_id) >= int(earliest_term_id):
        ids.append(term_id)
        term_id = previous_term_id(term_id)
    return ids
