# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 
The MIT License (MIT)
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from log import log


def __response_with_code(code, message, friendly_message=""):
    # todo log the stack trace or request information later
    log.debug("response with code: %d and message: %s" % (code, message))
    return {
        "error": {
            "code": code,
            "message": message,
            "friendly_message": friendly_message
        }
    }


def not_found(message, friendly_message="Not Found"):
    return __response_with_code(404, message, friendly_message)


def bad_request(message, friendly_message="Bad Request"):
    return __response_with_code(400, message, friendly_message)


def unauthorized(message, friendly_message="UnAuthorized"):
    return __response_with_code(401, message, friendly_message)


def access_denied(message, friendly_message="Access Denied"):
    return __response_with_code(403, message, friendly_message)


def internal_server_error(message, friendly_message="Internal Server Error"):
    return __response_with_code(500, message, friendly_message)


def ok(message=""):
    return {
        "code": 200,
        "message": message
    }
