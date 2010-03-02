__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

# TODO: refactor - think about how..

from errorhandler import ExcInfo
from webob.exc import HTTPException

try:
    from worker import FrontControllerWorker
except:
    FrontControllerWorker = None
    init_exc_info = ExcInfo()

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

        if (FrontControllerWorker == None):
            assert( init_exc_info != None )
            return FrontControllerErrStack(None, debug, show_debug_code, init_exc_info)
        else:
            return FrontControllerErrStack(FrontControllerWorker(**apps), debug, show_debug_code)

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
                raise AppNotInitializedProperly('Front controller is missing.',
                            self._init_exc_info)

        except HTTPException, exc:
            
            exc_info = ExcInfo()
            def repl_start_response(status, headers, exc=None):
                if exc is None:
                    exc = exc_info.tuple
                return start_resp(status, headers, exc)
            return exc(environ, repl_start_response)

        except Exception, exc:
            
            exc_info = ExcInfo()

            return exc_info(start_resp, self._debug, self._show_debug_code)

