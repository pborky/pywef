__author__="pborky"
__date__ ="$19.2.2010 0:21:07$"

import sys
from wsgi.controller import FrontControllerFactory
from wsgi.monitor import Monitor

Monitor().start()

class MyApp(object):
    def __call__(self, context):
        context.response.status = 200
        context.response.headers['Content-Type'] = 'text/plain'
        context.response.body_file.write('Hello world!\nHere be dragon soon.')

application = FrontControllerFactory.produce(MyApp())
