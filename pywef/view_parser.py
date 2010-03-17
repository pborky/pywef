'''
Grammar:

<blocks> ::= <block> | <block> <blocks>
<block> ::= <special-block> | <plain-block>
<special-block> ::= <opening-bracket> <code-block> <closing-bracket>

<code-block> ::= <expression-block> | <enclosed-statement-block> | <unenclosed-statement-block> | <enclosure-block>

<expression-block> ::= <opt-whitespace> <evaluator> <python-expression> <enclosure> <opt-whitespace>
<enclosed-statement-block> ::= <whitespace> <python-statements> <enclosure> <opt-whitespace>
<unenclosed-statement-block> ::= <whitespace> <python-statements>
<enclosure-block> ::= <opt-whitespace> <enclosure> <opt-whitespace>

<opt-whitespace> ::= <whitespace> <opt-whitespace> | <empty-string>

<opening-bracket> ::= '<?python'
<closing-bracket> ::= '?>'
<whitespace> ::= " " | "\t" | "\r" | "\r\n" | "\n"   <!-- white space character, e.g. space, tab, ..  -->
<empty-string> ::= "" <!-- "" is empty string, i.e. no whitespace -->
<enclosure> ::= '#'
<evaluator> ::= '='

<python-expression> ::= <!-- see python guide (will be passed to eval()) -->
<python-statements> ::= <!-- see python guide (will be passed to exec ) -->


Input:
<h1>Test</h1>
<?python if a < b: ?>
    <?python c = b - a #?>
    a is less than b.<br/>
    c = <?python= c #?> <br/>
    <?python for i in range(a, b):?>
        i = <?python= i #?><br/>
    <?python # ?>
<?python # ?>
<?python else: ?>
    <?python for i in range(b,a):?>
        <?python= 'i = %d<br/>' % i #?>
    <?python # ?>
<?python # ?>

Output:
out.write('<h1>Test</h1>')
if a < b:
    c = b - a
    out.write('a is less than b.<br/>\n    c = ')
    out.write('%s' % c)
    out.write(' <br/>')
    for i in range(a, b):
        out.write('i = ')
        out.write('%s' % i)
        out.write('<br/>')
else:
    for i in range(b, a):
        out.write('%s' % 'i = %d<br/>' % i)
'''

__author__="peterb"
__date__ ="$16.3.2010 13:26:21$"


__all__=('TokenStream',)

class TokenType(object):

    def __init__(self, name, pattern, composite = None):
        import re
        self._name = name
        self._pattern = pattern
        self._composite = composite
        self._regex = None
        
    def __str__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

    def __repr__(self):
        return '<%s.%s> pattern:"%s"' % (self.__class__.__name__, self.name, self.pattern)

    def __get_name(self):
        ''' TokenType name '''
        return self._name
    name = property(__get_name, doc=__get_name.__doc__)

    def __get_pattern(self):
        ''' Matcher pattern'''
        return self._pattern
    pattern = property(__get_pattern, doc=__get_pattern.__doc__)

    def __get_regex(self):
        ''' Regular expresion created from pattern '''
        if self._regex == None:
            if self._pattern is not None:
                self._regex = re.compile(self._pattern)
        return self._regex
    regex = property(__get_regex, doc=__get_regex.__doc__)

    def __get_composite(self):
        '''  '''
        return self._composite
    composite = property(__get_composite, doc=__get_composite.__doc__)

class Token(object):
    
    _UNKNOWN = TokenType('unknown', None)
    
    def __init__(self, type = _UNKNOWN, value = None):
        self._type = type
        self._value = value

    def __str__(self):
        return '<%s.%s> value: "%s"' % (self.__class__.__name__, self.type, self.value)

    def __repr__(self):
        return '<%s.%s> value: "%s"' % (self.__class__.__name__, self.type, self.value)

    def _get_type(self):
        return self._type
    type = property(_get_type, doc=_get_type.__doc__)

    def _get_value(self):
        return self._value
    value = property(_get_value, doc=_get_value.__doc__)


class TokenStream(object):
    '''
    TokenStream is a lexer class converting string to stream of Token objects.
    Lexical analysis is performed by matching patterns given by iterable of TokenType objects.
    Lexer goes thru string and trying to match given patterns (classes) first match wins and Token object
    is yielded while 'consuming' match length from input string. Pattern is any regular expression. The
    length of match is consumed from string, and if exists group(1) is yielded as token.
    i.e.
    Having a = TokenType('A', r"(A).*") as pattern returns Token(a, 'A') for all input strings starting with A
    and not matched by other rules. The matcher is moved to the last matched position (line end or end of string
    in this case)
    '''

    def __init__(self, data, lexical_classes):
        if isinstance(data, str):
            self._data = ''.join(data)
        else:
            self._data = ''.join(['%s\n'%i for i in data])
        self._pos = 0
        self._lexical_classes = lexical_classes
        self._token_stack = []

    def __iter__(self):
        return self._generator()

    def push_token(self, token):
        if not isinstance(token, Token):
            raise TypeError('Argument \'token\' must be instance of \'Token\'.')
        self._token_stack.append(token)

    def _generator(self):
        pos = 0
        while not ((len(self._data) <= 0) or (pos >= len(self._data))):
            if len(self._token_stack) > 0:
                yield self._token_stack.pop()
            matched = False
            for token_type in self._lexical_classes:
                if token_type.regex is None:
                    raise Exception('Given \'TokenType\' cannot be used as matcher.')
                match = token_type.regex.match(self._data, pos)
                if match is not None:
                    matched = True
                    token_str = match.group(0)
                    offset = len(token_str)
                    if len(match.groups()) > 0:
                        token_str = match.group(1)
                    break
            if matched:
                pos = pos + offset
                yield Token(token_type, token_str)



comment = TokenType('<comment>', r"\<\?--\s*(.*?)\s*--\?\>")
beginsymbol = TokenType('<beginsymb>', r"(\<\?python)(?=[\s=#])")
endsymbol = TokenType('<endsymb>', r"(\?\>)")
evaluate = TokenType('<evaluate>', r"(=)")
enclose = TokenType('<enclose>', r"(#)")
whitespace = TokenType('<whitespace>', r"([ \t]+)")
lineend = TokenType('<lineend>', r"(\r\n|[\n\r])")
string = TokenType('<string>', r"([\"'].*?[\"'])")
number = TokenType('<number>', r"(\d+)")
identifier = TokenType('<identifier>', r"(\w([\w\d])*)")
others = TokenType('<others>', r".")

lexer_classes = (comment, beginsymbol, endsymbol, evaluate, enclose, whitespace, lineend, string, number, identifier, others)


def test(data = None):
    if data is None:
        data = '''\
this is test<br/>
<?python for i in range(1,10): ?> i=<?python=i#?> <?-- this is comment --?>
    <a href=something
    \talt="test">
<?python#          
?>
</a> test'''
    for i in TokenStream(data, lexer_classes): print str(i)

def something():
    print 'something fd  '