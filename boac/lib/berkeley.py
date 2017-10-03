import re


"""A utility module collecting logic specific to the Berkeley campus."""


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
