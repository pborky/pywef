__author__="pborky"
__date__ ="$18.2.2010 16:40:48$"

from exc import ExcInfoWrapper, HTTPFound, HTTPInternalServerError
from webob import Request
from webob import Response
from routes.util import GenerationException

class Context(object):
    """
    Context of an application call. Contains webob.Request and webob.Response
    wrappers. Application data should be stored here.
    """

    def __init__(self, environ, start_response, worker = None, mapper = None):
        if worker == None and mapper == None:
            raise TypeError("Either 'worker' or 'mapper' must be passed.")
        self._request = Request(environ)
        self._response = None
        self._url_gen = None
        self._worker = worker
        self._start_response = start_response
        if mapper != None:
            self._mapper = mapper
        else:
            self._mapper = worker.mapper
    
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

    def _get_url_generator(self):
        """ """
        if self._url_gen == None:
            self._url_gen = self._request.environ['routes.url']
        return self._url_gen
    url_generator = property(_get_url_generator, doc = _get_url_generator.__doc__)

    def redirect(self, *args, **kwargs):
        """ """
        try:
            loc = self.url_generator(*args, **kwargs)
            raise HTTPFound('Redirecting to "%s".' % loc, location = loc)
        except GenerationException:
            raise HTTPInternalServerError('Could not redirect. Cannot generate appropiate url.', ExcInfoWrapper())

    def return_response(self):
        """ """
        return self.response(self.request.environ, self._start_response)
