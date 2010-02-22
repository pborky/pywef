__author__="pborky"
__date__ ="$19.2.2010 0:21:07$"

import sys
from wsgi.controller import FrontControllerFactory
from wsgi.monitor import Monitor

Monitor().start()

class MyException(Exception):
    pass

class MyApp(object):
    def __call__(self, context):
        try:
            raise MyException('Hello world! This is an example exception.')
            context.response.status = 200
            context.response.header.append(('Content-Type', 'text/plain'))
            context.response.body.append('Hello world!')
        except:
            raise Exception('Oh! Somethig gone wrong.', sys.exc_info())


application = FrontControllerFactory.produce(MyApp())
