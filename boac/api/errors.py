from boac.lib.http import tolerant_jsonify


class JsonableException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def to_json(self):
        if self.message:
            return tolerant_jsonify({'message': self.message})
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
