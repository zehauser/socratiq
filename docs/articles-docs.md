# API Documentation: /articles endpoints

## /articles

### GET /articles

Get a feed of 10 random articles (with metadata, but only partial body content).

Request:
```
GET /articles
```

Response:
```
200 OK

[
    {
        "article_id": "bdc4d94969c945bf9a394667a1543344",
        "author_id": "zehauser",
        "title": "The Art of Foo: Baz Bar"
        "name": "Zach Hauser",
        "date": "January 1, 1970",
        "snippet": "It was a dark and stormy night, and...",
        "tags": [ "foo", "bar", "baz" ],
        "followed": true,
    }
]
```

Note that the `"followed"` flag (indicating whether the authenticated user 
follows `userid`) will not appear if the request is unauthenticated, or if 
the authenticated user is `userid`.

## /articles/\<article_id\>

### GET /articles/\<article_id\>

Get the full content of the specified article.

Request:
```
GET /article/bdc4d94969c945bf9a394667a1543344
```

Response:
```
200 OK

{
    "article_id": "bdc4d94969c945bf9a394667a1543344",
    "author_id": "zehauser",
    "title": "The Art of Foo: Baz Bar"
    "name": "Zach Hauser",
    "date": "January 1, 1970",
    "content": "It was a dark and stormy night; the rain fell in torrents - 
                except at occasional intervals, when it was checked by a  
                violent gust of wind which swept up the streets."
    "tags": [ "foo", "bar", "baz" ],
    "followed": true,
}
```

Note that the `"followed"` flag (indicating whether the authenticated user 
follows `userid`) will not appear if the request is unauthenticated, or if 
the authenticated user is `userid`.