__author__="pborky"
__date__ ="$18.2.2010 16:41:24$"

from wsgi import context as ctx
from wsgi import application as appl

class FrontController(object):

    def __init__(self, AppClass):
        assert(issubclass(AppClass, appl.Application))
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
