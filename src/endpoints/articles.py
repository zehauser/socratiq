import uuid
from datetime import datetime

from common.database import Article, User, Tag
from endpoint import Endpoint, request_schema, requires_authentication


class ArticleCollection(Endpoint):
    """ /articles

    Represents the collection of all published articles.

    - GET is the article feed, and is unimplemented 
    - POST publishes an article (requires authentication as author)
    """

    # TODO
    def get(self):
        self.error(501)

    @request_schema({ 'author': str, 'title': str,
                      'content': str, 'tags': [str] })
    @requires_authentication(as_key='author')
    def post(self):
        # TODO don't just create them, and have a max # of tags, and check for uniqueness
        for tag in self.json_request['tags']:
            if not self.db_session.query(Tag).get(tag):
                self.db_session.add(Tag(name=tag))
        tags = [self.db_session.query(Tag).get(tag) for tag in self.json_request['tags']]

        author = self.db_session.query(User).get(self.json_request['author'])

        self.db_session.add(Article(uuid=uuid.uuid4().hex,
                                    title=self.json_request['title'],
                                    time_published=datetime.utcnow(),
                                    content=self.json_request['content'],
                                    tags=tags,
                                    author=author))
        self.db_session.commit()
        self.response.set_status(201)


class ArticleInstance(Endpoint):
    """ /articles/<article>
    
    Represents a specific published article.
    
    - GET returns the article content and its metadata
    """

    @request_schema(None)
    def get(self, article_id):
        article = self.db_session.query(Article).get(article_id)
        if not article:
            self.error(404)
        else:
            self.json_response({
                'id': article.uuid,
                'author': article.author_id,
                'title': article.title,
                'time_published': article_id.time_published,
                'content': article.content,
                'tags': [tag.name for tag in article.tags]
            })
