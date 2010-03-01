__author__="peterb"
__date__ ="$1.3.2010 15:13:43$"

import sys
from wsgi.errorhandler import ExcInfo

class MyException(Exception):
    pass

class ExcApp(object):
    """ Demo application showing handling of exceptions and traceback.."""

    def __call__(self, context, **kwargs):
        try:
            raise MyException('Hello world! This is an example exception.')
            context.response.status = 200
            context.response.header.append(('Content-Type', 'text/plain'))
            context.response.body.append('Hello world!')
        except:
            raise Exception('Oh! Somethig gone wrong.', ExcInfo())