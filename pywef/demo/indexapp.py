
__author__="pborky"
__date__ ="$18.3.2010 1:53:31$"

class Index(object):
    """ Demo application showing hello world.."""

    def __init__(self, **kwargs):
        if 'count' in kwargs:
            self.count = kwargs['count']
        else:
            self.count = 1

    def __call__(self, context, **kwargs):
        monster = 'dragon'
        who = 'world'

        if 'monster' in kwargs:
            monster = str(kwargs['monster'])

        if 'who' in kwargs:
            who = str(kwargs['who'])

        context.response.status = 200
        context.response.headers['Content-Type'] = 'text/html'
        context.response.body_file.write('''\
<h1>Hello %s!</h1>
<p>
<a href="%s">home</a>&nbsp;&nbsp;
<a href="%s">greeting</a>&nbsp;&nbsp;
<a href="%s">first</a>&nbsp;&nbsp;
previous&nbsp;&nbsp;
next
</p>
<p>Here be %d %s soon.</p>''' % (\
            who,\
            context.url_generator('index'),\
            context.url_generator('hello'),\
            context.url_generator('main',action='test',data=1), \
            self.count, \
            monster)
        )
