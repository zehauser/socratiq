import webapp2
import os
import MySQLdb

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')

class ApiServer(webapp2.RequestHandler):
    def get(self, arg):
        self.response.headers['Content-Type'] = 'text/plain'
        cloudsql_unix_socket = os.path.join(
          '/cloudsql', CLOUDSQL_CONNECTION_NAME)
        db = MySQLdb.connect(
          unix_socket=cloudsql_unix_socket,
          user=CLOUDSQL_USER)
        cursor = db.cursor()
        cursor.execute('USE testing')
        cursor.execute('SELECT lname, fav_color FROM Users WHERE fname = %s', (arg,))
        if cursor.rowcount:
          for (lname, color) in cursor.fetchall():
            self.response.write('{} {}\'s favorite color is {}\n'.format(arg, lname, color))
        else:
          self.response.write("No user with first name: {}\n".format(arg))

app = webapp2.WSGIApplication([
    ('/api/(.*)', ApiServer),
], debug=True)
