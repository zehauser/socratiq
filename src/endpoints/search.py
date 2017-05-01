from sqlalchemy import or_

from common.database import Article, User, Tag
from endpoints.articles import article_to_json
from endpoints.decorators import request_schema
from endpoints.endpoint import Endpoint
from endpoints.tags import tag_to_json
from endpoints.users import user_to_json

MAX_RESULTS = 30

class SearchServer(Endpoint):

    def search_users(self, query):
        exact_matches = self.db_session.query(User).filter(
            or_(
                User.id == query,
                User.name == query
            )
        ).all()
        matches = self.db_session.query(User).filter(
            or_(
                User.id.like('%' + query + '%'),
                User.name.like('%' + query + '%')

            )
        ).limit(MAX_RESULTS).all()

        matches = exact_matches + [u for u in matches if u not in exact_matches]

        return [user_to_json(u, self.authenticated_user)
                for u in matches[:MAX_RESULTS]]

    def search_tags(self, query):
        exact_match = self.db_session.query(Tag).get(query)
        close_matches = self.db_session.query(Tag).filter(
            Tag.name.like('% ' + query + ' %')
        ).limit(MAX_RESULTS).all()
        matches = self.db_session.query(Tag).filter(
            Tag.name.like('%' + query + '%')
        ).limit(MAX_RESULTS).all()

        matches = close_matches + [t for t in matches if t not in close_matches]
        if exact_match:
            matches = [t for t in matches if t.name != exact_match.name]
            matches.insert(0, exact_match)

        return [tag_to_json(u, self.authenticated_user) for u in matches[:MAX_RESULTS]]

    def search_articles(self, query):
        exact_matches = self.db_session.query(Article).filter(
            Article.title == query
        ).limit(MAX_RESULTS).all()
        close_matches = self.db_session.query(Article).filter(
            Article.title.like('% ' + query + ' %')
        ).limit(MAX_RESULTS).all()
        matches = self.db_session.query(Article).filter(
            Article.title.like('%' + query + '%')
        ).limit(MAX_RESULTS).all()

        close_matches = exact_matches + [a for a in close_matches if
                                   a not in exact_matches]
        matches = close_matches + [a for a in matches if
                                   a not in close_matches]

        return [article_to_json(a, self.authenticated_user) for a in
                matches[:MAX_RESULTS]]

    @request_schema(required_params=['query'])
    def post(self):
        query = self.request_data['query']

        self.json_response({
            'users': self.search_users(query),
            'articles': self.search_articles(query),
            'tags': self.search_tags(query)
        })