__author__="pborky"
__date__ ="$Mar 8, 2010 10:45:11 PM$"

import os
import os.path
#######
# pywef
from logger import get_logger
from exc import HTTPBadRequest, HTTPInternalServerError, NotInitializedProperly

log = get_logger('pywef.action')

class TemplateFile(object):
    ''' Helper class for handling teplates. '''

    def __init__(self, filename, parser_cls):
        if not (os.path.exists(filename) or os.access(filename, 'r')):
            raise IOError('File \'%s\' does not exist or wrong permissions.' % filename)
        self._filename = filename
        self._lines = None
        self._parser = None
        self._parser_cls = parser_cls

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

    def _get_parser(self):
        ''' Return template object. '''
        if self._parser is None:
            self._parser = self._parser_cls(self.content)
        return self._parser
    parser = property(_get_parser, doc=_get_parser.__doc__)

class ActionController(object):
    ''' '''

    def __init__(self, actions, templates, templates_dir, parser_cls, **kwargs):
        self._actions = {}
        self._templates = {}

        for (key, template) in templates.items():
            self._templates[key] = TemplateFile(os.path.join(templates_dir, template), parser_cls)

        for (key, action) in actions.items():
            (action, template) = action
            try:
                template = self._templates[template]
            except KeyError:
                raise NotInitializedProperly('Template \'%s\' not defined.' % template, exc_info = True)
            self._actions[key] = (action(**kwargs), template)

        default_action = kwargs.get('default_action', None)
        if not default_action == None:
            if not self._actions.has_key(default_action):
                raise TypeError('Argument \'default_action\' must be key of \'actions\' dictionary.')
            self._action=self._actions[default_action]
        else:
            self._action=None

    def __call__(self, context):
        action = context.match_dict.get('action', None)
        
        if action is None:
            action = self._action
        else:
            action = self._actions.get(action, self._action)
        
        if action is None:
            raise HTTPBadRequest('Appropiate action was not found.')

        (action, template) =  action
        
        executor =context.request.params.get('callback', context.match_dict.get('callback', 'execute') )
        try:
            executor = action.__getattribute__(executor) # TODO: check if callable
        except AttributeError:
            raise HTTPInternalServerError('Action %s is not providing proper executor.' % action.__class__, exc_info = True)

        executor(context)
        
        stream = template.parser.generate(**context.data)
        
        context.response.body = stream.render()
