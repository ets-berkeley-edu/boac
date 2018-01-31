import re
from flask import current_app as app


"""A utility module collecting logic specific to the Berkeley campus."""


def current_term_id():
    term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
    return sis_term_id_for_name(term_name)


def sis_term_id_for_name(term_name=None):
    if term_name:
        match = re.match(r'\A(Spring|Summer|Fall) 20(\d{2})\Z', term_name)
        if match:
            season_codes = {
                'Spring': '2',
                'Summer': '5',
                'Fall': '8',
            }
            return '2' + match.group(2) + season_codes[match.group(1)]


def term_name_for_sis_id(sis_id=None):
    if sis_id:
        sis_id = str(sis_id)
        season_codes = {
            '2': 'Spring',
            '5': 'Summer',
            '8': 'Fall',
        }
        return season_codes[sis_id[3:4]] + ' 20' + sis_id[1:3]
