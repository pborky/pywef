__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

# TODO: refactor this module

import sys

class AppNotInitializedProperly(Exception):
    pass

# TODO: refactor - think about how..
class FrontControllerFactory(object):
    """ Factory class. """

    _init_exc_info = None

    @staticmethod
    def produce(application):
        init_exc_info =  FrontControllerFactory._init_exc_info

        if (FrontController == None):
            assert( init_exc_info != None )
            return FrontControllerErrStack(None, True, init_exc_info)
        else:
            assert( init_exc_info == None )
            return FrontControllerErrStack(FrontController(application), True)

class FrontControllerErrStack(object):
    def __init__(self, application, debug = False, init_exc_info = None):
        self._application = application
        self._init_exc_info = init_exc_info
        self._debug = debug
    
    def __call__(self, env, start_resp):
        try:
            if (self._application != None):
                return self._application(env, start_resp)
            else:
                raise AppNotInitializedProperly('Front controller is missing.', self._init_exc_info)
        except:
            exc_info = sys.exc_info()
            if (self._debug):
                start_resp('500 Internal Server Error', [('Content-type', 'text/html')], exc_info)
                try:
                    from errorhandler import ErrHandle
                    return ErrHandle.format_exc(exc_info)
                except ImportError:
                    return ['<h1>500 Internal Server Error</h1><p>Could not render traceback.</p>']
            else:
                start_resp('500 Internal Server Error', [('Content-type', 'text/html')])
                return ['<h1>500 Internal Server Error</h1><p>The server encountered unexpected error.</p>']

try:
    from context import Context
    from context import Request
    from context import Response

    class _FrontControllerWorker(object):
        
        def __init__(self, app_inst):
            self._app = app_inst

        def __call__(self, environ, start_response):
            context = Context(Request(environ), Response(start_response))

            if (self._app == None):
                raise AppNotInitializedProperly('Missing application to execute.')
            else:
                self._app(context)

            return context.response.return_response()

    FrontController = _FrontControllerWorker
except:
    # TODO: this should be diferent - think about
    FrontController = None
    FrontControllerFactory._init_exc_info = sys.exc_info()

