import logging
from logging.handlers import RotatingFileHandler


def initialize_logger(app):
    # If location is configured as "STDOUT", don't create a new log file.
    location = app.config['LOGGING_LOCATION']
    if (location == 'STDOUT'):
        handlers = app.logger.handlers
    else:
        file_handler = RotatingFileHandler(location, mode='a', maxBytes=1024 * 1024 * 100, backupCount=20)
        handlers = [file_handler]
        app.logger.addHandler(file_handler)
    for handler in handlers:
        handler.setLevel(app.config['LOGGING_LEVEL'])
        formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
        handler.setFormatter(formatter)
