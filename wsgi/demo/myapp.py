__author__="pborky"
__date__ ="$Feb 21, 2010 6:54:38 PM$"

class MyApp(object):

    def __init__(self):
        self.counter = 0

    def __call__(self, context):
        res = context.response
        req = context.request

        res.status = 200
        res.headers['Content-Type'] ='text/html'

        self.counter += 1
        
        res.body_file.write('<p>Request number: %s </p>' % self.counter)
        res.body_file.write('<h1>Request environment: </h1><table>')
        res.body_file.write('<tr><td><b>request body</b></td><td>%s</td></tr>' % req.body)

        for i in req.environ.items():
            res.body_file.write('<tr><td><b>%s</b></td><td>%s</td></tr>' % i)

        res.body_file.write('</table>')

