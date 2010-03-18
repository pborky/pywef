__author__="pborky"
__date__ ="$19.2.2010 0:21:07$"

from pywef import FrontController, ActionController
from pywef.demo.helloapp import Hello
from pywef.demo.indexapp import Index
from pywef.demo.testaction import TestAction


SERVER_SETUP = {
    'debug': True,

    'loggers': {
        'default':{
            'file': {
                'name':'/tmp/pywef/log/pywef_app.log',
                'size':5000000,
                'count':5 } } },

    'monitor': {
        'logger': 'default',
        'force_restart': True,
        'track_files': ( '/tmp/test', '/home/pborky/Projects/python/pywef/src/templates/') },

    'exc_wrapper': {
        'logger': 'default',
        'call': True,
        'init': True },

    'controllers': {
        'index': {
            'ctrl': Index,
            'ctrl_vars': {
                'count': 25 },
            'route': '/',
            'route_vars': {
                'who': 'World',
                'monster': 'dragons' } },
        'hello': {
            'ctrl': Hello,
            'route': '/hello' },
        'main': {
            'ctrl': ActionController,
            'ctrl_vars': {
                'actions': {
                    'test': (TestAction, 'test') },
                'templates_dir': '/home/pborky/Projects/python/pywef/src/templates',
                'templates': {
                    'test': 'testview.xml' } },
            'route': '/do/{action}/{data}' } } }

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
