__author__="pborky"
__date__ ="$19.2.2010 0:21:07$"

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello world!']

