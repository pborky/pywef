__author__="pborky"
__date__ ="$Feb 21, 2010 6:54:38 PM$"

class MyApp(object):

    def __init__(self):
        self.counter = 0

    def __call__(self, context):
        res = context.response
        req = context.request

        res.status = 200

        self.counter += 1
        res.body.append('<p>Request number: %s </p>' % self.counter)

        if (False):#len(req.content) == 0):
            res.body.append("""<FORM method="post">
                <P>
                Name: <INPUT type="text" name="name"></br>
                Last: <INPUT type="text" name="last"></br>
                <INPUT type="radio" name="sex" value="Male"> Male</br>
                <INPUT type="radio" name="sex" value="Female"> Female</br>
                <INPUT type="submit" value="Send"></P>
                </FORM>""")

        else:
            res.body.append('<p>Request content: %s </p>' % req.content)
            res.body.append('<h1>The environ contains: </h1><table>')

            for i in req.environ.items():
                res.body.append('<tr><td><b>%s</td><td>%s</td></tr>' % i)

            res.body.append('</table>')

        res.header.append(('Content-Type', 'text/html'))
        res.header.append(('Content-Length', str(res.contentLength)))