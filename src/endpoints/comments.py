import uuid

import datetime

from common.database import Article, Comment, User
from endpoints.decorators import request_schema, requires_authentication
from endpoints.endpoint import Endpoint
from common.representations import user_to_json


def comment_to_json(comment, follower_id=None, snippet=False):
    json = {
        'id': comment.id,
        'date': comment.time_published.strftime('%B %d, %Y'),
        'author': user_to_json(comment.author, follower_id)
    }
    if snippet:
        if len(comment.content) < 50:
            json['snippet'] = comment.content
        else:
            json['snippet'] = comment.content[:47].rstrip('.,!?; \n') + '...'
    else:
        json['content'] = comment.content


class CommentCollection(Endpoint):
    @request_schema(None)
    def get(self, article_id):
        article = self.db_session.query(Article).get(article_id)
        if not article:
            self.error(404)
        else:
            self.json_response([comment_to_json(c, self.authenticated_user)
                                for c in article.comments.all()])

    @requires_authentication()
    @request_schema({'content': str})
    def post(self, article_id):
        author = self.db_session.query(User).get(self.authenticated_user)
        comment_id = uuid.uuid4().hex

        comment = Comment(uuid=comment_id,
                          author=author,
                          content=self.request_data['content'],
                          time_published=datetime.utcnow())
        self.db_session.add(Comment)
        self.db_session.commit()

        self.response.set_status(201)
        url = '/articles/{}/comments/{}'.format(article_id, comment_id)
        self.response.headers['Location'] = url
        self.json_response(comment_to_json(comment))


class CommentInstance(Endpoint):
    @request_schema(None)
    def get(self, article_id, comment_id):
        comment = self.db_session.query(Comment).get(comment_id)
        if not comment:
            self.error(404)
        else:
            self.json_response(comment, self.authenticated_user)
