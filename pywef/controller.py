import sys
__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

# TODO: refactor - think about how..

from exc import ExcInfoWrapper, NotInitializedProperly, HTTPOk, HTTPRedirection, HTTPError, HTTPInternalServerError
from pywef.logger import set_logger, get_logger
from pywef.monitor import Monitor

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
    
    def __init__(self, controllers, **kw):

        self._debug = kw.get('debug', False)
        
        self._init_exc_info = None
        self._worker = None
        # TODO: following is shit...
        #try:
        if kw.has_key('loggers'):
            for name, data in kw.get('loggers').items():
                exc = data.get('exc')
                if exc != None:
                    init = exc.get('init', False)
                    call = exc.get('call', False)
                   
                file = data.get('file')
                fname = file.get('name')
                size = file.get('size')
                count = file.get('count')
                set_logger(name, fname, max_bytes = size, backup_count = count)
        
        if kw.has_key('exc_wrapper'):
            exc_wrapper = kw.get('exc_wrapper')
            logger = get_logger(exc_wrapper.get('logger'))
            init = exc_wrapper.get('init')
            call = exc_wrapper.get('call')
            ExcInfoWrapper._loggers.append((logger, init, call))

        if kw.has_key('monitor'):
            monitor = kw.get('monitor')
            logger = get_logger(monitor.get('logger'))
            force_restart = monitor.get('force_restart', True)
            self._monitor = Monitor(logger=logger, force_restart=force_restart)
            for i in monitor.get('track_files', []):
                self._monitor.track(i)
            self._monitor.start()
        
        
        #except:
        #    self._init_exc_info = ExcInfoWrapper()

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

