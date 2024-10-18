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

import csv
import glob
import json
import math
import os
import re
import shutil
import time

from bea.models.term import Term
from flask import current_app as app


# Driver config

def get_browser():
    return app.config['BROWSER']


def get_browser_chrome_binary_path():
    return app.config['BROWSER_BINARY_PATH']


def browser_is_headless():
    return app.config['BROWSER_HEADLESS']


# Timeouts

def get_click_sleep():
    return app.config['CLICK_SLEEP']


def get_short_timeout():
    return app.config['TIMEOUT_SHORT']


def get_medium_timeout():
    return app.config['TIMEOUT_MEDIUM']


def get_long_timeout():
    return app.config['TIMEOUT_LONG']


# Users

def get_admin_uid():
    return app.config['ADMIN_UID']


def get_admin_username():
    return os.getenv('USERNAME')


def get_admin_password():
    return os.getenv('PASSWORD')


# Test configs and utils

def get_test_identifier():
    return f'QA TEST {int(time.time())}'


def parse_test_data():
    with open(app.config['TEST_DATA']) as f:
        return json.load(f)


def attachments_dir():
    return f'{app.config["BASE_DIR"]}/bea/assets'


def default_download_dir():
    return f'{app.config["BASE_DIR"]}/bea/downloads'


def prepare_download_dir():
    # Make sure a clean download directory exists
    if os.path.isdir(default_download_dir()):
        shutil.rmtree(default_download_dir())
    os.mkdir(default_download_dir())


def is_download_dir_empty():
    return False if os.listdir(default_download_dir()) else True


def wait_for_export(file_ext):
    tries = 0
    max_tries = get_medium_timeout()
    while tries <= max_tries:
        tries += 1
        try:
            assert len(glob.glob(f'{default_download_dir()}/*.{file_ext}')) == 1
            break
        except AssertionError:
            if tries == max_tries:
                raise
            else:
                time.sleep(1)
    return glob.glob(f'{default_download_dir()}/*.{file_ext}')[0]


def wait_for_export_csv():
    file = wait_for_export('csv')
    return csv.DictReader(open(file))


def wait_for_export_zip():
    return wait_for_export('zip')


def assert_equivalence(actual, expected):
    if actual != expected:
        app.logger.info(f'Expecting {expected}, got {actual}')
    assert actual == expected


def assert_actual_includes_expected(actual, expected):
    if expected not in actual:
        app.logger.info(f'Expected {actual} to include {expected}')
    assert expected in actual


def assert_existence(actual):
    app.logger.info(f'Expecting {actual} not to be null or empty')
    assert actual


def assert_non_existence(actual):
    app.logger.info(f'Expecting {actual} to be null or empty')
    assert not actual


def strip_tags_and_whitespace(string):
    string = re.sub(re.compile('<.*?>'), '', string)
    return re.sub(r'\s+', ' ', string)


def date_to_local_tz(date):
    return date.astimezone()


def in_op(arr):
    arr = list(map(lambda i: f"'{i}'", arr))
    return ', '.join(arr)


def formatted_units(units_as_num):
    if units_as_num:
        if units_as_num == 0:
            return '0'
        else:
            if math.floor(units_as_num) == units_as_num:
                return f'{math.floor(units_as_num)}'
            else:
                return f"{float('{:.3f}'.format(units_as_num))}"


def safe_key(parsed, key):
    try:
        return parsed[key]
    except KeyError:
        return None


# Terms

def get_current_term():
    return Term({
        'code': app.config['TERM_CODE'],
        'name': app.config['TERM_NAME'],
        'sis_id': app.config['TERM_SIS_ID'],
    })


def get_previous_term(term=None):
    term = term or get_current_term()
    sis_id = get_prev_term_sis_id(term.sis_id)
    return Term({
        'code': get_previous_term_code(sis_id),
        'name': term_sis_id_to_term_name(sis_id),
        'sis_id': sis_id,
    })


def get_prev_term_sis_id(sis_id=None):
    current_sis_id = int(sis_id) if sis_id else int(app.config['TERM_SIS_ID'])
    previous_sis_id = current_sis_id - (4 if (current_sis_id % 10 == 2) else 3)
    return f'{previous_sis_id}'


def get_previous_term_code(term_sis_id):
    d1 = '2'
    d2_3 = str(int(term_sis_id[1:3]) - 1) if (term_sis_id[-1] == '2') else term_sis_id[1:3]
    if term_sis_id[3] == '8':
        d4 = '5'
    elif term_sis_id[3] == '5':
        d4 = '2'
    else:
        d4 = '8'
    return d1 + d2_3 + d4


def get_next_term(term=None):
    term = term or get_current_term()
    sis_id = get_next_term_sis_id(term.sis_id)
    return Term({
        'code': get_next_term_code(sis_id),
        'name': term_sis_id_to_term_name(sis_id),
        'sis_id': sis_id,
    })


def get_next_term_sis_id(sis_id=None):
    current_sis_id = int(sis_id) if sis_id else int(app.config['TERM_SIS_ID'])
    next_sis_id = current_sis_id + (3 if (current_sis_id % 10 in [2, 5]) else 4)
    return f'{next_sis_id}'


def get_next_term_code(term_sis_id):
    d1 = '2'
    d2_3 = str(int(term_sis_id[1:3]) + 1) if (term_sis_id[-1] == '8') else term_sis_id[1:3]
    if term_sis_id[3] == '2':
        d4 = '5'
    elif term_sis_id[3] == '5':
        d4 = '8'
    else:
        d4 = '2'
    return d1 + d2_3 + d4


def term_sis_id_to_term_name(term_sis_id):
    year = f'{term_sis_id[0]}0{term_sis_id[1]}{term_sis_id[2]}'
    if term_sis_id[3] == '2':
        return f'Spring {year}'
    elif term_sis_id[3] == '5':
        return f'Summer {year}'
    else:
        return f'Fall {year}'
