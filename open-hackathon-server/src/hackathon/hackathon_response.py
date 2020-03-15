# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from hackathon.log import log


class HTTP_CODE:
    CREATE_NOT_FINISHED = 412101
    OBSOLETE = 412102


__all__ = [
    "bad_request",
    "unauthorized",
    "forbidden",
    "not_found",
    "conflict",
    "precondition_failed",
    "unsupported_mediatype",
    "internal_server_error",
    "ok",
    "HTTP_CODE",
]


#
# Common hackathon response with status code 200 and the real status code and message in body
#

def __response_with_code(code, message, friendly_message=""):
    log.debug("response with code: %d and message: %s" % (code, message))
    return {
        "error": {
            "code": code,
            "message": message,
            "friendly_message": friendly_message
        }
    }


def general_error(code,
                  message="",
                  friendly_message=(
                          'An unexpected error encountered'
                  )):
    return __response_with_code(code, message, friendly_message)


def bad_request(message="",
                friendly_message=(
                        'The browser (or proxy) sent a request that this server could '
                        'not understand.'
                )):
    return __response_with_code(400, message, friendly_message)


def unauthorized(message="",
                 friendly_message=(
                         'The server could not verify that you are authorized to access '
                         'the URL requested.  You either supplied the wrong credentials (e.g. '
                         'a bad password), or your browser doesn\'t understand how to supply '
                         'the credentials required.')):
    return __response_with_code(401, message, friendly_message)


def forbidden(message="",
              friendly_message=(
                      'You don\'t have the permission to access the requested resource. '
                      'It is either read-protected or not readable by the server.')):
    return __response_with_code(403, message, friendly_message)


def not_found(message="",
              friendly_message=(
                      'The requested URL was not found on the server.  '
                      'If you entered the URL manually please check your spelling and '
                      'try again.')):
    return __response_with_code(404, message, friendly_message)


def conflict(message="",
             friendly_message=(
                     'A conflict happened while processing the request.  The resource '
                     'might have been modified while the request was being processed.'
             )):
    return __response_with_code(409, message, friendly_message)


def precondition_failed(message="",
                        friendly_message=(
                                'The precondition on the request for the URL failed positive '
                                'evaluation.'
                        )):
    return __response_with_code(412, message, friendly_message)


def unsupported_mediatype(message="",
                          friendly_message=(
                                  'The server does not support the media type transmitted in '
                                  'the request.'
                          )):
    return __response_with_code(415, message, friendly_message)


def login_provider_error(message="",
                         friendly_message=(
                                 'Current hackathon must be logged in to use a specific way.'
                         ), provides=""):
    return {
        "error": {
            "code": 420,
            "message": message,
            "friendly_message": friendly_message,
            "provides": provides
        }
    }


def internal_server_error(message="",
                          friendly_message=(
                                  'The server encountered an internal error and was unable to '
                                  'complete your request.  Either the server is overloaded or there '
                                  'is an error in the application.'
                          )):
    return __response_with_code(500, message, friendly_message)


def ok(message=""):
    return {
        "code": 200,
        "message": message
    }

