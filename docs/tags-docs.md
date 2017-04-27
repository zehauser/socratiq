# API Documentation: /tags endpoints

## /tags/\<tag\>/articles

### GET /tags/\<tag\>/articles

Get a feed of 10 random articles tagged with `tag` 
(with metadata, but only partial body content).

Request:
```
GET /tags/foo/articles
```

Successful response:
```
200 OK

[
    {
        "id": "bdc4d94969c945bf9a394667a1543344",
        "title": "The Art of Foo: Baz Bar",
        "author": {
            "userid": "zehauser",
            "name": "Zach Hauser",
            "institution": "Pomona College",
            "followed": true
        },
        "date": "January 1, 1970",
        "snippet": "It was a dark and stormy night, and...",
        "tags": [ "foo", "bar", "baz" ]
    }
]
```

Error response (`tag` does not exist): `404 Not Found`

Note that the `"followed"` flag (indicating whether the authenticated user 
follows `author`) will not appear if the request is unauthenticated, or if 
the authenticated user is `author`.