__author__="pborky"
__date__ ="$23.3.2010 23:13:24$"

import urlparse
import sys
try:
    from string import Template
except ImportError:
    from webob.util.stringtemplate import Template
from webob import Response, Request, html_escape
from traceback import extract_tb
#######
# pywef
from logger import get_logger

log = get_logger('pywef.exc')

def no_escape(value):
    if value is None:
        return ''
    if not isinstance(value, basestring):
        if hasattr(value, '__unicode__'):
            value = unicode(value)
        else:
            value = str(value)
    return value


############################################################
## Classes defined in thos module
############################################################
# Each HTTP state has appropiate exception object.
# A wrapper object is defined. That allows you to use
# java-like traceback.
#
# ExcInfoWrapper (object)
#  HTTPException (Exception)
#    HTTPOk (allways must be catched and processed normally)
#      * 200 - HTTPOk
#      * 201 - HTTPCreated
#      * 202 - HTTPAccepted
#      * 203 - HTTPNonAuthoritativeInformation
#      * 204 - HTTPNoContent
#      * 205 - HTTPResetContent
#      * 206 - HTTPPartialContent
#    HTTPRedirection
#      * 300 - HTTPMultipleChoices
#      * 301 - HTTPMovedPermanently
#      * 302 - HTTPFound
#      * 303 - HTTPSeeOther
#      * 304 - HTTPNotModified
#      * 305 - HTTPUseProxy
#      * 306 - Unused (not implemented, obviously)
#      * 307 - HTTPTemporaryRedirect
#    HTTPError
#      HTTPClientError
#        * 400 - HTTPBadRequest
#        * 401 - HTTPUnauthorized
#        * 402 - HTTPPaymentRequired
#        * 403 - HTTPForbidden
#        * 404 - HTTPNotFound
#        * 405 - HTTPMethodNotAllowed
#        * 406 - HTTPNotAcceptable
#        * 407 - HTTPProxyAuthenticationRequired
#        * 408 - HTTPRequestTimeout
#        * 409 - HTTPConflict
#        * 410 - HTTPGone
#        * 411 - HTTPLengthRequired
#        * 412 - HTTPPreconditionFailed
#        * 413 - HTTPRequestEntityTooLarge
#        * 414 - HTTPRequestURITooLong
#        * 415 - HTTPUnsupportedMediaType
#        * 416 - HTTPRequestRangeNotSatisfiable
#        * 417 - HTTPExpectationFailed
#      HTTPServerError
#        * 500 - HTTPInternalServerError
#        * 501 - HTTPNotImplemented
#        * 502 - HTTPBadGateway
#        * 503 - HTTPServiceUnavailable
#        * 504 - HTTPGatewayTimeout
#        * 505 - HTTPVersionNotSupported
#
#References:
#
#.. [1] http://www.python.org/peps/pep-0333.html#error-handling
#.. [2] http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5


############################################################
## ExcInfoWrapper
############################################################
# Wraps exception info and supports methods for generation
# of HTTP response.
#

