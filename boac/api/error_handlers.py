"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from flask import current_app as app
from flask import jsonify
from flask_wtf.csrf import CSRFError

import boac.api.errors


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    # A BadRequest subclass; without this handler it would fall through to the catch-all Exception handler
    # below and get misreported as a 500 "unexpected server error" instead of an actionable 400.
    app.logger.warning(f'CSRF validation failed: {error.description}')
    return jsonify(
        error_class='CSRFError',
        message='Your session security token is missing or has expired. Please refresh the page and try again.',
        success=False,
    ), 400


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
    return jsonify(
        error_class=str(type(error)) if error else None,
        message='An unexpected server error occurred.',
        success=False,
    ), 500
