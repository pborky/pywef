__author__="pborky"
__date__ ="$12.3.2010 1:22:45$"

from pywef import HTTPBadRequest

class TestAction(object):

    def execute(self, context):
        data = context.match_dict.get('data', 0)
        try:
            data = int(data)
        except:
            raise HTTPBadRequest('Cannot convert \'%s\' to integer.'% data, exc_info = True)

        val = data
        name =self.__class__.__name__
        title = context.match_dict.get('title', "A Dummy Thing")
        first = 1
        last = 500000
        previous = data - 1
        next = data + 1
        show = data>=first and data <= last

        urls = dict(\
            home = context.url('index'),
            first = context.url('main', action='test', data=first),
            previous = context.url('main', action='test', data=previous),
            next = context.url('main', action='test', data=next),
            last = context.url('main', action='test', data=last))

        if data == first:
            urls['first'] = None
            urls['previous'] = None
        elif data == last:
            urls['next'] = None
            urls['last'] = None
        elif not show:
            urls['previous'] = None
            urls['next'] = None

        vars = locals()
        del vars['self']
        context.data.update(vars)



