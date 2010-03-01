__author__="peterb"
__date__ ="$1.3.2010 14:50:31$"

import os
from wsgi.monitor import Monitor

Monitor().start()

def test_app(context, **kwargs):
    res = context.response
    req = context.request

    res.status = 200
    res.headers['Content-Type'] = 'text/plain'

    environ = req.environ
    input = environ['wsgi.input']

    res.body_file.write('PID: %s\n' % os.getpid())
    res.body_file.write('UID: %s\n' % os.getuid())
    res.body_file.write('GID: %s\n' % os.getgid())

    res.body_file.write('\n')

    keys = environ.keys()
    keys.sort()
    for key in keys:
        res.body_file.write('%s: %s\n' % (key, repr(environ[key])))

    res.body_file.write('\n')

    res.body_file.write(input.read(int(environ.get('CONTENT_LENGTH', '0'))))
