from flask import current_app as app
from sqlalchemy import create_engine
from sqlalchemy.sql import text

data_loch_db = create_engine(app.config['DATA_LOCH_URI'])


def execute(string):
    s = text(string)
    return data_loch_db.execute(s)
