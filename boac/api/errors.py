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


class InternalServerError(JsonableException):
    pass
