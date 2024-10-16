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

from enum import Enum


class TimelineRecordSource(Enum):

    ASC = {
        'name': 'ASC',
        'schema': 'boac_advising_asc',
    }
    BOA = {
        'name': 'BOA',
        'schema': None,
    }
    DATA = {
        'name': 'Data Science',
        'schema': 'boac_advising_data_science',
    }
    E_AND_I = {
        'name': 'CE3',
        'schema': 'boac_advising_e_i',
    }
    E_FORM = {
        'name': 'eForm',
        'schema': 'sis_advising_notes',
    }
    EOP = {
        'name': 'EOP',
        'schema': 'boac_advising_eop',
    }
    HISTORY = {
        'name': 'History Dept',
        'schema': 'boac_advising_history_dept',
    }
    SIS = {
        'name': 'SIS',
        'schema': 'sis_advising_notes',
    }
    YCBM = {
        'name': 'YouCanBookMe',
        'schema': 'ycbm_advising_appointments',
    }
