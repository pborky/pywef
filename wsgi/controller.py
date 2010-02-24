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
    def produce(application, debug = True):
        """ """

        init_exc_info =  FrontControllerFactory._init_exc_info

        if (FrontController == None):
            assert( init_exc_info != None )
            return FrontControllerErrStack(None, True, init_exc_info)
        else:
            assert( init_exc_info == None )
            return FrontControllerErrStack(FrontController(application), debug)

class FrontControllerErrStack(object):
    """ """

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
                    (type, val) = sys.exc_info()[:2]
                    msg = '<code><b>%s: %s</b></code>.'
                    if (len(val.args) > 1):
                        msg = msg % (type.__name__, str(val))
                    else:
                        msg = msg % (type.__name__, str(val[0]))
                    return ['<h1>500 Internal Server Error</h1><p>Server encountered an unexpected error.</p><p>%s</p>' % msg]
            else:
                start_resp('500 Internal Server Error', [('Content-type', 'text/html')])
                return ['<h1>500 Internal Server Error</h1><p>The server encountered unexpected error.</p>']

try:
    try:
        from webob import Request
        from webob import Response
    except ImportError:
        raise ImportError('Import failed (package webob).', sys.exc_info())

    try:
        from context import Context
    except:
        raise ImportError('Import failed (package wsgi.context).', sys.exc_info())


    class _FrontControllerWorker(object):
        
        def __init__(self, application):
            self._app = application

        def __call__(self, environ, start_response):

            if (self._app == None):
                raise AppNotInitializedProperly('Missing application to execute.')
            else:
                request = Request(environ)
                response = Response(request = request)
                context = Context(request, response)
                self._app(context)

            return context.response(environ, start_response)

    FrontController = _FrontControllerWorker
except:
    FrontController = None
    FrontControllerFactory._init_exc_info = sys.exc_info()

