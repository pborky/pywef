__author__="pborky"
__date__ ="$19.2.2010 0:21:07$"

from wsgi.controller import FrontControllerFactory
from wsgi.demo.testapp import test_app
from wsgi.demo.sendapp import SendApp
from wsgi.demo.myapp import MyApp
from wsgi.demo.exceptionapp import ExcApp
from wsgi.monitor import Monitor

Monitor().start()

class Hello(object):
    """ Demo application showing hello world.."""
    def __init__(self, **kwargs):
        if 'count' in kwargs:
            self.count = kwargs['count']
        else:
            self.count = 1

    def __call__(self, context, **kwargs):
        monster = 'dragon'
        who = 'world'
        
        if 'monster' in kwargs.keys():
            monster = str(kwargs['monster'])

        if 'who' in kwargs.keys():
            who = str(kwargs['who'])            

        context.response.status = 200
        context.response.headers['Content-Type'] = 'text/plain'
        context.response.body_file.write('Hello %s!\nHere be %d %s soon.' % (who, self.count, monster))

APP_SETUP = {'debug': True,
            'show_debug_code': True,
            'apps': {'index': {     'app'   : Hello,
                                    'route' : '/' },
                                    
                     'hello': {     'app'   : Hello,
                                    'app_vars': {'count': 100}, # app = Hello(count=999) ..
                                    'route' : '/hello/{who}',
                                    'route_vars': {'monster': 'snakes'} }, # app(who={who}, monster='snake')

                     'send': {      'app'   : SendApp,
                                    'route' : '/send' },

                     'wsgitest': {  'app'   : MyApp,
                                    'route' : '/wsgitest' },

                     'test': {       'app'   : test_app,
                                    'route' : '/test' },

                     'exception': {  'app'   : ExcApp,
                                    'route' : '/exc' } } }
                                    
                    #'anyname':{'app' : AppClass         - callable class or method, must take positional argument and keyword dictionary
                    #           'app_vars' : dict        - dictionary of application init arguments (optional)
                    #           'route' : '/path'        - route path passed to routes.Mapper.connect() method
                    #           'route_vars' : {..}}     - routing variables, dict passed to routes.Mapper.connect() method
                    #                               see alse http://routes.groovie.org documentation

application = FrontControllerFactory.produce(**APP_SETUP)
