__author__="pborky"
__date__ ="$18.2.2010 16:40:48$"

import cStringIO
import copy

class Request:
    """ TODO: parse the environ and prive own properties """

    def __init__(self, environ):
        """ Initiate Request object """
        self._environ = environ
        lines = []
        for line in environ['wsgi.input']:
            lines.append(line)
        newlines = copy.copy(lines)
        self._content = newlines #cStringIO.StringIO(''.join(newlines))
        environ['wsgi.input'] = None

    @property
    def content(self):
        """ Get the body of request as a stream """
        return self._content

    @property
    def environ(self):
        """ Access the environ  """
        return self._environ

class Response:

    _STATUS_LIST = {
                        0: '',
                        200:'200 OK',
                        500:'500 Internal Server Error'
                   }

    def __init__(self, start_response, status=0, header=None, body=None):
        
        self._start_response = start_response
        
        self.status = status
        
        if (header==None):
            self._header = []
        else:
            self._header = [].extend(header)

        if (body==None):
            self._body = []
        else:
            self._body = [].extend(body)
    
    @property
    def statusList(self):
        """ List of HTTP satus keys """
        return Response._STATUS_LIST.keys()

    @property
    def statusString(self):
        return Response._STATUS_LIST[self.status]

    @property
    def status(self):
        """ HTTP status integer defined by Response.statusList """
        return self._status

    @status.setter
    def status(self, value):
        if (not value in Response._STATUS_LIST):
            raise Exception('HTTP status %s is not defined' % value)
        self._status = value

    @property
    def header(self):
        return self._header

    @property
    def body(self):
        return self._body

    @property
    def contentLength(self):
        l = 0
        for i in self._body:
            l += len(i)
        return l

    def return_response(self):
        if (self.status == 0):
            raise Exception('HTTP status is unset')

        self._start_response(self.statusString, self.header)
        return self.body

class Session:
    pass

class Context:

    def __init__(self, session, request, response):
        self._session = session
        self._request = request
        self._response = response

    @property
    def session(self):
        return self._session

    @property
    def request(self):
        return self._request

    @property
    def response(self):
        return self._response