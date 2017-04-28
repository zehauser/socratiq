from common import authentication
from common.authentication import InvalidAuthenticationError
from common.database import PasswordData
from endpoint import Endpoint, request_schema


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
            self.response.set_status(204)
            self.response.headers['Authorization'] = "Bearer {}".format(token)
        except InvalidAuthenticationError:
            self.error(
                403,
                "403 Forbidden! Username/password combination is invalid.\r\n"
            )
