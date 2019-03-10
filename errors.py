#!/usr/bin/python2.7
from flask import jsonify


class InvalidRequest(Exception):
    status_code = 400

    def __init__(self, message, **kwargs):
        Exception.__init__(self)
        self.kwargs = dict(kwargs or ())
        self.kwargs['error'] = message

    def to_dict(self):
        return self.kwargs

class UnknownValue(Exception):
    status_code = 400

    def __init__(self,message):
        Exception.__init__(self)
        self.message = message
    def to_dict(self):
        return {'error':message}
