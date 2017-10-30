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
if os.environ.get('HOME') == '/home/wsgi':
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


if __name__ == '__main__':
    host = application.config['HOST']
    port = application.config['PORT']

    application.logger.info('BOAC server running on http://%s:%s !', host, port)
    application.run(host=host, port=port)
