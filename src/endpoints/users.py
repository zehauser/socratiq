from datetime import datetime

from common import authentication
from common.database import User
from endpoint import Endpoint, request_schema


class UserCollection(Endpoint):
    """ /users

      Collection of all users.

      - GET returns the list and count of users
      """

    @request_schema(None)
    def get(self):
        users = [user.id for user in self.db_session.query(User).all()]
        self.json_response({ 'user_count': len(users), 'users': users })


class UserInstance(Endpoint):
    """ /users/<user>

      Represents a specific user account.

      - GET returns basic info about the user
      - PUT creates the user account
      """

    @request_schema(None)
    def get(self, userid):
        user = self.get_user(userid)
        if user:
            self.json_response({ 'userid': userid, 'name': user.name })
        else:
            self.error(404)

    @request_schema({ 'name': str, 'email': str, 'password': str })
    def put(self, userid):
        if self.get_user(userid):
            self.error(409)
        else:
            self.db_session.add(User(id=userid,
                                     name=self.json_request['name'],
                                     email=self.json_request['email'],
                                     time_created=datetime.utcnow()))
            password_data = authentication.create_password_data(
                userid, self.json_request['password'])
            self.db_session.add(password_data)
            self.db_session.commit()
            self.response.set_status(201)