class ExcInfoWrapper(object):
    ''' Wrapper around sys.exc_info().  '''

    plain_template = Template('''\
${status}
${explanation}

${exception}: ${detail}
${_traceback}''')
    plain_url_template = Template('''\
"${location}"''')
    plain_tb = Template('''\
  Traceback:
${_items}
${_nested}''')
    plain_tb_item = Template('''\
    File "${filename}, line ${lineno}, in "${name}"
       [${line}]
''')
    plain_tb_nested = Template('''\
${exception}`s root cause:
${nest_exception}: ${nest_detail}
${_nest_traceback}''')
    html_template = Template('''\
<html>
 <head>
  <title>${status}</title>
 </head>
 <body>
  <h1>${status}</h1>
  <p>${explanation}</p>
  <p><code><b>${exception}: ${detail}</b></code></p>
  ${_traceback}
 </body>
</html>''')
    html_url_template = Template('''\
<a href=${location}>${location}</a>''')
    html_tb = Template('''\
<p><code>Traceback:</code><br/>
${_items}
${_nested}''')
    html_tb_item = Template('''\
<code>
File "<b><font color="blue">${filename}</font></b>,
line <b>${lineno}</b>,
in "<b>${name}</b>"</code><br/>
<code>&nbsp;&nbsp;&nbsp;[<font color="red">${line}</font>]</code><br/>''')
    html_tb_nested = Template('''\
<p><code><b>${exception}</b></code>`s root cause:</p>
<p><code><b>${nest_exception}: ${nest_detail}</b></code></p>
${_nest_traceback}''')

    _templates = {
        'html' : {
            'escape' : html_escape,
            'template' : html_template,
            'url_template' : html_url_template,
            'traceback' : {
                'template' : html_tb,
                'item' : html_tb_item,
                'nested' : html_tb_nested } },
        'plain' : {
            'escape' : no_escape,
            'template' : plain_template,
            'url_template' : plain_url_template,
            'traceback' : {
                'template' : plain_tb,
                'item' : plain_tb_item,
                'nested' : plain_tb_nested } } }

    _logging = {'init': True, 'call': True}

    def __init__(self, exc_info = None):
        if exc_info == None:
            (cls, exc, tb) = sys.exc_info()
        else:
            (cls, exc, tb) = exc_info
        self._exc_info = {'cls':cls, 'exc':exc, 'tb':tb}
        self._tuple = (cls, exc, tb)

        self._write_log('Catching: %s: %s' % (self.typename, self.detail), init=True)

    def __iter__(self):
        return self._exc_info.__iter__()

    def __getitem__(self, key):
        if (isinstance(key, int)):
            return self._tuple[key]
        else:
            return self._exc_info[key]

    def __call__(self, environ, start_resp, debug = False):
        exc = self.exc

        self._write_log(' ** Responding: %s: %s' % (self.typename, self.detail), call=True)

        if not issubclass(exc.__class__, HTTPException):
            exc = HTTPInternalServerError()

        def repl_start_response(status, headers, exc=None):
            if exc==None:
                exc = self.tuple
            return start_resp(status, headers, exc)

        return self._generate_response(environ, repl_start_response, debug, exc)

    def _write_log(self, msg, call = False, init = False):
        # TODO: call and init arguments are very crappy... also self._loggers..
        exc_cls = self.cls
        if (call and self._logging['call']) or (init and self._logging['init']):
            if call:
                if issubclass(exc_cls, HTTPError):
                    log.critical(msg)
            else:
                if issubclass(exc_cls, HTTPError):
                    log.error(msg)
                elif issubclass(exc_cls, HTTPRedirection) or issubclass(exc_cls, HTTPOk):
                    log.info(msg)
                else:
                    log.warn(msg)


    def _get_traceback(self):
        '''  '''
        exc = self.exc
        if not issubclass(exc.__class__, HTTPException):
            exc = HTTPInternalServerError()
        return self._get_body(Request.blank('/').environ, self._templates['plain'], 2,
                        exc.status, exc.explanation, '?', exc.headerlist)
    traceback=property(_get_traceback, doc=_get_traceback.__doc__)

    def _generate_response(self, environ, start_response, debug, exc):
        assert issubclass(exc.__class__, HTTPException)
        req = Request(environ)
        location = exc.location
        if exc.add_slash:
            url = req.path
            url += '/'
            if req.environ.get('QUERY_STRING'):
                url += '?' + req.environ['QUERY_STRING']
            location = url
        if location != None:
            location = urlparse.urljoin(req.path_url, location)
        accept = environ.get('HTTP_ACCEPT', '')
        if accept and 'html' in accept or '*/*' in accept:
            content_type = 'text/html'
            temp = self._templates['html']
        else:
            content_type = 'text/plain'
            temp = self._templates['plain']
        body=self._get_body(environ, temp, debug, exc.status, exc.explanation, location, exc.headerlist)
        resp = Response(\
            body=body,
            status=exc.status,
            headerlist=exc.headerlist,
            content_type=content_type,
            location=location
        )
        return resp(environ, start_response)

    def _get_body(self, environ, temp, debug, status, explanation, location, headerlist):
        escape = temp['escape']
        template = temp['template']
        url_template = temp['url_template']
        traceback = temp['traceback']

        args = {
            'status' : escape(status),
            'exception' : self.typename,
            'detail': self.detail,
        }

        if location == None:
            args['location'] = ''
        else:
            args['location'] = url_template.substitute(location=escape(location))

        for k, v in environ.items():
            args[k] = escape(v)
        for k, v in headerlist:
            args[k.lower()] = escape(v)
        t = Template(''.join(explanation))
        args['explanation'] = t.substitute(args)
        if debug:
            args['_traceback'] = self._get_traceback(traceback, escape, debug)
        else:
            args['_traceback'] = ''

        return template.substitute(args)

    def _get_traceback(self, temp, escape, debug):

        template = temp['template']
        item_template = temp['item']
        nested_template = temp['nested']

        args = {
            'filename' : '',
            'lineno' : '',
            'name' : '',
            'line' : ''
        }
        items = []

        exc_tb = extract_tb(self.tb)
        exc_tb.reverse()

        for filename, lineno, name, line in exc_tb:
            args['filename'] = escape(filename)
            args['lineno'] = escape(lineno)
            args['name' ] = escape(name)
            args['line'] = escape(line)

            items.append(item_template.substitute(args))

        args = {
            'exception' : escape(self.typename),
            'nest_exception' : '',
            'nest_detail' : '',
            '_nested_template' : ''
        }
        nested = []

        for i in self.nested:
            args['nest_exception'] = escape(i.typename)
            args['nest_detail'] = escape(i.detail)
            args['_nest_traceback'] = i._get_traceback(temp, escape, debug)
            nested.append(nested_template.substitute(args))

        args = {
            '_items' : ''.join(items),
            '_nested' : ''.join(nested)
        }
        return template.substitute(args)

    def _get_tuple(self):
        '''  '''
        return self._tuple
    tuple = property(_get_tuple, doc = _get_tuple.__doc__)

    def _get_cls(self):
        '''  '''
        return self._exc_info['cls']
    cls = property(_get_cls, doc = _get_cls.__doc__)

    def _get_exc(self):
        '''  '''
        return self._exc_info['exc']
    exc = property(_get_exc, doc = _get_exc.__doc__)

    def _get_tb(self):
        '''  '''
        return self._exc_info['tb']
    tb = property(_get_tb, doc = _get_tb.__doc__)

    def _get_detail(self):
        '''  '''
        exc_val = self.exc
        if (len(exc_val.args) >= 1):
            return str(exc_val.args[0])
        else:
            return ''
    detail = property(_get_detail, _get_detail.__doc__)

    def _get_typename(self):
        '''  '''
        return self.cls.__name__
    typename = property(_get_typename, _get_typename.__doc__)

    def _get_nested(self):
        '''  '''
        args = self.exc.args
        list = []
        if (len(args)>0):
            for i in args:
                if (isinstance(i,ExcInfoWrapper)):
                    list.append(i)
        return list
    nested = property(_get_nested, _get_nested.__doc__)



