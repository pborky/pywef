__author__="pborky"
__date__ ="$1.3.2010 23:44:36$"

from context import Context
from routes import Mapper
from errorhandler import ControllerInitializationError
from errorhandler import ControllerNotInitializedProperly
from webob.exc import HTTPBadRequest
from webob.exc import HTTPFound

class FrontControllerWorker(object):
    """ Application front controller  processer """
    def __init__(self, **controllers):
        self._controllers = None
        self._mapper = None

        if (len (controllers) > 0):
            self._controllers = {}
            self._mapper = Mapper()

            for key in controllers.keys():
                ctrl = controllers[key]
                
                if isinstance(ctrl, dict):
                    ctrl_keys = ctrl.keys()

                    if not ('ctrl' in ctrl_keys and 'route' in ctrl_keys):
                        raise ControllerInitializationError('Arguments "app" and "route" are required.')

                    if 'route_vars' in ctrl_keys:
                        route_vars = ctrl['route_vars']
                    else:
                        route_vars = None

                    if 'ctrl_vars' in ctrl_keys:
                        ctrl_vars = ctrl['ctrl_vars']
                    else:
                        ctrl_vars = None

                    route = ctrl['route']
                    ctrl = ctrl['ctrl']

                    if (not isinstance(ctrl, type)):
                        ctrl_inst = ctrl
                    else:
                        if (isinstance(ctrl_vars, dict)):
                            #TODO: implement app requirements list
                            ctrl_inst = ctrl(**ctrl_vars)
                        else:
                            ctrl_inst = ctrl()

                    self._controllers[key] = ctrl_inst

                    if (isinstance(route_vars, dict)):
                        self._mapper.connect(key, route, controller = key, **route_vars)
                    else:
                        self._mapper.connect(key, route, controller = key)

    def __call__(self, environ, start_response):

        if (self._controllers == None
                or len(self._controllers) == 0
                or self._mapper == None):
            raise ControllerNotInitializedProperly('Missing controller to execute.')
        else:
            context = Context(environ=environ, start_response = start_response, worker = self)
            route = self._mapper.match(environ=environ)
            if route == None:
                if not context.request.path_url.endswith('/'):
                    raise HTTPFound('Trying add trailing slash.', add_slash=True)
                else:
                    raise HTTPBadRequest('Requested route %s not found.' % context.request.path_url)
            ctrl = self._controllers[route['controller']]
            # TODO: test if callable and raise ControllerNotInitializedProperly respectively
            ctrl(context, **route)

        return context.return_response()

    def _get_mapper(self):
        """"""
        return self._mapper
    mapper = property(_get_mapper, doc = _get_mapper.__doc__)
