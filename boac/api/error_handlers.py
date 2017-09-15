import boac.api.errors
from flask import current_app as app, jsonify


@app.errorhandler(boac.api.errors.BadRequestError)
def handle_bad_request(error):
    return error.to_json(), 400


@app.errorhandler(boac.api.errors.UnauthorizedRequestError)
def handle_unauthorized(error):
    return error.to_json(), 401


@app.errorhandler(boac.api.errors.ForbiddenRequestError)
def handle_forbidden(error):
    return error.to_json(), 403


@app.errorhandler(boac.api.errors.ResourceNotFoundError)
def handle_resource_not_found(error):
    return error.to_json(), 404


@app.errorhandler(boac.api.errors.InternalServerError)
def handle_internal_server_error(error):
    return error.to_json(), 500


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception(error)
    return jsonify({'message': 'An unexpected server error occurred.'}), 500
