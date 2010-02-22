__author__="pborky"
__date__ ="$18.2.2010 16:30:21$"

from wsgi.demo.sendapp import SendApp
from wsgi.controller import FrontControllerFactory
from wsgi.monitor import Monitor

Monitor().start()
application = FrontControllerFactory.produce(SendApp())
