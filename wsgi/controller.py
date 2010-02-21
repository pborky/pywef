__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

# TODO: refactor this module

import sys


class AppNotInitializedProperly(Exception):
    pass

class FrontControllerFactory(object):
    _controller = None
    _init_exc_info = None
    
    @staticmethod
    def produce(app):
        if (controller == None):
            return _FrontControllerHandler(None, init_exc_info)
        else:
            controller.set_app(app)
            return _FrontControllerHandler(controller, None)


class _FrontControllerHandler(object):
    """ This is fail safe front controller. It returns 500 and error details"""
    # TODO: make confirable the error output
    def __init__(self, controller, init_exc_info):
        self._controller = controller
        self._init_exc_info = init_exc_info

    def __call__(self, environ, start_resp):
        try:
            if (self._controller == None):
                raise AppNotInitializedProperly()
            else:
                return self._controller(environ, start_resp)
        except:
            fail(start_resp, sys.exc_info())

    def fail(self, start_resp, exc_info):
        start_resp('500 Internal Server Error', [('Content-type', 'text/html')], exc_info)
        return ['<h1>500 Internal Server Error</h1>',
                '<p>Server initialiazation failed.</p>',
                '<code>',
                '<p>', exc_info[0].__name__, ':</br> ',
                str(exc_info[1]), '</p>',
                '</code>'
                ]

try:
    from wsgi import context as ctx

    class _FrontControllerWorker(object):

        def __init__(self):
            self._sess = ctx.Session()
            self._app = None

        def set_app(self, instance):
            self._app = instance

        def __call__(self, environ, start_response):
            context = ctx.Context(self._sess, ctx.Request(environ), ctx.Response(start_response))

            if (self._app == None):
                raise AppNotInitializedProperly('Missing application to execute.')
            else:
                self._app(context)

            return context.response.return_response()

    # TODO: this should be diferent - think about
    FrontControllerFactory._controller = _FrontControllerWorker()
except:
    # TODO: this should be diferent - think about
    FrontControllerFactory._init_exc_info = sys.exc_info()
    FrontControllerFactory._controller = None
