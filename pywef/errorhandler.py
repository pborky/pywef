__author__="pborky"
__date__ ="$22.2.2010 0:52:47$"

import sys
import os
import linecache

class ExcInfo(object):
    """ Encapslation of exc_info() tuple. """
    
    def __init__(self):
        (cls, exc, tb) = sys.exc_info()
        self._info = {'cls':cls, 'exc':exc, 'tb':tb}
        self._log_it()

    def __iter__(self):
        return self._info.__iter__()

    def __call__(self, start_resp, debug = False, show_debug_code = True):
        start_resp('500 Internal Server Error', [('Content-type', 'text/html')], self.tuple)
        return [''.join(self._get_resp_body(debug, show_debug_code))]

    def __getitem__(self, key):
        if (isinstance(key, int)):
            return self._info[self._info.keys()[key]]
        else:
            return self._info[key]

    def _log_it(self):
        prefix = '[%s (pid=%d)]:' % (self.__class__.__name__ ,os.getpid())
        print >> sys.stderr, '%s Handling exception: %s' % (prefix, self._get_traceback())

    def _get_tuple(self):
        return tuple(self)
    tuple = property(_get_tuple, doc = _get_tuple.__doc__)

    def _get_cls(self):
        return self._info['cls']
    cls = property(_get_cls, doc = _get_cls.__doc__)

    def _get_exc(self):
        return self._info['exc']
    exc = property(_get_exc, doc = _get_exc.__doc__)

    def _get_tb(self):
        return self._info['tb']
    tb = property(_get_tb, doc = _get_tb.__doc__)

    def _get_detail(self):
        exc_val = self.exc
        if (len(exc_val.args) >= 1):
            return str(exc_val.args[0])
        else:
            return ''
    detail = property(_get_detail, _get_detail.__doc__)

    def _get_typename(self):
        return self.cls.__name__
    typename = property(_get_typename, _get_typename.__doc__)

    def _get_nested(self):
        args = self.exc.args
        list = []
        if (len(args)>1):
            for i in args:
                if (isinstance(i,ExcInfo)):
                    list.append(i)
        return list
    nested = property(_get_nested, _get_nested.__doc__)

    def _get_resp_body(self, debug, show_debug_code):
        list = []
        list.append('<h1>500 Internal Server Error</h1>\n'
                    '<p>The server has either erred or is incapable of performing\n'
                    'the requested operation.\n</p>')
        if debug:
            list.append(self._format_tb_html(show_debug_code))
        else:
            list.append('<code><b>%s: %s</b></code>' % (self.typename, self.detail))
        return list

    def _get_traceback(self):
        exc_type = self.typename
        exc_tb = _extract_tb(self.tb)  # [(filename, lineno, name, line)...]
        exc_str = self.detail

        list = []
        list.append('\n  %s: %s\n    Traceback:\n' % (exc_type, exc_str))

        exc_tb.reverse()

        for filename, lineno, name, line in exc_tb:
            if name is not None or name != '':
                list.append('      File "%s, line %d, in "%s"\n' % (filename, lineno, name.replace('<','&lt;').replace('>','&gt;')))
            else:
                list.append('      File "%s, line %d\n' % (filename, lineno))

            if (line):
                list.append('         [%s]\n' % line.strip())

        for i in self.nested:
            list.append('  %s`s root cause:' % exc_type)
            list.append(i._get_traceback())

        return ''.join(list)

    def _format_tb_html(self, show_debug_code):
        exc_type = self.typename
        exc_tb = _extract_tb(self.tb)  # [(filename, lineno, name, line)...]
        exc_str = self.detail

        list = []
        list.append('<p><code><b>%s: %s</b><br/>Traceback:<br/>' % (exc_type, exc_str))

        exc_tb.reverse()
        
        for filename, lineno, name, line in exc_tb:
            if name is not None or name != '':
                list.append('File "<b><font color="blue">%s</font></b>, line <b>%d</b>, in "<b>%s</b>"<br/>' % (filename, lineno, name.replace('<','&lt;').replace('>','&gt;')))
            else:
                list.append('File "<b><font color="blue">%s</font></b>, line <b>%d</b><br/>' % (filename, lineno))

            if (show_debug_code and line):
                list.append('&nbsp;&nbsp;&nbsp;[<font color="red">%s</font>]<br/>' % line.strip())

        list.append('</code></p>')
        
        for i in self.nested:
            list.append('<p><code><b>%s</b></code>`s root cause:</p>' % exc_type)
            list.extend(i._format_tb_html(show_debug_code))

        return ''.join(list)

def _extract_tb(tb):
    list = []
    while tb is not None:
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line: line = line.strip()
        else: line = None
        list.append((filename, lineno, name, line))
        tb = tb.tb_next
    return list
