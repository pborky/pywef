__author__="pborky"
__date__ ="$19.2.2010 0:21:07$"

from pywef.controller import FrontController
from pywef.demo.testapp import test_app
from pywef.demo.sendapp import SendApp
from pywef.demo.myapp import MyApp
from pywef.demo.exceptionapp import ExcApp
from pywef.demo.helloapp import Hello

SERVER_SETUP = {'debug': True,
                
                'loggers': {
                    'default':{
                        'file': {
                            'name':'/tmp/pywef/log/pywef_app.log',
                            'size':5000000,
                            'count':5 } } },
                
                'monitor': {
                    'logger': 'default',
                    'force_restart': True,
                    'track_files': ( '/home/peterb/test', ) },

                'exc_wrapper': {
                    'logger': 'default',
                    'call': True,
                    'init': True },

                'controllers': {
                    'index': {
                        'ctrl'  : Hello,
                        'route' : '/' },

                    'hello': {
                        'ctrl'  : Hello,            # instantionate class invoking
                        'ctrl_vars': {'count': 100}, # app = Hello(count=100) ..
                        'route' : '/hello/{who}',              # on each request invoking
                        'route_vars': {'monster': 'snakes'} }, # app(context, who={who}, monster='snake')

                    'send': {
                        'ctrl'  : SendApp,
                        'route' : '/send' },

                    'recv': {
                        'ctrl'  : MyApp,
                        'route' : '/wsgitest' },

                    'test': {
                        'ctrl'  : test_app,
                        'route' : '/test' },

                    'exc':  {
                        'ctrl'  : ExcApp,
                        'route' : '/exc/' },

                    'move': {
                        'ctrl'  : ExcApp,
                        'route' : '/exc/{move}' } } }

                        #'anyname':{'app' : AppClass         - callable class or method, must take positional argument and keyword dictionary
                        #           'app_vars' : dict        - dictionary of application init arguments (optional)
                        #           'route' : '/path'        - route path passed to routes.Mapper.connect() method
                        #           'route_vars' : {..}}     - routing variables, dict passed to routes.Mapper.connect() method
                        #                               see alse http://routes.groovie.org documentation

application = FrontController(**SERVER_SETUP)
