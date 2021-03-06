from datetime import datetime

from common import authentication
from common.database import User, Institution
from common.representations import user_to_json, tag_to_json
from endpoint import Endpoint
from endpoints.decorators import request_schema


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
        user = self.db_session.query(User).get(userid)
        if not user:
            self.error(404)

        response = user_to_json(user, self.authenticated_user)

        response['tagsFollowed'] = [tag_to_json(t, self.authenticated_user)
                                    for t in user.tags_followed.all()]
        response['usersFollowed'] = [user_to_json(u, self.authenticated_user)
                                     for u in user.users_followed.all()]

        self.json_response(response)

    @request_schema({'name': str, 'email': str, 'password': str,
                     'institution': str})
    def put(self, userid):
        if self.db_session.query(User).get(userid):
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