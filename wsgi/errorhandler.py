__author__="pborky"
__date__ ="$22.2.2010 0:52:47$"

import sys
import linecache
from types import TracebackType

class ExcInfo(object):
    def __init__(self):
        (cls, exc, tb) = sys.exc_info()
        self._info = {'cls':cls, 'exc':exc, 'tb':tb}

    def __iter__(self):
        return self._info.__iter__()

    def get_cls(self):
        return self._info['cls']
    cls = property(get_cls, doc = get_cls.__doc__)

    def get_exc(self):
        return self._info['exc']
    exc = property(get_exc, doc = get_exc.__doc__)

    def get_tb(self):
        return self._info['tb']
    tb = property(get_tb, doc = get_tb.__doc__)

class ErrHandle(object):

    @staticmethod
    def format_exc(exc_info, show_debug_code):
        assert(isinstance(exc_info, ExcInfo))

        ret_iterable = []
        ret_iterable.extend(['<h1>500 Internal Server Error</h1><p>The server encountered an unexpected error.</p>'])

        ret_iterable.extend(ErrHandle.format_tb(exc_info, show_debug_code))

        return ret_iterable

    @staticmethod
    def format_tb(exc_info, show_debug_code):
        assert(isinstance(exc_info, ExcInfo))
        exc_val = exc_info.exc
        exc_type = exc_info.cls.__name__
        exc_tb = ErrHandle.extract_tb(exc_info.tb)  # [(filename, lineno, name, line)...]

        if (len(exc_val.args) > 1):
            exc_str = str(exc_val.args[0])
        else:
            exc_str = str(exc_val)

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

        if (len(exc_val.args)>1):
            # TODO: how to detect sys.exc_info tuple? Do I make an wrapper? Better than this crap..
            for i in exc_val.args:
                if (isinstance(i,ExcInfo)):
                    list.append('<p><code><b>%s</b></code>`s root cause:</p>' % exc_type)
                    list.extend(ErrHandle.format_tb(i, show_debug_code))

        return [''.join(list)]

    @staticmethod
    def extract_tb(tb):
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
