from common import authentication
from common.authentication import InvalidAuthenticationError
from common.database import PasswordData, User
from endpoint import Endpoint
from endpoints.decorators import request_schema
from common.representations import user_to_json


class LoginServer(Endpoint):
    @request_schema({'userid': str, 'password': str})
    def post(self):
        try:
            userid = self.request_data['userid']
            token = authentication.issue_token(
                userid,
                self.db_session.query(PasswordData).get(userid),
                self.request_data['password']
            )
            self.response.set_status(200)
            self.response.headers['Authorization'] = "Bearer {}".format(token)

            user = self.db_session.query(User).get(userid)
            response = user_to_json(user)
            response['tagsFollowed'] = [t.name for t in user.tags_followed.all()]
            response['usersFollowed'] = [u.id for u in user.users_followed.all()]
            self.json_response(response)

        except InvalidAuthenticationError:
            self.error(
                403,
                "403 Forbidden! Username/password combination is invalid.\r\n"
            )
