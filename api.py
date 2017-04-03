import webapp2

class ApiServer(webapp2.RequestHandler):
    def get(self, args):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("API Server: {}".format(args))

app = webapp2.WSGIApplication([
    ('/api/(.*)', ApiServer),
], debug=True)
