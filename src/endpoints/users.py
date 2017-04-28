from datetime import datetime

from common import authentication
from common.database import User, Institution
from endpoint import Endpoint, request_schema


def email_has_domain(email, domain):
    return email.endswith('@' + domain) or email.endswith('.' + domain)


class UserCollection(Endpoint):
    """ /users

      Collection of all users.

      - GET returns the list and count of users
      """

    @request_schema(None)
    def get(self):
        users = self.db_session.query(User.id).all()
        self.json_response({'user_count': len(users), 'users': users})


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
            response = {
                'userid': userid,
                'name': user.name,
                'institution': user.institution
            }
            if self.authenticated_user and self.authenticated_user != userid:
                if (user.followers
                            .filter(User.id == self.authenticated_user)
                            .count() == 1):
                    response['followed'] = True
                else:
                    response['followed'] = False
            self.json_response(response)
        else:
            self.error(404)

    @request_schema({'name': str, 'email': str, 'password': str,
                     'institution': str})
    def put(self, userid):
        if self.get_user(userid):
            self.error(409)
            return
        email = self.request_data['email']
        institution_name = self.request_data['institution']
        institution = self.db_session.query(Institution).get(institution_name)
        if not (institution and email_has_domain(email, institution.domain)):
            self.error(422)
        else:
            self.db_session.add(User(id=userid,
                                     name=self.request_data['name'],
                                     email=email,
                                     institution=institution_name,
                                     time_created=datetime.utcnow()))
            password = self.request_data['password']
            password_data = authentication.create_password_data(userid,
                                                                password)
            self.db_session.add(password_data)
            self.db_session.commit()
            self.response.set_status(201)
            token = authentication.issue_token(userid, password_data, password)
            self.response.headers['Authorization'] = "Bearer {}".format(token)
