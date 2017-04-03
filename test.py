import webapp2

class TestPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("test home page")

app = webapp2.WSGIApplication([
    ('/', TestPage),
], debug=True)
