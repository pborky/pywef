__author__="pborky"
__date__ ="$18.2.2010 16:40:48$"

import cStringIO
import copy

class Request:
    """ TODO: parse the environ and provide high level properties """

    def __init__(self, environ):
        """ Initiate Request object """
        self.environ = environ
        lines = []
        for line in environ['wsgi.input']:
            lines.append(line)
        newlines = copy.copy(lines)
        self.content = newlines #cStringIO.StringIO(''.join(newlines))
        environ['wsgi.input'] = None
        
    def __setattr__(self, name, val):
        if name in ('environ', 'content'):
            raise Exception('Attribute %s is read only.' % name)
        self.__dict__[name] = val

class Response:
    """ """
    
    _STATUS_LIST = {
                        0: '',
                        200:'200 OK',
                        500:'500 Internal Server Error'
                   }

    def __init__(self, start_response, status=0, header=None, body=None):
        
        self._start_response = start_response        
        self.status = status        
        if (header==None):
            self.header = []
        else:
            self.header = [].extend(header)
        if (body==None):
            self.body = []
        else:
            self.body = [].extend(body)

    def __setattr__(self, name, val):
        if (name in ('status')) and (not value in Response._STATUS_LIST):
            raise Exception('HTTP status %s is not defined' % value)
        self.__dict__[name] = val

    def get_status_string(self):
        return Response._STATUS_LIST[self.status]
    
    def get_content_length(self):
        l = 0
        for i in self._body:
            l += len(i)
        return l

    def return_response(self):
        if (self.status == 0):
            raise Exception('HTTP status is unset')
        self._start_response(self.get_status_string(), self.header)
        return self.body

class Context:
    """ """

    def __init__(self, request, response):
        # TODO: fix following
        self.__dict__['request'] = request
        self.__dict__['response'] = response
    
    def __setattr__(self,name, val):
        if name in ('request', 'response'):
            raise Exception('Attribute %s is read only.' % name)
        self.__dict__[name] = val    
            
