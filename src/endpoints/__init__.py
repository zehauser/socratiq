from articles import ArticleInstance, ArticleCollection, TagArticleCollection
from followers import UserFollowerInstance, UserFollowerCollection, TagFollowerInstance
from tags import TagCollection
from endpoint import NotFoundHandler
from login import LoginServer
from users import UserInstance, UserCollection
from search import SearchServer
from comments import CommentCollection, CommentInstance

ArticleLikeCollection = NotFoundHandler
ArticleLikeInstance = NotFoundHandler
CommentLikeCollection = NotFoundHandler
CommentLikeInstance = NotFoundHandler

class TestErrorHandler(endpoint.Endpoint):
    def get(self):
        raise StandardError("test exception")