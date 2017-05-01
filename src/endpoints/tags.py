from sqlalchemy import func

from common.database import _article_tags
from endpoints.decorators import request_schema
from endpoints.endpoint import Endpoint


class TagCollection(Endpoint):
    @request_schema(None)
    def get(self):
        tags_by_count = self.db_session \
            .query(_article_tags.c.tag, func.count('*').label('count')) \
            .group_by(_article_tags.c.tag) \
            .order_by('count DESC') \
            .all()
        self.json_response([t for t, _ in tags_by_count])
