""" """
__author__="pborky"
__date__ ="$Mar 8, 2010 5:50:24 AM$"

import urlparse
import sys
try:
    from string import Template
except ImportError:
    from webob.util.stringtemplate import Template
from webob import Response, Request, html_escape
from traceback import extract_tb
from pywef.logger import get_logger
import http_exc

logger = get_logger('pywef')

def no_escape(value):
    if value is None:
        return ''
    if not isinstance(value, basestring):
        if hasattr(value, '__unicode__'):
            value = unicode(value)
        else:
            value = str(value)
    return value

class ExcInfoWrapper(object):
    ''' Wrapper around sys.exc_info().  '''

    plain_template = Template('''\
${status}
${explanation}

${exception}: ${detail}
${_traceback}''')
    plain_tb = Template('''\
  Traceback:
${_items}

${_nested}''')
    plain_tb_item = Template('''\
    File "${filename}, line ${lineno}, in "${name}"
''')
    plain_tb_item_code = Template('''\
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
    html_tb = Template('''\
<p><code>Traceback:</code><br/>
${_items}
${_nested}''')
    html_tb_item = Template('''\
<code>
File "<b><font color="blue">${filename}</font></b>,
line <b>${lineno}</b>,
in "<b>${name}</b>"</code><br/>''')
    html_tb_item_code = Template('''\
<code>&nbsp;&nbsp;&nbsp;[<font color="red">${line}</font>]</code><br/>''')
    html_tb_nested = Template('''\
<p><code><b>${exception}</b></code>`s root cause:</p>
<p><code><b>${nest_exception}: ${nest_detail}</b></code></p>
${_nest_traceback}''')

    _templates = {
        'html' : {
            'escape' : html_escape,
            'template' : html_template,
            'traceback' : {
                'template' : html_tb,
                'item' : html_tb_item,
                'code' : html_tb_item_code,
                'nested' : html_tb_nested } },
        'plain' : {
            'escape' : no_escape,
            'template' : plain_template,
            'traceback' : {
                'template' : plain_tb,
                'item' : plain_tb_item,
                'code' : plain_tb_item_code,
                'nested' : plain_tb_nested } } }

    def __init__(self, exc_info = None):
        if exc_info == None:
            (cls, exc, tb) = sys.exc_info()
        else:
            (cls, exc, tb) = exc_info
        self._exc_info = {'cls':cls, 'exc':exc, 'tb':tb}
        logger.warning('%s: %s' % (self.typename, self.detail))

    def __iter__(self):
        return self._exc_info.__iter__()

    def __getitem__(self, key):
        if (isinstance(key, int)):
            return self._exc_info[self._exc_info.keys()[key]]
        else:
            return self._exc_info[key]

    def __call__(self, environ, start_resp, debug):
        logger.critical('%s: %s' % (self.typename, self.detail))
        
        exc = self.exc
        if not issubclass(exc.__class__, http_exc.HTTPException):
            exc = http_exc.HTTPInternalServerError()
        
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

        def repl_start_response(status, headers, exc=None):
            if exc==None:
                exc = self.tuple
            return start_resp(status, headers, exc)

        return self._generate_response(environ, repl_start_response, debug,
                        exc.status, exc.explanation, location, exc.headerlist)

    def _generate_response(self, environ, start_response, debug,  status,
                        explanation, location, headerlist):

        if not isinstance(debug, int):
            if debug:
                debug = 2
            else:
                debug = 0
        assert debug in (0,1,2)

        accept = environ.get('HTTP_ACCEPT', '')
        if accept and 'html' in accept or '*/*' in accept:
            content_type = 'text/html'
            temp = self._templates['html']
        else:
            content_type = 'text/plain'
            temp = self._templates['plain']
        body=self._get_body(environ, temp, debug, status, explanation, location, headerlist)
        resp = Response(\
            body=body,
            status=status,
            headerlist=headerlist,
            content_type=content_type,
            location=location
        )
        return resp(environ, start_response)

    def _get_body(self, environ, temp, debug, status, explanation, location, headerlist):
        escape = temp['escape']
        template = temp['template']
        traceback = temp['traceback']

        args = {
            'status' : escape(status),
            'exception' : self.typename,
            'detail': self.detail,
        }

        if location == None:
            args['location'] = ''
        else:
            args['location'] = Template('<a href="${location}">${location}</a>').substitute(location=escape(location))

        for k, v in environ.items():
            args[k] = escape(v)
        for k, v in headerlist:
            args[k.lower()] = escape(v)
        t = Template(''.join(explanation))
        args['explanation'] = t.substitute(args)
        if debug == 0:
            args['_traceback'] = ''
        else:
            args['_traceback'] = self._get_traceback(traceback, escape, debug)

        return template.substitute(args)

    def _get_traceback(self, temp, escape, debug):

        template = temp['template']
        item_template = temp['item']
        code_template = temp['code']
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
            if ((debug == 2) and line):
                items.append(code_template.substitute(args))

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
        return tuple(self)
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