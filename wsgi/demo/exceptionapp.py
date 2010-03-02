__author__="peterb"
__date__ ="$1.3.2010 15:13:43$"

from wsgi.errorhandler import ExcInfo
from webob.exc import HTTPMovedPermanently

class MyException(Exception):
    pass

class ExcApp(object):
    """ Demo application showing handling of exceptions and traceback.."""

    def __call__(self, context, **kwargs):
        if 'move' in kwargs:
            loc = '/'+kwargs['move']
            raise HTTPMovedPermanently('Redirecting to "%s".' % loc, location = loc)
        try:
            raise MyException('Hello world! This is an example exception.')
            context.response.status = 200
            context.response.header.append(('Content-Type', 'text/plain'))
            context.response.body.append('Hello world!')
        except:
            raise Exception('Oh! Somethig gone wrong.', ExcInfo())
