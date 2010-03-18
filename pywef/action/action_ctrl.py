__author__="pborky"
__date__ ="$Mar 8, 2010 10:45:11 PM$"

from view_parser import Parser
from pywef.exc import HTTPBadRequest
import os
import os.path

class Template(object):
    ''' Helper class for handling teplates. '''

    def __init__(self, filename):
        if not (os.path.exists(filename) or os.access(filename, 'r')):
            raise IOError('File \'%s\' does not exist or wrong permissions.' % filename)
        self._filename = filename
        self._lines = None

    def __repr__(self):
        return '<%s> [%s]' % (self.__class__.__name__, self._filename)

    def __iter__(self):
        if self._lines is None:
            self._read_file()
        return self._lines.__iter__()

    def __getitem__(self, key):
        if self._lines is None:
            self._read_file()
        return self._lines.__getitem__(key)

    def __len__(self):
        if self._lines is None:
            self._read_file()
        return self._lines.__len__()

    def _read_file(self):
        ''' Reads whole file. '''
        f = open(self._filename, 'r')
        self._lines = f.readlines()
        f.close()

    def _get_lines(self):
        ''' Returns content of file as a list of lines. '''
        if self._lines is None:
            self._read_file()
        return self._lines.copy()
    lines = property(_get_lines, doc=_get_lines.__doc__)

    def _get_content(self):
        ''' Returns content of file as a single string. '''
        if self._lines is None:
            self._read_file()
        return ''.join(self._lines)
    content = property(_get_content, doc=_get_content.__doc__)


class ActionController(object):
    ''' '''

    def __init__(self, actions, templates, templates_dir, **kwargs):
        self._actions = {}
        self._templates = {}

        for (key, template) in templates.items():
            template_name = '%s/%s' % (templates_dir, template)
            self._templates[key] = Template(template_name)

        for (key, action) in actions.items():
            (action, template) = action
            template = self._templates[template]
            self._actions[key] = (action(**kwargs), template)

        default_action = kwargs.get('default_action', None)
        if not default_action == None:
            if not self._actions.has_key(default_action):
                raise TypeError('Argument \'default_action\' must be key of \'actions\' dictionary.')
            self._action=self._actions[default_action]
        else:
            self._action=None

    def __call__(self, context, **kwargs):
        action = kwargs.get('action', None)
        
        if action is None:
            action = self._action
        else:
            action = self._actions.get(action, self._action)
        
        if action is None:
            raise HTTPBadRequest('Appropiate action was not found.')

        (action, template) =  action

        context.action_data = {}
        
        params =context.request.params
        callback = None
        if params.has_key('callback'):
            callback = params.getone('callback')
        elif kwargs.has_key('callback'):
            callback = kwargs.get('callback')

        if callback == None:
            action.execute(context, **kwargs)
        else:
            try:
                callback = action.__getattribute__(callback)
            except AttributeError:
                callback = action.execute
            callback(context, **kwargs)

        globals = context.action_data.copy()
        globals['context'] = context
        globals['request'] = context.request
        globals['url_generator'] = context.url_generator
        
        context.response.body = Parser.parse(template, globals)
