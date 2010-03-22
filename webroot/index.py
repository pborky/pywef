__author__="pborky"
__date__ ="$19.2.2010 0:21:07$"

from pywef import FrontController, ActionController
from pywef.demo.testaction import TestAction
from genshi.template import MarkupTemplate

SERVER_SETUP = {
    'debug': True,

    'loggers': {
        'pywef':{
            'file': {
                'name':'/tmp/pywef/log/pywef_app.log',
                'size':5000000,
                'count':5 } } },

    'monitor': {
        'force_restart': True,
        'track_files': ( '/tmp/test', '/home/peterb/workspace/python/wsgi/src/templates') },

    'exc_wrapper': {
        'call': True,
        'init': True },

    'controllers': {
        'index': {
            'ctrl': ActionController,
            'ctrl_vars': {
                'actions': {
                    'test': (TestAction, 'test_template') },
                'templates_dir': '/home/peterb/workspace/python/wsgi/src/templates',
                'templates': {
                    'test_template': 'testview.xml' },
                'parser_cls': MarkupTemplate } ,
            'route': '/',
            'route_vars': {
                'action': 'test',
                'callback': 'execute',
                'data': 0,
                'title': 'Hello World!'} },
        'main': {
            'ctrl': ActionController,
            'ctrl_vars': {
                'actions': {
                    'test': (TestAction, 'test_template') },
                'templates_dir': '/home/peterb/workspace/python/wsgi/src/templates',
                'templates': {
                    'test_template': 'testview.xml' },
                'parser_cls': MarkupTemplate } ,
            'route': '/do/test/{data}',
            'route_vars': {
                'action': 'test',
                'callback': 'execute'} } } }

application = FrontController(**SERVER_SETUP)

# alternative configuration file
#[server]
#debug = True
#
#loggers.default.file.name = '/tmp/pywef/log/pywef_app.log'
#loggers.default.file.size = 50000000
#loggers.default.file.count = 5
#
#monitor.logger = 'default'
#monitor.force_restart = True
#monitor.track_files = '/tmp/test','/home/pborky/Projects/python/pywef/src/templates/'
#
#exc_wrapper.logger = 'default'
#exc_wrapper.call = True
#exc_wrapper.init = True
#
#controllers.index.ctrl = 'pywef.demo.helloapp.Index'
#controllers.index.ctrl_vars.count = 25
#controllers.index.route = '/'
#controllers.index.route_vars.who = 'World'
#controllers.index.route_vars.monster = 'dragons'
#
#controllers.hello.ctrl = 'pywef.demo.helloapp.Hello'
#controllers.hello.route = '/'
#
#controllers.main.ctrl = 'pywef.ActionController'
#controllers.main.ctrl_vars.actions.test = 'pywef.demo.testaction.TestAction'
#controllers.main.ctrl_vars.templates.test = 'testview.html'
#controllers.main.ctrl_vars.templates_dir = '/home/pborky/Projects/python/pywef/src/templates'
#controllers.main.route = '/do/{action}/{data}'
