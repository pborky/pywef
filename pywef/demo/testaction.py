__author__="pborky"
__date__ ="$12.3.2010 1:22:45$"

from pywef import HTTPBadRequest, ExcInfoWrapper

class TestAction(object):

    def execute(self, context, **kwargs):
        data = kwargs.get('data', 0)
        try:
            data = int(data)
        except:
            raise HTTPBadRequest('Cannot convert \'%s\' to integer.'% data, exc_info=ExcInfoWrapper())

        context.action_data['val'] = data
        context.action_data['name'] = self.__class__.__name__