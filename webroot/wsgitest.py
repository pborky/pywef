__author__="pborky"
__date__ ="$18.2.2010 16:30:21$"

import wsgi.demo.myapp as app
import wsgi.controller as ctrl

application = ctrl.FrontControllerFactory.produce(app.MyApp())