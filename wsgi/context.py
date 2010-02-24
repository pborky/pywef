__author__="pborky"
__date__ ="$18.2.2010 16:40:48$"

class Context(object):
    """ """

    def __init__(self, request, response):
        # TODO: fix following
        d = self.__dict__
        d['_request'] = request
        d['_response'] = response

    def __setattr__(self, name, val):
        if name.startswith('_'):
            raise Exception('Attribute %s is read only.' % name)
        self.__dict__[name] = val
    
    def _get_request(self):
        """ """
        return self._request
    request = property(_get_request,doc =_get_request.__doc__)

    def _get_response(self):
        """ """
        return self._response
    response = property(_get_response,doc =_get_response.__doc__)
            