############################################################
## HTTP Exception classes
############################################################
#
# 
#

class HTTPException(Exception):
    """
    Exception used on pre-Python-2.5, where new-style classes cannot be used as
    an exception. We only support python 2.5+.
    """
    ## You should set in subclasses:
    # code = 200
    # title = 'OK'
    # explanation = 'why this happens'
    # body_template_obj = Template('response template')
    code = None
    title = None
    explanation = ''
    ## Set this to True for responses that should have no request body
    empty_body = False
    location=''
    add_slash=False

    def __init__(self, detail=None, exc_info=False, headerlist=None, comment=None, **kargs):

        if exc_info:
            if not isinstance(exc_info, wrap_exc.ExcInfoWrapper):
                if not isinstance(exc_info, bool):
                    exc_info = wrap_exc.ExcInfoWrapper(exc_info)
                else:
                    exc_info = wrap_exc.ExcInfoWrapper()
            Exception.__init__(self, detail, exc_info, **kargs)
        else:
            #TODO:check kargs for ExcInfoWrapper instance
            Exception.__init__(self, detail, **kargs)

        self.status='%s %s' % (self.code, self.title)

        self.headerlist = []
        if headerlist:
            self.headerlist.append(headerlist)
        self.detail = detail
        self.comment = comment

        for key, value in kargs:
            self.__setattr__( key, value )

class HTTPError(HTTPException):
    """
    base class for status codes in the 400's and 500's

    This is an exception which indicates that an error has occurred,
    and that any work in progress should not be committed.  These are
    typically results in the 400's and 500's.
    """

class HTTPRedirection(HTTPException):
    """
    base class for 300's status code (redirections)

    This is an abstract base class for 3xx redirection.  It indicates
    that further action needs to be taken by the user agent in order
    to fulfill the request.  It does not necessarly signal an error
    condition.
    """
body_template=None,
class HTTPOk(HTTPException):
    """
    Base class for the 200's status code (successful responses)
    """
    code = 200
    title = 'OK'

############################################################
## 2xx success
############################################################

class HTTPCreated(HTTPOk):
    code = 201
    title = 'Created'

class HTTPAccepted(HTTPOk):
    code = 202
    title = 'Accepted'
    explanation = 'The request is accepted for processing.'

