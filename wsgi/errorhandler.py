__author__="pborky"
__date__ ="$22.2.2010 0:52:47$"

import linecache
from types import TracebackType

class ErrHandle:

    @staticmethod
    def format_exc(exc_info, lines = True):

        ret_iterable = []
        ret_iterable.extend(['<h1>500 Internal Server Error</h1><p>Server encountered an unexpected error.</p>'])

        ret_iterable.extend(ErrHandle.format_tb(exc_info, lines))

        return ret_iterable

    @staticmethod
    def format_tb(exc_info, lines = True):        
        exc_val = exc_info[1]
        exc_type = exc_info[0].__name__
        exc_tb = ErrHandle.extract_tb(exc_info[2])  # [(filename, lineno, name, line)...]

        if (len(exc_val.args) > 1):
            exc_str = str(exc_val.args[0])
        else:
            exc_str = str(exc_val)

        list = []
        list.extend(['<p><code><b>',exc_type, ': ', exc_str, '</b><br/>Traceback:<br/>'])

        exc_tb.reverse()
        
        for filename, lineno, name, line in exc_tb:
            list.append('File "<b><a target="_blank" href="file://%s">%s</a></b>, line <b>%d</b>, in "<b>%s</b>"<br/>' % (filename, filename, lineno, name))
            if (lines and line):
                list.append('&nbsp;&nbsp;&nbsp;[<font color="red">%s</font>]<br/>' % line.strip())

        list.extend(['</code></p>'])

        if (len(exc_val.args)>1):
            # TODO: how to detect sys.exc_info tuple?
            for i in exc_val.args:
                if (isinstance(i,tuple)
                        and len(i) == 3
                        and issubclass(i[0], Exception)
                        and issubclass(i[1].__class__, Exception)
                        and isinstance(i[2], TracebackType)):
                    list.append('<p><code><b>%s</b></code>`s root cause:</p>' % exc_type)
                    list.extend(ErrHandle.format_tb(i, lines))

        return list

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
