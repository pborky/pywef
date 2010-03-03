__author__="pborky"
__date__ ="$2.3.2010 0:41:31$"

class Hello(object):
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
        context.response.headers['Content-Type'] = 'text/plain'
        context.response.body_file.write('Hello %s!\nHere be %d %s soon.' % (who, self.count, monster))

