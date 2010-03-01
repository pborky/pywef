__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

# TODO: refactor - think about how..

import sys

class AppNotInitializedProperly(Exception):
    pass

class FrontControllerFactory(object):
    """ Factory class. """

    _init_exc_info = None

    @staticmethod
    def produce(apps, debug = False, show_debug_code = True):
        """
        Producent of Front controller. That is stacked with midleware error
        stack. Most fatal exceptions like missing import are catched. 
        If debug = True traceback is showed.
        If show_debug_code = True  then more debug lines are showing.
        """

        init_exc_info =  FrontControllerFactory._init_exc_info

        if (FrontController == None):
            assert( init_exc_info != None )
            return FrontControllerErrStack(None, debug, show_debug_code, init_exc_info)
        else:
            assert( init_exc_info == None )
            return FrontControllerErrStack(FrontController(**apps), debug, show_debug_code)

class FrontControllerErrStack(object):
    """
    Error catching midleware. Intended to provide debug output - traceback.
    If the exception is throwed with exc_info tuple as an additional argument
    it is root cause and that is showed too.
    """

    def __init__(self, worker, debug, show_debug_code, init_exc_info = None):
        self._worker = worker
        self._init_exc_info = init_exc_info
        self._debug = debug
        self._show_debug_code = show_debug_code
    
    def __call__(self, environ, start_resp):
        try:
            if (self._worker != None):
                return self._worker(environ, start_resp)
            else:
                raise AppNotInitializedProperly('Front controller is missing.', self._init_exc_info)
        except: # TODO: handle webob.exc
            exc_info = sys.exc_info()
            if (self._debug):
                start_resp('500 Internal Server Error', [('Content-type', 'text/html')], exc_info)
                try:
                    from errorhandler import ErrHandle
                    return ErrHandle.format_exc(exc_info, self._show_debug_code)
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

    try:
        from routes import Mapper
    except:
        raise ImportError('Import failed (package routes).', sys.exc_info())

    class _FrontControllerWorker(object):
        """ Application front controller  processer """
        #TODO: extend functionality move to separate package, this is the core so be careful
        def __init__(self, **apps):
            
            if (len (apps) > 0):
                self._apps = {}
                self._mapper = Mapper()

                for key in apps.keys():
                    # TODO: detect if appvars or rvars are passed (or reimplement using dict instead of tuple of tuples..)
                    # if no name passed noething happens -  use the app as a key
                    app = apps[key]
                    app_keys = app.keys()
                    
                    if 'route_vars' in app_keys:
                        route_vars = app['route_vars']
                    else:
                        route_vars = None

                    if 'app_vars' in app_keys:
                        app_vars = app['app_vars']
                    else:
                        app_vars = None
             
                    route = app['route']
                    app = app['app']

                    # TODO: do we support old style objects?
                    if (not isinstance(app, type)):
                        app_inst = app
                    else:
                        if (isinstance(app_vars, dict)):
                            app_inst = app(**app_vars)
                        else:
                            app_inst = app()

                    self._apps[key] = app_inst

                    if (isinstance(route_vars, dict)):
                        self._mapper.connect(key, route, application = app_inst, **route_vars)
                    else:
                        self._mapper.connect(key, route, application = app_inst)
            else:
                self._apps = None
                self._mapper = None

        def __call__(self, environ, start_response):

            if (self._apps == None):
                raise AppNotInitializedProperly('Missing application to execute.')
            else:
                request = Request(environ)
                response = Response(request = request)
                context = Context(request, response)
                route = self._mapper.match(environ=environ)
                if not (route != None):
                    # TODO: use webob.exc
                    raise Exception('Not found.')
                app = route.pop('application')
                app(context, **route)
            
            return context.response(environ, start_response)

    FrontController = _FrontControllerWorker
except:
    FrontController = None
    FrontControllerFactory._init_exc_info = sys.exc_info()

