__author__="pborky"
__date__ ="$Mar 8, 2010 10:45:11 PM$"

from action_base import Action
from pywef.exc import HTTPBadRequest

class ActionController(object):
    """ """

    def __init__(self, actions, **kwargs):
        self._actions = {}

        for key, action in actions.items():
            if not issubclass(action, Action):
                raise TypeError('Argument \'action_list\' must be dictionary of \'Action\' subclasses.')
            self._actions[key] = action(**kwargs)

        default_action = kwargs.get('default_action', None)
        if not default_action == None:
            if not self._actions.has_key(default_action):
                raise TypeError('Argument \'default_action\' must be key of \'actions\' dictionary.')
            self._action=self._actions[default_action]
        else:
            self._action=None


    def __call__(self, context, **kwargs):
        action = kwargs.get('action', None)
        if action == None:
            action = self._action
        else:
            action = self._actions.get(action, self._action)

        if action == None:
            raise HTTPBadRequest('The action was not specified.')

        return action(context, **kwargs)
