__author__="pborky"
__date__ ="$1.3.2010 23:44:36$"

from context import Context
from routes import Mapper
from errorhandler import ControllerInitializationError
from errorhandler import ControllerNotInitializedProperly
from webob.exc import HTTPBadRequest
from webob.exc import HTTPMovedPermanently

class FrontControllerWorker(object):
    """ Application front controller  processer """
    def __init__(self, **controllers):
        self._apps = None
        self._mapper = None

        if (len (controllers) > 0):
            self._apps = {}
            self._mapper = Mapper()

            for key in controllers.keys():
                ctrl = controllers[key]
                
                if isinstance(ctrl, dict):
                    app_keys = ctrl.keys()

                    if not ('app' in app_keys and 'route' in app_keys):
                        raise ControllerInitializationError('Arguments "app" and "route" are required.')

                    if 'route_vars' in app_keys:
                        route_vars = ctrl['route_vars']
                    else:
                        route_vars = None

                    if 'app_vars' in app_keys:
                        app_vars = ctrl['app_vars']
                    else:
                        app_vars = None

                    route = ctrl['route']
                    ctrl = ctrl['app']

                    if (not isinstance(ctrl, type)):
                        ctrl_inst = ctrl
                    else:
                        if (isinstance(app_vars, dict)):
                            #TODO: implement app requirements list
                            ctrl_inst = ctrl(**app_vars)
                        else:
                            ctrl_inst = ctrl()

                    self._apps[key] = ctrl_inst

                    if (isinstance(route_vars, dict)):
                        self._mapper.connect(key, route, controller = ctrl_inst, **route_vars)
                    else:
                        self._mapper.connect(key, route, controller = ctrl_inst)

    def __call__(self, environ, start_response):

        if (self._apps == None):
            raise ControllerNotInitializedProperly('Missing controller to execute.')
        else:
            context = Context(environ=environ, start_response = start_response, worker = self)
            route = self._mapper.match(environ=environ)
            if route == None:
                if not context.request.path_url.endswith('/'):
                    raise HTTPMovedPermanently('Trying add trailing slash.', add_slash=True)
                else:
                    raise HTTPBadRequest('Requested route %s not found.' % context.request.path_url)
            ctrl = route.pop('controller')
            # TODO: test if callable and raise ControllerNotInitializedProperly respectively
            ctrl(context, **route)

        return context.return_response()

