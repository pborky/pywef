__author__="pborky"
__date__ ="$18.2.2010 16:40:48$"

from logger import get_logger
from exc import HTTPFound, HTTPInternalServerError
from webob import Request
from webob import Response
from routes.util import GenerationException

log = get_logger('pywef.context')

class Context(object):
    """
    Context of an application call. Contains webob.Request and webob.Response
    wrappers. Application data should be stored here.
    """

    def __init__(self, environ, worker = None, mapper = None,
                match_callback = None, generator_callback = None):
        if worker == None and mapper == None:
            raise TypeError("Either 'worker' or 'mapper' must be passed.")
        self._request = Request(environ)
        self._worker = worker
        if mapper != None:
            self._mapper = mapper
        else:
            self._mapper = worker.mapper
        self._match_callback = match_callback
        if match_callback is None:
            if hasattr(self._mapper,'routematch'):
                self._match_callback = self._mapper.routematch
            elif hasattr(self._mapper,'match'):
                self._match_callback = self._mapper.match
        
        self._generator_callback = generator_callback

        self._data = None
        self._response = None
        self._route = None
        self._match_dict = None
    
    def _request__get(self):
        """ Request wrapper. The webob encapsulation of environ dictionary. """
        return self._request
    request = property(_request__get, doc = _request__get.__doc__)

    def _environ__get(self):
        ''' '''
        return self.request.environ
    environ = property(_environ__get, doc = _environ__get.__doc__)

    def _response__get(self):
        ''' Response creation. '''
        if self._response is None:
            self._response = Response(request=self._request)
        return self._response
    response = property(_response__get, doc = _response__get.__doc__)
    
    def _worker__get(self):
        ''' '''
        return self._worker
    worker = property(_worker__get, doc = _worker__get.__doc__)

    def _route__get(self):
        ''' '''
        return self._route
    route = property(_route__get, doc = _route__get.__doc__)

    def _match_dict__get(self):
        ''' '''
        return self._match_dict
    match_dict = property(_match_dict__get, doc = _match_dict__get.__doc__)

    def _data__get(self):
        ''' '''
        if self._data is None:
            self._data = {}
            self._data['url_generator'] = self.url
            self._data['url'] = self.url
            self._data['request'] = self.request
        return self._data
    data = property(_data__get, doc = _data__get.__doc__)

    def _get_url_generator(self):
        ''' '''
        if self._generator_callback is not None:
            return self._generator_callback
        else:
            raise TypeError('Url generator callback not defined.')
    url_generator = property(_get_url_generator, doc = _get_url_generator.__doc__)
    
    def _matcher__get(self):
        ''' '''
        if self._match_callback is not None:
            return self._match_callback
        else:
            raise TypeError('Matcher callback not defined.')
    matcher = property(_matcher__get, doc = _matcher__get.__doc__)

    def match(self):
        ''' '''
        results = self.matcher(environ=self.environ)
        if results:
            self._match_dict, self._route = results[0], results[1]
            urlinfo = "%s %s" % (self.environ['REQUEST_METHOD'], self.environ['PATH_INFO'])
            log.debug("Matched %s", urlinfo)
            log.debug("Route path: '%s', defaults: %s", self._route.routepath, self._route.defaults)
            log.debug("Match dict: %s", self._match_dict)
        else:
            self._match_dict = self._route = None

        return self._match_dict

    def url(self, *arg, **kwarg):
        url = self.url_generator(*arg, **kwarg)
        if url.startswith('/'):
            url = self.request.application_url + url
        return url

    def redirect(self, *arg, **kwarg):
        ''' '''
        try:
            loc = self.url(*arg, **kwarg)
            raise HTTPFound('Redirecting to "%s".' % loc, location = loc)
        except GenerationException:
            raise HTTPInternalServerError('Could not redirect. Cannot generate appropiate url.')

    def return_response(self, start_response):
        ''' '''
        return self.response(self.request.environ, start_response)
