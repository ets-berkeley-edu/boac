"""BOAC takes good care of you.

Usage mode A:

>>> python run.py

Usage mode B:

>>> export FLASK_APP=run.py
>>> flask run --help
>>> flask run --debugger
>>> flask initdb
"""

from boac.factory import create_app

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
