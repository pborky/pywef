__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

# TODO: refactor this module

import sys
from errorhandler import ErrHandle

class AppNotInitializedProperly(Exception):
    pass

# TODO: refactor - think about how..
class FrontControllerFactory(object):
    """ Factory class. """

    _worker_cls = None
    _init_exc_info = None

    @staticmethod
    def produce(app_inst):
        init_exc_info =  FrontControllerFactory._init_exc_info
        worker_cls = FrontControllerFactory._worker_cls

        if (worker_cls == None):
            assert( init_exc_info != None )
            return FrontControllerFactory(None, init_exc_info)
        else:
            assert( init_exc_info == None )
            return FrontControllerFactory(worker_cls(app_inst), None)
    
    def __init__(self, controller, init_exc_info):
        self._controller = controller
        self._init_exc_info = init_exc_info
    
    def __call__(self, environ, start_resp):
        try:
            if (self._controller != None):
                return self._controller(environ, start_resp)
            else:
                raise AppNotInitializedProperly('Front controller is missing.', self._init_exc_info)
        except:
            exc_info = sys.exc_info()
            start_resp('500 Internal Server Error', [('Content-type', 'text/html')], exc_info)
            return ErrHandle.format_exc(exc_info)


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

    # TODO: this should be diferent - think about
    FrontControllerFactory._worker_cls = _FrontControllerWorker
except:
    # TODO: this should be diferent - think about
    FrontControllerFactory._init_exc_info = sys.exc_info()
    FrontControllerFactory._worker_cls = None