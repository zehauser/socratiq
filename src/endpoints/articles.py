import uuid
from datetime import datetime

from common.database import Article, User, Tag
from endpoint import Endpoint, request_schema, requires_authentication

def article_to_json(article, snippet=False, follower=None):
    json = {
        'id': article.uuid,
        'title': article.title,
        'author': {
            'name': article.author.name,
            'userid': article.author.id,
            'institution': article.author.institution
        },
        'date': article.time_published.strftime('%B %d, %Y'),
        'tags': [tag.name for tag in article.tags if tag.name != 'NYT_scraped']
    }
    if snippet:
        json['snippet'] = article.content[:247] + '...'
    else:
        json['content'] = article.content
    if follower and follower != article.author.id:
        if article.author.followers.filter(User.id == follower).count() == 1:
            json['author']['followed'] = True
        else:
            json['author']['followed'] = False
    return json


class ArticleCollection(Endpoint):
    """ /articles

    Represents the collection of all published articles.

    - GET is the article feed 
    - POST publishes an article (requires authentication as author)
    """

    @request_schema(None)
    def get(self):
        articles = self.db_session.query(Article).limit(10).all()
        articles = [
            article_to_json(a, snippet=True, follower=self.authenticated_user)
            for a in articles
        ]
        self.json_response(articles)

    @request_schema({'title': str, 'content': str, 'tags': [str]})
    @requires_authentication()
    def post(self):

        tag_names = self.json_request['tags']
        for tag in tag_names:
            if not self.db_session.query(Tag).get(tag):
                self.db_session.add(Tag(name=tag))

        tags = [self.db_session.query(Tag).get(tag) for tag in tag_names]

        author = self.db_session.query(User).get(self.authenticated_user)

        article_id = uuid.uuid4().hex

        article = Article(uuid=article_id,
                          title=self.json_request['title'],
                          time_published=datetime.utcnow(),
                          content=self.json_request['content'],
                          tags=tags,
                          author=author)
        self.db_session.add(article)
        self.db_session.commit()

        self.response.set_status(201)
        self.response.headers['Location'] = '/articles/{}'.format(article_id)
        self.json_response(article_to_json(article))


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
            json = article_to_json(article, follower=self.authenticated_user)
            self.json_response(json)


class TagArticleCollection(Endpoint):
    """ /tags/<tag>/articles
    
    Represents the collection of all published articles with the tag <tag>.
    
    - GET returns the collection 
    """

    @request_schema(None)
    def get(self, tag):
        tag = self.db_session.query(Tag).get(tag)
        if not tag:
            self.error(404)
        else:
            articles = tag.articles.limit(10)
            articles = [
                article_to_json(a, snippet=True, follower=self.authenticated_user)
                for a in articles
            ]
            self.json_response(articles)