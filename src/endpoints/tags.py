from sqlalchemy import func

from common.database import _article_tags, userid_does_follow
from endpoints.decorators import request_schema
from endpoints.endpoint import Endpoint


def tag_to_json(tag, follower_id=None):
    json = {'tag': tag.name}
    if follower_id:
        json['followed'] = userid_does_follow(follower_id, tag=tag)
    return json


class TagCollection(Endpoint):
    @request_schema(None)
    def get(self):
        tags_by_count = self.db_session \
            .query(_article_tags.c.tag, func.count('*').label('count')) \
            .group_by(_article_tags.c.tag) \
            .order_by('count DESC') \
            .all()
        self.json_response([t for t, _ in tags_by_count])
