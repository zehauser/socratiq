import uuid
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.sql import func
from common.database import Article, User, Tag, userid_does_follow
from endpoint import Endpoint
from endpoints.decorators import requires_authentication, request_schema
from endpoints.tags import tag_to_json
from endpoints.users import user_to_json


def article_to_json(article, snippet=False, follower=None):
    json = {
        'id': article.uuid,
        'title': article.title,
        'author': user_to_json(article.author, follower),
        'date': article.time_published.strftime('%B %d, %Y'),
        'tags': [t.name for t in article.tags.all()]
    }

    if snippet:
        if len(article.content) < 250:
            json['snippet'] = article.content
        else:
            json['snippet'] = article.content[:247].rstrip('.,!?; \n') + '...'
    else:
        json['content'] = article.content

    return json


class ArticleCollection(Endpoint):
    """ /articles

    Represents the collection of all published articles.

    - GET is the article feed 
    - POST publishes an article (requires authentication as author)
    """

    @request_schema(optional_params=['tag', 'author', 'author_institution',
                                     'month', 'year', 'infinite', 'personalized'])
    def get(self):
        infinite = ('infinite' in self.request_data and
                    self.request_data['infinite'] == 'true')
        personalized = ('personalized' in self.request_data and
                        self.request_data['personalized'] == 'true')
        if personalized and (not self.authenticated_user):
            self.error(401)
            return

        articles = self.db_session.query(Article)
        if 'tag' in self.request_data or personalized:
            articles = articles.join(Article.tags)

        if personalized:
            user = self.db_session.query(User).get(self.authenticated_user)
            users_followed = [u.id for u in user.users_followed.all()]
            tags_followed = [t.name for t in user.tags_followed.all()]
            articles = articles.filter(
                or_(
                    Article.author_id.in_(users_followed),
                    Tag.name.in_(tags_followed)
                )
            )

        if 'tag' in self.request_data:
            articles = articles.filter_by(name=self.request_data['tag'])
        if 'author' in self.request_data:
            articles = articles.filter(Article.author_id == self.request_data['author'])
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

        limit = 500 if infinite else 30
        articles = articles.order_by(
            Article.time_published.desc()).limit(limit).all()
        articles = [
            article_to_json(a, snippet=True, follower=self.authenticated_user)
            for a in articles
        ]
        self.json_response(articles)

    def get_or_create_tag(self, tag_name):
        tag = self.db_session.query(Tag).get(tag_name)
        if not tag:
            tag = Tag(name=tag_name)
            self.db_session.add(tag)
        return tag

    @request_schema({'title': str, 'content': str, 'tags': [str]})
    @requires_authentication()
    def post(self):
        tags = [self.get_or_create_tag(t) for t in self.request_data['tags']]

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
