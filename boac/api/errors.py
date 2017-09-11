from flask import current_app as app
from flask import jsonify


class JsonableException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def to_json(self):
        if self.message:
            return jsonify({'message': self.message})
        else:
            return ''


class BadRequestError(JsonableException):
    pass


class UnauthorizedRequestError(JsonableException):
    pass


class ForbiddenRequestError(JsonableException):
    pass


class ResourceNotFoundError(JsonableException):
    pass


@app.errorhandler(BadRequestError)
def handle_bad_request(error):
    return error.to_json(), 400


@app.errorhandler(UnauthorizedRequestError)
def handle_unauthorized(error):
    return error.to_json(), 401


@app.errorhandler(ForbiddenRequestError)
def handle_forbidden(error):
    return error.to_json(), 403


@app.errorhandler(ResourceNotFoundError)
def handle_resource_not_found(error):
    return error.to_json(), 404


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception(error)
    return jsonify({'message': 'An unexpected server error occurred.'}), 500
