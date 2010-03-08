import sys
__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

# TODO: refactor - think about how..

from exc import ExcInfoWrapper, NotInitializedProperly, HTTPOk, HTTPRedirection, HTTPError, HTTPInternalServerError

try:
    from worker import FrontControllerWorker
    from routes.middleware import RoutesMiddleware
    init_exc_info = None
except:
    FrontControllerWorker = None
    RoutesMiddleware  = None
    init_exc_info = ExcInfoWrapper()

class FrontController(object):
    """
    Error catching midleware. Intended to provide debug output - traceback.
    If the exception is throwed with exc_info tuple as an additional argument
    it is root cause and that is showed too.
    """
    
    def __init__(self, controllers, debug = 0):

        if isinstance(debug, int):
            self._debug = debug
        else:
            if debug:
                self._debug = 2
            else:
                self._debug = 0
            
        self._init_exc_info = None
        self._worker = None

        if (FrontControllerWorker == None):
            self._init_exc_info = init_exc_info
        else:
            try:
                worker = FrontControllerWorker(**controllers)
                if RoutesMiddleware == None:
                    self._worker = worker
                else:
                    self._worker = RoutesMiddleware(worker, worker.mapper, singleton = True)
            except:
                self._init_exc_info = ExcInfoWrapper()
    
    def __call__(self, environ, start_resp):
        try:
            try:

                if (self._worker != None):
                    return self._worker(environ, start_resp)
                else:
                    raise NotInitializedProperly('Front controller worker is missing.', self._init_exc_info)

            except HTTPOk:
                raise HTTPInternalServerError('HTTPOk raised but not properly processed.', ExcInfoWrapper())

            except HTTPRedirection:
                exc_info = ExcInfoWrapper()
                return exc_info(environ, start_resp, self._debug)

            except HTTPError:
                exc_info = ExcInfoWrapper()
                return exc_info(environ, start_resp, self._debug)
            
            except Exception:
                raise HTTPInternalServerError('Exceptional state detected.', ExcInfoWrapper())
            

        except HTTPError:
            exc_info = ExcInfoWrapper()
            return exc_info(environ, start_resp, self._debug)

