from common.database import userid_does_follow


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


def user_to_json(user, follower_id=None):
    json = {'userid': user.id, 'name': user.name,
            'institution': user.institution}
    if follower_id and follower_id != user.id:
        if userid_does_follow(follower_id, user):
            json['followed'] = True
        else:
            json['followed'] = False
    return json


def tag_to_json(tag, follower_id=None):
    json = {'tag': tag.name}
    if follower_id:
        json['followed'] = userid_does_follow(follower_id, tag=tag)
    return json