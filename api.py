import webapp2
from datetime import datetime

from endpoints import Endpoint, requires_authentication, request_schema
from database import User, PasswordData
from authentication import issue_token, create_password

class UserInstance(Endpoint):

    @request_schema({ 'name': str, 'email': str, 'password': str })
    def put(self, userid):
        if self.get_user(userid):
            self.error(409)
        else:
            self.db_session.add(User(id=userid, 
                                     name=self.json_request['name'], 
                                     email=self.json_request['email'],
                                     time_created=datetime.utcnow()))
            self.db_session.add(create_password(userid, 
                                                self.json_request['password']))
            self.db_session.commit()
            self.response.set_status(201)

    @request_schema(None)
    def get(self, userid):
        user = self.get_user(userid)
        if user:
            self.json_response({ 'name': user.name })
        else:
            self.error(404)

class LoginServer(Endpoint):

    @request_schema({ 'userid': str, 'password': str })
    def post(self):
        userid = self.json_request['userid']
        token = issue_token(userid, 
                            self.db_session.query(PasswordData).get(userid),
                            self.json_request['password'])
        if token:
            self.response.set_status(204)
            self.response.headers['Authorization'] = "Bearer {}".format(token)
        else:
            self.error(403, "Username/password combination is invalid.\r\n")

class UserInstanceEmail(Endpoint):

    @request_schema(None)
    @requires_authentication(as_param='userid')
    def get(self, userid):
        user = self.get_user(userid)
        if user:
            self.json_response({ 'email': user.email })
        else:
            self.error(404)

class UserInstanceFollowers(Endpoint):

    @request_schema(None)
    @requires_authentication(as_param='follower_id')
    def put(self, followee_id, follower_id):
        followee = self.db_session.query(User).get(followee_id)
        follower = self.db_session.query(User).get(follower_id)
        if not (follower and followee):
            self.error(404)
        elif follower.users_followed.filter(id == followee_id).count() > 0:
            self.error(409)
        else:
            follower.users_followed.append(followee)
            self.db_session.commit()
            self.response.set_status(201)

    @request_schema(None)
    @requires_authentication(as_param='follower_id')
    def delete(self, followee_id, follower_id):
        followee = self.db_session.query(User).get(followee_id)
        follower = self.db_session.query(User).get(follower_id)
        if not (followee and follower):
            self.error(404)
        if not follower.users_followed.filter(id == followee.id).count() > 0:
            self.error(404)
        else:
            follower.users_followed.remove(followee)
            self.db_session.commit()
            self.response.set_status(204)

app = webapp2.WSGIApplication([
    webapp2.Route('/api/users/<userid>/email', UserInstanceEmail),
    webapp2.Route('/api/users/<followee_id>/followers/<follower_id>', UserInstanceFollowers),
    webapp2.Route('/api/users/<userid>', UserInstance),
    webapp2.Route('/api/login', LoginServer)
], debug=True)
