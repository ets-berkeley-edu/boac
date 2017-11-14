"""BOAC takes good care of you.

Usage mode A:

>>> python run.py

Usage mode B:

>>> export FLASK_APP=run.py
>>> flask run --help
>>> flask run --debugger
>>> flask initdb
"""

import os
import subprocess

from boac.factory import create_app

# When running under WSGI, system environment variables are not automatically made available to Python code, and
# an app restart will result in configurations being lost. We work around this with an explicit load from the shell
# environment, sourcing from the Elastic Beanstalk-provided /opt/python/current/env file if available.
if __name__.startswith('_mod_wsgi'):
    command = ['bash', '-c', '{ source /opt/python/current/env || true; } && env']
    shell_environment = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in shell_environment.stdout:
        key, _, value = line.decode('utf-8').rstrip().partition('=')
        os.environ[key] = value

application = create_app()


@application.cli.command()
def initdb():
    from boac.models import development_db
    development_db.load()


@application.cli.command()
def load_external_data():
    from boac.api import cache_utils
    cache_utils.load_current_term()


@application.cli.command()
def refresh_external_data():
    from boac.api import cache_utils
    cache_utils.refresh_current_term()


host = application.config['HOST']
port = application.config['PORT']

if __name__ == '__main__':
    application.logger.info('Starting development server on %s:%s', host, port)
    application.run(host=host, port=port)
elif __name__.startswith('_mod_wsgi'):
    application.logger.info('Will start WSGI server on %s:%s', host, port)
