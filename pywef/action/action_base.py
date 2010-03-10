__author__="pborky"
__date__ ="$Mar 8, 2010 10:48:06 PM$"

class Action(object):
    def __init__(self, **kwargs):
        pass

    def __call__(self, context, **kwargs):
        callback = kwargs.get('callback', None)
        if callback == None:
            return self.execute(context, **kwargs)
        else:
            callback = self.__getattr__(callback)
            return callback(context, **kwargs)
    
    def execute(self, context, **kwargs):
        return None