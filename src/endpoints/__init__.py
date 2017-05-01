from articles import ArticleInstance, ArticleCollection, TagArticleCollection
from followers import UserFollowerInstance, UserFollowerCollection
from tags import TagCollection
from endpoint import NotFoundHandler
from login import LoginServer
from users import UserInstance, UserCollection

ArticleLikeCollection = NotFoundHandler
ArticleLikeInstance = NotFoundHandler
CommentInstance = NotFoundHandler
CommentLikeCollection = NotFoundHandler
CommentLikeInstance = NotFoundHandler
UserArticleCollection = NotFoundHandler
TagInstance = NotFoundHandler
TagFollowerCollection = NotFoundHandler
TagFollowerInstance = NotFoundHandler
CommentCollection = NotFoundHandler

class TestErrorHandler(endpoint.Endpoint):
    def get(self):
        raise StandardError("test exception")