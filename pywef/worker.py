__author__="pborky"
__date__ ="$1.3.2010 23:44:36$"

from context import Context
from routes import Mapper
from routes.util import RoutesException
from exc import HTTPNotFound, HTTPFound, NotInitializedProperly, InitializationError

class FrontControllerWorker(object):
    """ Application front controller  processer """
    #TODO: use of submappers for actions use
    def __init__(self, **controllers):
        self._controllers = None
        self.mapper = None

        if (len (controllers) > 0):
            self._controllers = {}
            self.mapper = Mapper()

            for key in controllers.keys():
                ctrl = controllers[key]
                
                if isinstance(ctrl, dict):
                    ctrl_keys = ctrl.keys()

                    if not ('ctrl' in ctrl_keys and 'route' in ctrl_keys):
                        raise InitializationError('Arguments "ctrl" and "route" are required.')

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
                        self.mapper.connect(key, route, controller = key, **route_vars)
                    else:
                        self.mapper.connect(key, route, controller = key)

    def __call__(self, environ, start_response):

        if (self._controllers == None
                or len(self._controllers) == 0
                or self.mapper == None):
            raise NotInitializedProperly('Missing controller to execute.')
        else:
            context = Context(environ=environ, worker = self)
            try:
                route = self.mapper.match(environ=environ)
                if route == None:
                    if not context.request.path_url.endswith('/'):
                        raise HTTPFound('Trying add trailing slash.', add_slash=True)
                    else:
                        raise HTTPNotFound('Requested route %s cannot be matched.' % context.request.path_url)
            except RoutesException:
                raise HTTPNotFound('Requested route %s cannot be matched.' % context.request.path_url, ExcInfoWrapper())
            ctrl = self._controllers[route['controller']]
            # TODO: test if callable and raise ControllerNotInitializedProperly respectively
            ctrl(context, **route)

        return context.response(environ, start_response) # context.return_response()
