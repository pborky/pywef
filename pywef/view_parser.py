''' based on Yet Another Python Templating Utility, Version 1.2  '''

import re
from pywef.logger import get_logger
logger = get_logger('default')

# utility stuff to avoid tests in the mainline code
class _Nevermatch:
    "Polymorphic with a regex that never matches"
    def match(self, line):
        return None
_never = _Nevermatch()     # one reusable instance of it suffices
def identity(string, why):
    "A do-nothing-special-to-the-input, just-return-it function"
    return string
def nohandle(string):
    "A do-nothing handler that just re-raises the exception"
    raise

# and now the real thing
class Parser(object):
    "Smart-copier (YAPTU) class"

    def _parse_block(self, i=0, last=None):
        "Main copy method: process lines [i,last) of block"

        out = []

        def repl(match, self=self):
            "return the eval of a found expression, for replacement"
            expr = self.preproc(match.group(1), 'eval')
            try: val = str(eval(expr, self.globals, self.locals))
            except: val = str(self.handle(expr))
            #logger.debug('Evaluating "%s" = "%s".'% (expr, val))
            return val

        block = self.locals['_bl']
        if last is None: last = len(block)
        while i<last:
            line = block[i]
            match = self.restat.match(line)
            if match:   # a statement starts "here" (at line block[i])
                # i is the last line to _not_ process
                stat = match.group(1).strip()
                j=i+1   # look for 'finish' from here onwards
                nest=1  # count nesting levels of statements
                while j<last:
                    line = block[j]
                    # first look for nested statements or 'finish' lines
                    if self.restend.match(line):    # found a statement-end
                        nest = nest - 1     # update (decrease) nesting
                        if nest==0: break   # j is first line to _not_ process
                    elif self.restat.match(line):   # found a nested statement
                        nest = nest + 1     # update (increase) nesting
                    elif nest==1:   # look for continuation only at this nesting
                        match = self.recont.match(line)
                        if match:                   # found a contin.-statement
                            nestat = match.group(1).strip()
                            stat = '%s _out+=_cb(%s,%s)\n%s' % (stat,i+1,j,nestat)
                            i=j     # again, i is the last line to _not_ process
                    j=j+1
                stat = self.preproc(stat, 'exec')
                stat = '%s _out+=_cb(%s,%s)' % (stat,i+1,j)
                stat = '_out=""\n%s' % stat
                #logger.debug('Executing "%s".'% stat)
                exec stat in self.globals,self.locals
                out.append(self.locals['_out'])
                i=j+1
            else:       # normal line, just copy with substitution
                out.append('%s\n'% self.regex.sub(repl,line))
                i=i+1
        return ''.join(out)

    def __init__(self, regex, globals, restat, restend, recont,
            preproc=identity, handle=nohandle):
        "Initialize self's attributes"
        self.regex   = regex
        self.globals = globals
        self.locals  = { '_cb':self._parse_block }
        self.restat  = restat
        self.restend = restend
        self.recont  = recont
        self.preproc = preproc
        self.handle  = handle            

    def __call__(self, input):
        self.locals['_bl'] = input
        return self._parse_block()

    @staticmethod
    def parse(input, globals, regex=None, restat=None, restend=None, recont=None, recomm=None):
        if regex==None:
            regex=re.compile(r"\<\?python\s+=(.+?)#\s*\?\>")
        if restat==None:
            restat=re.compile(r"\s*\<\?python\s([^%].+?(#\s*)?)\?\>")
        if recont==None:
            recont=re.compile(r"\s*\<\?python\s+%(.+?)(#\s*)?\?\>")
        if restend==None:
            restend=re.compile(r"\s*\<\?python\s+#\s*\?\>")
        if recomm==None:
            recomm=re.compile(r"\s*\<\?--\s*(.*?)\s*--\?\>")

        parser = Parser(regex, globals, restat, restend, recont)
        return parser(input)

def test(input=None, globals={}):
    "Test: copy a block of lines, with full processing"
    
    rex=re.compile(r"<%=\s*([^>]+)\s*/>")
    rbe=re.compile(r"<%%\s*(.+)\s*>")
    rco=re.compile(r"<%.\s*(.+)\s*>")
    ren=re.compile(r"</%%>")
    cop = Parser(rex, globals, rbe, ren, rco)
    if input == None:
        input = """
A first, plain line -- it just gets copied.
A second line, with <%=x/> substitutions.
<%% x+=1   # non-block statements MUST end with comments>
</%%>
Now the substitutions are <%=x/>.
<%% if x>23:>
After all, <%=x/> is rather large!
<%. else:>
After all, <%=x/> is rather small!
</%%>
<%% for i in range(3):>
  Also, <%=i/> times <%=x/> is <%=i*x/>.
</%%>
One last, plain line at the end."""

    lines_block = [line+'\n' for line in input.split('\n')]
    print "*** input:"
    print ''.join(lines_block)
    print "*** output:"
    cop.copy(lines_block)