class HTTPNonAuthoritativeInformation(HTTPOk):
    code = 203
    title = 'Non-Authoritative Information'

class HTTPNoContent(HTTPOk):
    code = 204
    title = 'No Content'
    empty_body = True

class HTTPResetContent(HTTPOk):
    code = 205
    title = 'Reset Content'
    empty_body = True

class HTTPPartialContent(HTTPOk):
    code = 206
    title = 'Partial Content'

## FIXME: add 207 Multi-Status (but it's complicated)


############################################################
## 3xx redirection
############################################################

class _HTTPMove(HTTPRedirection):
    """
    redirections which require a Location field

    Since a 'Location' header is a required attribute of 301, 302, 303,
    305 and 307 (but not 304), this base class provides the mechanics to
    make this easy.

    You can provide a location keyword argument to set the location
    immediately.  You may also give ``add_slash=True`` if you want to
    redirect to the same URL as the request, except with a ``/`` added
    to the end.

    Relative URLs in the location will be resolved to absolute.
    """
    explanation = ('The resource has been moved to ${location};',
                    'you should be redirected automatically.')

    def __init__(self, detail=None, exc_info=None, headerlist=None, comment=None,
                location=None, add_slash=False, **kargs):
        HTTPRedirection.__init__(self, detail=detail, headerlist=headerlist, comment=comment, exc_info=exc_info, **kargs)
        if location is not None:
            self.location = location
            if add_slash:
                raise TypeError("You can only provide one of the arguments location and add_slash")
        self.add_slash = add_slash

class HTTPMultipleChoices(_HTTPMove):
    code = 300
    title = 'Multiple Choices'

class HTTPMovedPermanently(_HTTPMove):
    code = 301
    title = 'Moved Permanently'

class HTTPFound(_HTTPMove):
    code = 302
    title = 'Found'
    explanation = ('The resource was found at ${location};',
                    'you should be redirected automatically.')

# This one is safe after a POST (the redirected location will be
# retrieved with GET):
class HTTPSeeOther(_HTTPMove):
    code = 303
    title = 'See Other'

class HTTPNotModified(HTTPRedirection):
    # FIXME: this should include a date or etag header
    code = 304
    title = 'Not Modified'
    empty_body = True

class HTTPUseProxy(_HTTPMove):
    # Not a move, but looks a little like one
    code = 305
    title = 'Use Proxy'
    explanation = ('The resource must be accessed through a proxy located at ${location};',
                    'you should be redirected automatically.')

class HTTPTemporaryRedirect(_HTTPMove):
    code = 307
    title = 'Temporary Redirect'


############################################################
## 4xx client error
############################################################

class HTTPClientError(HTTPError):
    """
    base class for the 400's, where the client is in error

    This is an error condition in which the client is presumed to be
    in-error.  This is an expected problem, and thus is not considered
    a bug.  A server-side traceback is not warranted.  Unless specialized,
    this is a '400 Bad Request'
    """
    code = 400
    title = 'Bad Request'
    explanation = ('The server could not comply with the request since',
                   'it is either malformed or otherwise incorrect.')

class HTTPBadRequest(HTTPClientError):
    pass


class HTTPUnauthorized(HTTPClientError):
    code = 401
    title = 'Unauthorized'
    explanation = ('This server could not verify that you are authorized to',
                   'access the document you requested.  Either you supplied the',
                   'wrong credentials (e.g., bad password), or your browser',
                   'does not understand how to supply the credentials required.')

class HTTPPaymentRequired(HTTPClientError):
    code = 402
    title = 'Payment Required'
    explanation = 'Access was denied for financial reasons.'

class HTTPForbidden(HTTPClientError):
    code = 403
    title = 'Forbidden'
    explanation = 'Access was denied to this resource.'

class HTTPNotFound(HTTPClientError):
    code = 404
    title = 'Not Found'
    explanation = 'The resource could not be found.'

class HTTPMethodNotAllowed(HTTPClientError):
    code = 405
    title = 'Method Not Allowed'
    explanation = 'The method ${REQUEST_METHOD} is not allowed for this resource.'

class HTTPNotAcceptable(HTTPClientError):
    code = 406
    title = 'Not Acceptable'
    explanation = ('The resource could not be generated that was acceptable to your browser',
                   '(content of type ${HTTP_ACCEPT}).')

