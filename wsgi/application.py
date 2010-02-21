__author__="pborky"
__date__ ="$18.2.2010 17:23:37$"

from wsgi import context as ctx

class Application(object):

    def __call__(self, context):
        assert(issubclass(context.__class__, ctx.Context))
        return False