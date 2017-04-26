import webapp2

from endpoints import *

app = webapp2.WSGIApplication([
    webapp2.Route('/articles', ArticleCollection),
    webapp2.Route('/articles/<article_id>', ArticleInstance),
    webapp2.Route('/articles/<article_id>/likes', ArticleLikeCollection),
    webapp2.Route('/articles/<article_id>/likes/<userid>', ArticleLikeInstance),

    webapp2.Route('/articles/<article_id>/comments', CommentCollection),
    webapp2.Route('/articles/<article_id>/comments/<comment_id',
                  CommentInstance),
    webapp2.Route('/articles/<article_id>/comments/<comment_id>/likes',
                  CommentLikeCollection),
    webapp2.Route('/articles/<article_id>/comments/<comment_id>/likes/<userid>',
                  CommentLikeInstance),

    webapp2.Route('/users', UserCollection),
    webapp2.Route('/users/<userid>', UserInstance),
    webapp2.Route('/users/<userid>/articles', UserArticleCollection),
    webapp2.Route('/users/<followee_id>/followers', UserFollowerCollection),
    webapp2.Route('/users/<followee_id>/followers/<follower_id>',
                  UserFollowerInstance),

    webapp2.Route('/tags', TagCollection),
    webapp2.Route('/tags/<tag>', TagInstance),
    webapp2.Route('/tags/<tag>/articles', TagArticleCollection),
    webapp2.Route('/tags/<tag>/followers/', TagFollowerCollection),
    webapp2.Route('/tags/<tag>/followers/<follower_id>', TagFollowerInstance),

    webapp2.Route('/login', LoginServer),

    webapp2.Route('<:.*>', NotFoundHandler)
], debug=False)