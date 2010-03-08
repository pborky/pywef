"""
This module overrides exception handling in webob.exc package.

List of HTTP statuses and webob exceptions:
Exception
  HTTPException
    HTTPOk (allways must be catched and processed normally)
      * 200 - HTTPOk
      * 201 - HTTPCreated
      * 202 - HTTPAccepted
      * 203 - HTTPNonAuthoritativeInformation
      * 204 - HTTPNoContent
      * 205 - HTTPResetContent
      * 206 - HTTPPartialContent
    HTTPRedirection
      * 300 - HTTPMultipleChoices
      * 301 - HTTPMovedPermanently
      * 302 - HTTPFound
      * 303 - HTTPSeeOther
      * 304 - HTTPNotModified
      * 305 - HTTPUseProxy
      * 306 - Unused (not implemented, obviously)
      * 307 - HTTPTemporaryRedirect
    HTTPError
      HTTPClientError
        * 400 - HTTPBadRequest
        * 401 - HTTPUnauthorized
        * 402 - HTTPPaymentRequired
        * 403 - HTTPForbidden
        * 404 - HTTPNotFound
        * 405 - HTTPMethodNotAllowed
        * 406 - HTTPNotAcceptable
        * 407 - HTTPProxyAuthenticationRequired
        * 408 - HTTPRequestTimeout
        * 409 - HTTPConflict
        * 410 - HTTPGone
        * 411 - HTTPLengthRequired
        * 412 - HTTPPreconditionFailed
        * 413 - HTTPRequestEntityTooLarge
        * 414 - HTTPRequestURITooLong
        * 415 - HTTPUnsupportedMediaType
        * 416 - HTTPRequestRangeNotSatisfiable
        * 417 - HTTPExpectationFailed
      HTTPServerError
        * 500 - HTTPInternalServerError
        * 501 - HTTPNotImplemented
        * 502 - HTTPBadGateway
        * 503 - HTTPServiceUnavailable
        * 504 - HTTPGatewayTimeout
        * 505 - HTTPVersionNotSupported

References:

.. [1] http://www.python.org/peps/pep-0333.html#error-handling
.. [2] http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5

"""

__author__="pborky"
__date__ ="$Mar 8, 2010 5:46:06 AM$"

import wrap_exc
import sys
from webob.headerdict import HeaderDict

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

    def __init__(self, detail=None, exc_info=None, headerlist=None, comment=None, **kargs):

        if exc_info is not None:
            if not isinstance(exc_info, wrap_exc.ExcInfoWrapper):
                exc_info = wrap_exc.ExcInfoWrapper(exc_info)
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
    explanation = ('The request is accepted for processing.',)

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
    explanation = ('Access was denied for financial reasons.',)

class HTTPForbidden(HTTPClientError):
    code = 403
    title = 'Forbidden'
    explanation = ('Access was denied to this resource.',)

class HTTPNotFound(HTTPClientError):
    code = 404
    title = 'Not Found'
    explanation = ('The resource could not be found.',)

class HTTPMethodNotAllowed(HTTPClientError):
    code = 405
    title = 'Method Not Allowed'
    explanation = ('The method ${REQUEST_METHOD} is not allowed for this resource.',)

class HTTPNotAcceptable(HTTPClientError):
    code = 406
    title = 'Not Acceptable'
    explanation = ('The resource could not be generated that was acceptable to your browser',
                   '(content of type ${HTTP_ACCEPT}).')

class HTTPProxyAuthenticationRequired(HTTPClientError):
    code = 407
    title = 'Proxy Authentication Required'
    explanation = ('Authentication with a local proxy is needed.',)

class HTTPRequestTimeout(HTTPClientError):
    code = 408
    title = 'Request Timeout'
    explanation = ('The server has waited too long for the request to be sent by the client.',)

class HTTPConflict(HTTPClientError):
    code = 409
    title = 'Conflict'
    explanation = ('There was a conflict when trying to complete your request.',)

class HTTPGone(HTTPClientError):
    code = 410
    title = 'Gone'
    explanation = ('This resource is no longer available.  No forwarding address is given.',)

class HTTPLengthRequired(HTTPClientError):
    code = 411
    title = 'Length Required'
    explanation = ('Content-Length header required.',)

class HTTPPreconditionFailed(HTTPClientError):
    code = 412
    title = 'Precondition Failed'
    explanation = ('Request precondition failed.',)

class HTTPRequestEntityTooLarge(HTTPClientError):
    code = 413
    title = 'Request Entity Too Large'
    explanation = ('The body of your request was too large for this server.',)

class HTTPRequestURITooLong(HTTPClientError):
    code = 414
    title = 'Request-URI Too Long'
    explanation = ('The request URI was too long for this server.',)

class HTTPUnsupportedMediaType(HTTPClientError):
    code = 415
    title = 'Unsupported Media Type'
    explanation = ('The request media type ${CONTENT_TYPE} is not supported by this server.',)

class HTTPRequestRangeNotSatisfiable(HTTPClientError):
    code = 416
    title = 'Request Range Not Satisfiable'
    explanation = ('The Range requested is not available.',)

class HTTPExpectationFailed(HTTPClientError):
    code = 417
    title = 'Expectation Failed'
    explanation = ('Expectation failed.',)

class HTTPUnprocessableEntity(HTTPClientError):
    ## Note: from WebDAV
    code = 422
    title = 'Unprocessable Entity'
    explanation = ('Unable to process the contained instructions',)

class HTTPLocked(HTTPClientError):
    ## Note: from WebDAV
    code = 423
    title = 'Locked'
    explanation = ('The resource is locked',)

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
    explanation = ('The request method ${REQUEST_METHOD} is not implemented for this server')

class HTTPBadGateway(HTTPServerError):
    code = 502
    title = 'Bad Gateway'
    explanation = ('Bad gateway.')

class HTTPServiceUnavailable(HTTPServerError):
    code = 503
    title = 'Service Unavailable'
    explanation = ('The server is currently unavailable.',
                   'Please try again at a later time.')

class HTTPGatewayTimeout(HTTPServerError):
    code = 504
    title = 'Gateway Timeout'
    explanation = ('The gateway has timed out.')

class HTTPVersionNotSupported(HTTPServerError):
    code = 505
    title = 'HTTP Version Not Supported'
    explanation = ('The HTTP version is not supported.')

class HTTPInsufficientStorage(HTTPServerError):
    code = 507
    title = 'Insufficient Storage'
    explanation = ('There was not enough space to save the resource')
