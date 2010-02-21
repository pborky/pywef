__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

try:
    from wsgi import context as ctx

    class FrontController(object):

        def __init__(self, AppClass):
            self._sess = ctx.Session()
            self._app = AppClass()

        def __call__(self, environ, start_response):
            try:
                context = ctx.Context(self._sess, ctx.Request(environ), ctx.Response(start_response))

                self._app(context)

                return context.response.return_response()

            except Exception as inst:
                raise
                return ctx.Response(start_response,
                                    500,
                                    [('Content-Type', 'text/html')],
                                    [ '<h1>500 Internal Server Error</h1>',
                                      'Raised <b>',
                                      str(inst.__class__.__name__),
                                      '</b> with argument(s): <b>',
                                      str(inst),
                                      '</b>.']
                                   ).return_response()
except:
    import sys

    class FrontControllerInitFailed(object):
        """ This is fail safe front controller. It returns 500 and error details"""
        # TODO: make confirable the error output
        def __init__(self, AppClass):
            self._exc_info = sys.exc_info()

        def __call__(self, environ, start_resp):
            start_resp('500 Internal Server Error', [('Content-type', 'text/html')], self._exc_info)

            return ['<h1>500 Internal Server Error</h1>',
                    '<p>Server initialiazation failed.</p>',
                    '<code>',
                    '<p>', self._exc_info[0].__name__, ':</br> ',
                    str(self._exc_info[1]), '</p>',
                    '</code>'
                    ]
    # TODO: this should be diferent - factory class generating front controller
    FrontController = FrontControllerInitFailed