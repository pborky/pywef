__author__="pborky"
__date__ ="$18.2.2010 16:40:48$"

from webob import Request
from webob import Response

class Context(object):
    """
    Context of an application call. Contains webob.Request and webob.Response
    wrappers. Application data should be stored here.
    """

    def __init__(self, environ, start_response, worker):
        self._request = Request(environ)
        self._response = None
        self._worker = worker
        self._start_response = start_response
    
    def _get_request(self):
        """ Request wrapper. The encapsulation of environ dictionary. """
        return self._request
    request = property(_get_request, doc = _get_request.__doc__)

    def _get_response(self):
        """ Response helper. Easy reponse creation. """
        if self._response == None:
            self._response = Response(request=self._request)
        return self._response
    response = property(_get_response, doc = _get_response.__doc__)

    def _return_response(self):
        return self.response(self.request.environ, self._start_response)
    return_response = property(_return_response, doc = _return_response.__doc__)