class HTTPProxyAuthenticationRequired(HTTPClientError):
    code = 407
    title = 'Proxy Authentication Required'
    explanation = 'Authentication with a local proxy is needed.'

class HTTPRequestTimeout(HTTPClientError):
    code = 408
    title = 'Request Timeout'
    explanation = 'The server has waited too long for the request to be sent by the client.'

class HTTPConflict(HTTPClientError):
    code = 409
    title = 'Conflict'
    explanation = 'There was a conflict when trying to complete your request.'

class HTTPGone(HTTPClientError):
    code = 410
    title = 'Gone'
    explanation = 'This resource is no longer available.  No forwarding address is given.'

class HTTPLengthRequired(HTTPClientError):
    code = 411
    title = 'Length Required'
    explanation = 'Content-Length header required.'

class HTTPPreconditionFailed(HTTPClientError):
    code = 412
    title = 'Precondition Failed'
    explanation = 'Request precondition failed.'

class HTTPRequestEntityTooLarge(HTTPClientError):
    code = 413
    title = 'Request Entity Too Large'
    explanation = 'The body of your request was too large for this server.'

class HTTPRequestURITooLong(HTTPClientError):
    code = 414
    title = 'Request-URI Too Long'
    explanation = 'The request URI was too long for this server.'

class HTTPUnsupportedMediaType(HTTPClientError):
    code = 415
    title = 'Unsupported Media Type'
    explanation = 'The request media type ${CONTENT_TYPE} is not supported by this server.'

class HTTPRequestRangeNotSatisfiable(HTTPClientError):
    code = 416
    title = 'Request Range Not Satisfiable'
    explanation = 'The Range requested is not available.'

class HTTPExpectationFailed(HTTPClientError):
    code = 417
    title = 'Expectation Failed'
    explanation = 'Expectation failed.'

class HTTPUnprocessableEntity(HTTPClientError):
    ## Note: from WebDAV
    code = 422
    title = 'Unprocessable Entity'
    explanation = 'Unable to process the contained instructions'

class HTTPLocked(HTTPClientError):
    ## Note: from WebDAV
    code = 423
    title = 'Locked'
    explanation = 'The resource is locked'

class HTTPFailedDependency(HTTPClientError):
    ## Note: from WebDAV
    code = 424
    title = 'Failed Dependency'
    explanation = ('The method could not be performed because the requested ',
                   'action dependended on another action and that action failed')

############################################################
## 5xx Server Error
############################################################
#  Response status codes beginning with the digit "5" indicate cases in
#  which the server is aware that it has erred or is incapable of
#  performing the request. Except when responding to a HEAD request, the
#  server SHOULD include an entity containing an explanation of the error
#  situation, and whether it is a temporary or permanent condition. User
#  agents SHOULD display any included entity to the user. These response
#  codes are applicable to any request method.

class HTTPServerError(HTTPError):
    """
    base class for the 500's, where the server is in-error

    This is an error condition in which the server is presumed to be
    in-error.  This is usually unexpected, and thus requires a traceback;
    ideally, opening a support ticket for the customer. Unless specialized,
    this is a '500 Internal Server Error'
    """
    code = 500
    title = 'Internal Server Error'
    explanation = ('The server has either erred or is incapable of performing',
                   'the requested operation.')

class HTTPInternalServerError(HTTPServerError):
    pass

class HTTPNotImplemented(HTTPServerError):
    code = 501
    title = 'Not Implemented'
    explanation = 'The request method ${REQUEST_METHOD} is not implemented for this server'

class HTTPBadGateway(HTTPServerError):
    code = 502
    title = 'Bad Gateway'
    explanation = 'Bad gateway.'

class HTTPServiceUnavailable(HTTPServerError):
    code = 503
    title = 'Service Unavailable'
    explanation = ('The server is currently unavailable.',
                   'Please try again at a later time.')

class HTTPGatewayTimeout(HTTPServerError):
    code = 504
    title = 'Gateway Timeout'
    explanation = 'The gateway has timed out.'

class HTTPVersionNotSupported(HTTPServerError):
    code = 505
    title = 'HTTP Version Not Supported'
    explanation = 'The HTTP version is not supported.'

class HTTPInsufficientStorage(HTTPServerError):
    code = 507
    title = 'Insufficient Storage'
    explanation = 'There was not enough space to save the resource'


############################################################
## Custom HTTP Exception classes
############################################################
#
#
# TODO: consider removal

class NotInitializedProperly(HTTPInternalServerError):
    pass

class InitializationError(HTTPInternalServerError):
    pass