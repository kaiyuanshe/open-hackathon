# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")
from functools import wraps
from werkzeug.exceptions import BadRequest, InternalServerError
from dateutil import parser

from flask_restful import Resource
from flask import request
import validictory

from hackathon.views.api_schema import schemas
from hackathon import RequiredFeature, Context

__all__ = ["Resource", "HackathonResource"]

log = RequiredFeature("log")


def get_input_schema(class_name, method_name):
    return __get_schema(class_name, method_name, "input")


def get_output_schema(class_name, method_name):
    return __get_schema(class_name, method_name, "output")


def __get_schema(class_name, method_name, t):
    if class_name in schemas:
        cls = schemas[class_name]
        if method_name in cls:
            return cls[method_name].get(t)

    return None


def validate_date(validator, fieldname, value, format_option):
    if format_option == "hack_date":
        try:
            parser.parse(value)
        except Exception as e:
            raise validictory.FieldValidationError(
                "Could not parse date from string %s, reason: %s" % (value, e), fieldname, value)
    else:
        raise validictory.FieldValidationError("Invalid format option for \
        'validate_uuid': %(format)s" % format_option, fieldname, value)


def validate(func):
    """A decorator for RestFul APIs that enables parameter validation"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        class_name = func.__self__.__class__.__name__
        method_name = func.__name__.lower()
        if hasattr(func, "original"):
            method_name = func.original

        input_schema = get_input_schema(class_name, method_name)
        output_schema = get_output_schema(class_name, method_name)

        if input_schema:
            if method_name in ["post", "put"] and not request.path == "/api/user/file":
                data = request.get_json(force=True)
            else:
                data = request.args

            try:
                formatdict = {
                    "hack_date": validate_date
                }
                validictory.validate(data, input_schema, format_validators=formatdict, fail_fast=False)
                log.debug("input validated for %s.%s" % (class_name, method_name))
            except validictory.MultipleValidationError as me:
                log.debug("input validation of '%s.%s' failed: %s" % (class_name, method_name, repr(me.errors)))
                raise BadRequest(repr(me.errors))

        output_data = func(*args, **kwargs)
        if output_schema:
            # if it's kind of `error` defined in hackathon_response.py, skip the validation
            if isinstance(output_data, dict) and "error" in output_data:
                return output_data

            try:
                validictory.validate(output_data, output_schema, fail_fast=False)
                log.debug("output validated for %s.%s" % (class_name, method_name))
            except validictory.MultipleValidationError as me:
                log.debug("output validation of '%s.%s' failed: %s" % (class_name, method_name, repr(me.errors)))
                raise InternalServerError(repr(me.errors))

        code = "200"
        if output_data is not None and isinstance(output_data, dict) and "error" in output_data:
            code = output_data["error"]["code"]
        log.debug("API call %s.%s -- %s %d" % (class_name, method_name, code, len(str(output_data))))
        return output_data

    return wrapper


class HackathonResource(Resource):
    """Inheritance of Resource which provides custom input/output validation"""
    method_decorators = [validate]

    def context(self):
        """Convert input to Context

        By default, convert json body to Convext for put/post request, convert args for get/delete request

        :rtype: Context
        :return Context object from request body or query
        """
        caller = sys._getframe().f_back.f_code.co_name.lower()
        if caller in ["post", "put"] and not request.path == "/api/user/file":
            return Context.from_object(request.get_json(force=True))
        else:
            return Context.from_object(request.args)
