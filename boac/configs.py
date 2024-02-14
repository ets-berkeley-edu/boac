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


import importlib.util
import os


def load_configs(app):
    """On app creation, load and and override configs.

    Order:
     - config/default.py
     - config/{BOAC_ENV}.py
     - {BOAC_LOCAL_CONFIGS}/{BOAC_ENV}-local.py (excluded from version control; sensitive values go here)
    """
    load_module_config(app, 'default')
    # BOAC_ENV defaults to 'development'.
    app_env = os.environ.get('BOAC_ENV', 'development')
    load_module_config(app, app_env)
    load_local_config(app, f'{app_env}-local.py')
    app.config['BOAC_ENV'] = app_env


def load_module_config(app, config_name):
    """Load an individual module-hosted configuration file if it exists."""
    config_path = f'config.{config_name}'
    if importlib.util.find_spec(config_path) is not None:
        app.config.from_object(config_path)


def load_local_config(app, config_name):
    """Load the local configuration file (if any) from a location outside the package."""
    configs_location = os.environ.get('BOAC_LOCAL_CONFIGS') or '../config'
    config_path = configs_location + '/' + config_name
    app.config.from_pyfile(config_path, silent=True)
