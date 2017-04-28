import uuid
from datetime import datetime

from sqlalchemy.sql import func
from common.database import Article, User, Tag
from endpoint import Endpoint
from endpoints.decorators import requires_authentication, request_schema


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
        if article.author.followers.filter_by(id=follower).count() == 1:
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

    @request_schema(optional_params=['tag', 'author', 'author_institution',
                                     'month', 'year'])
    def get(self):
        if 'tag' in self.request_data:
            tag = self.db_session.query(Tag).get(self.request_data['tag'])
            if not tag:
                self.json_response([])
                return
            articles = tag.articles
        else:
            articles = self.db_session.query(Article)

        if 'author' in self.request_data:
            articles = articles.filter_by(author_id=self.request_data['author'])
        if 'author_institution' in self.request_data:
            articles = articles.filter(
                Article.author.has(institution=self.request_data[
                    'author_institution']))
        if 'year' in self.request_data:
            articles = articles.filter(
                func.YEAR(Article.time_published) ==
                self.request_data['year'])
        if 'month' in self.request_data:
            articles = articles.filter(
                func.MONTH(Article.time_published) ==
                self.request_data['month'])

        articles = articles.order_by(
            Article.time_published.desc()).limit(10).all()
        articles = [
            article_to_json(a, snippet=True, follower=self.authenticated_user)
            for a in articles
        ]
        self.json_response(articles)

    def get_or_create_tag(self, tag_name):
        tag = self.db_session.query(Tag).get(tag_name)
        if not tag:
            self.db_session.add(Tag(name=tag_name))
            self.db_session.query(Tag).get(tag_name)
        return tag

    @request_schema({'title': str, 'content': str, 'tags': [str]})
    @requires_authentication()
    def post(self):
        tags = [self.get_or_create_tag(tag) for tag in tagss]

        author = self.db_session.query(User).get(self.authenticated_user)

        article_id = uuid.uuid4().hex

        article = Article(uuid=article_id,
                          title=self.request_data['title'],
                          time_published=datetime.utcnow(),
                          content=self.request_data['content'],
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
            articles = tag.articles.order_by(
                Article.time_published.desc()).limit(10)
            articles = [
                article_to_json(a, snippet=True,
                                follower=self.authenticated_user)
                for a in articles
            ]
            self.json_response(articles)
