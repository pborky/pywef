__author__="pborky"
__date__ ="$19.2.2010 0:21:07$"

from wsgi.controller import FrontControllerFactory
from wsgi.demo.testapp import test_app
from wsgi.demo.sendapp import SendApp
from wsgi.demo.myapp import MyApp
from wsgi.demo.exceptionapp import ExcApp
from wsgi.demo.helloapp import Hello
from wsgi.monitor import Monitor

Monitor().start()

SERVER_SETUP = {'debug': True,
                'show_debug_code': True,
                'apps': {'index': { 'app'   : Hello,
                                    'route' : '/' },

                         'hello': { 'app'   : Hello,
                                    'app_vars': {'count': 100}, # app = Hello(count=100) ..
                                    'route' : '/hello/{who}',
                                    'route_vars': {'monster': 'snakes'} }, # app(context, who={who}, monster='snake')

                         'send': {  'app'   : SendApp,
                                    'route' : '/send' },

                         'recv': {  'app'   : MyApp,
                                    'route' : '/wsgitest' },

                         'test': {  'app'   : test_app,
                                    'route' : '/test' },

                         'exc':  {  'app'   : ExcApp,
                                    'route' : '/exc/' },

                         'move': {  'app'   : ExcApp,
                                    'route' : '/exc/{move}' } } }

                    #'anyname':{'app' : AppClass         - callable class or method, must take positional argument and keyword dictionary
                    #           'app_vars' : dict        - dictionary of application init arguments (optional)
                    #           'route' : '/path'        - route path passed to routes.Mapper.connect() method
                    #           'route_vars' : {..}}     - routing variables, dict passed to routes.Mapper.connect() method
                    #                               see alse http://routes.groovie.org documentation

application = FrontControllerFactory.produce(**SERVER_SETUP)
