from boac import db


def initialize_db(app):
    db.init_app(app)
    return db
