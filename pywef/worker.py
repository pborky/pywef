__author__="pborky"
__date__ ="$1.3.2010 23:44:36$"

from context import Context
from routes import Mapper
from webob.exc import HTTPBadRequest
from webob.exc import HTTPMovedPermanently

class FrontControllerWorker(object):
    """ Application front controller  processer """
    def __init__(self, **apps):
        self._apps = None
        self._mapper = None

        if (len (apps) > 0):
            self._apps = {}
            self._mapper = Mapper()

            for key in apps.keys():
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
                
                if (not isinstance(app, type)):
                    app_inst = app
                else:
                    if (isinstance(app_vars, dict)):
                        #TODO: implement app requirements list
                        app_inst = app(**app_vars)
                    else:
                        app_inst = app()

                self._apps[key] = app_inst

                if (isinstance(route_vars, dict)):
                    self._mapper.connect(key, route, application = app_inst, **route_vars)
                else:
                    self._mapper.connect(key, route, application = app_inst)

    def __call__(self, environ, start_response):

        if (self._apps == None):
            raise AppNotInitializedProperly('Missing application to execute.')
        else:
            context = Context(environ=environ, start_response = start_response, worker = self)
            route = self._mapper.match(environ=environ)
            if route == None:
                if not context.request.path_url.endswith('/'):
                    raise HTTPMovedPermanently('Trying add trailing slash.', add_slash=True)
                else:
                    raise HTTPBadRequest('Requested route %s not found.' % context.request.path_url)
            app = route.pop('application')
            app(context, **route)

        return context.return_response()

