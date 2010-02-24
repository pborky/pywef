__author__="pborky"
__date__ ="$Feb 21, 2010 6:54:38 PM$"

class SendApp(object):

    def __init__(self):
        self.counter = 0

    def __call__(self, context):
        res = context.response
        req = context.request

        res.status = 200
        res.headers['Content-Type'] = 'text/html'

        self.counter += 1
        res.body_file.write('<p>Request number: %s </p>' % self.counter)
        res.body_file.write("""<FORM method="post" action="wsgitest.py">
            <P>
            Name: <INPUT type="text" name="name"></br>
            Last: <INPUT type="text" name="last"></br>
            <INPUT type="radio" name="sex" value="Male"> Male</br>
            <INPUT type="radio" name="sex" value="Female"> Female</br>
            <INPUT type="submit" value="Send"></P>
            </FORM>""")

