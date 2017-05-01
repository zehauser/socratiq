from common.database import User, userid_does_follow
from endpoint import Endpoint
from endpoints.decorators import requires_authentication, request_schema


class UserFollowerCollection(Endpoint):
    """ /users/<followee>/followers

    Collection of all users that follow <followee>. 

    - GET returns the list and count of followers
    """

    @request_schema(None)
    def get(self, followee_id):
        followee = self.db_session.query(User).get(followee_id)
        if not followee:
            self.error(404)
        else:
            followers = [user.id for user in followee.followers.all()]
            self.json_response(
                { 'followee': followee_id, 'follower_count': len(followers),
                  'followers': followers })


class UserFollowerInstance(Endpoint):
    """ /users/<followee>/followers/<follower> 
    
    Represents a user-to-user follower relationship. 
        
    - GET checks to see if the relationship exists (requires authentication as 
      follower)
    - PUT adds a follower (requires authentication as follower)
    - DELETE removes a follower (requires authentication as follower)
    """

    @request_schema(None)
    @requires_authentication(as_param='follower_id')
    def get(self, followee_id, follower_id):
        followee = self.db_session.query(User).get(followee_id)
        if not followee:
            self.error(404)
        elif userid_does_follow(follower_id, user=followee):
            self.response.set_status(204)
        else:
            self.error(404)

    @request_schema(None)
    @requires_authentication(as_param='follower_id')
    def put(self, followee_id, follower_id):
        followee = self.db_session.query(User).get(followee_id)
        if not followee:
            self.error(404)
        elif userid_does_follow(follower_id, user=followee):
            self.error(409)
        else:
            follower = self.db_session.query(User).get(follower_id)
            follower.users_followed.append(followee)
            self.db_session.commit()
            self.response.set_status(201)

    @request_schema(None)
    @requires_authentication(as_param='follower_id')
    def delete(self, followee_id, follower_id):
        followee = self.db_session.query(User).get(followee_id)
        if not followee:
            self.error(404)
        elif userid_does_follow(follower_id, user=followee):
            follower = self.db_session.query(User).get(follower_id)
            follower.users_followed.remove(followee)
            self.db_session.commit()
            self.response.set_status(204)

        else:
            self.error(404)