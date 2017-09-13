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

app = create_app()


@app.cli.command()
def initdb():
    from boac.models import development_db
    development_db.load()


if __name__ == '__main__':
    app.logger.info('BOAC server running on http://%s:%s !', app.config['HOST'], app.config['PORT'])
    app.run(host=app.config['HOST'], port=app.config['PORT'])
