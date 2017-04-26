# API Documentation

## General notes

Many endpoints require authentication. Authentication tokens are obtained from 
the `/login` endpoint and are valid for 12 hours. Tokens are sent as an 
`Authorization` header, e.g. `Authorization: Bearer <token>`.

General errors applicable to all resources:
- resource doesn't exist: `404 Not Found`
- request method (GET, POST, etc) invalid for resource: `405 Method Not Allowed`
- request body doesn't match required schema: `400 Bad Request`
- server error (please report this!): `500 Internal Server Error`

General errors applicable to endpoints that require authentication:
- authorization token is unexpired and valid for User X, but User X is not 
authorized for the resource: `403 Forbidden`
- authorization token is missing, invalid, or expired: `401 Unauthorized`




## Endpoints

### GET /users

Returns summary information about all users on the site. 

Request:
```
GET /users
```

Response: 
```
200 OK

{
  "user_count": 3,
  "users": ["zehauser", "knuth", "abello", "madhura"]
} 
```

### GET /users/\<userid\>

Returns basic information about a user, if the user exists.

Request:
```
GET /users/zehauser
```

Successful response:
```
200 OK

{
  "userid": "zehauser",
  "name": "Zach Hauser",
  "followed": false
}
```

Note that the `"followed"` flag (indicating whether the authenticated user 
follows `userid`) will not appear if the request is unauthenticated, or if 
the authenticated user is `userid`.

Error response (no such user): `404 Not Found`

### PUT /users/\<userid\>

Creates a user account (and issues an authorization token, like `/login`).

Request:
```
PUT /users/zehauser

{
  "name": "Zach Hauser",
  "email": "zehauser@foo.bar",
  "password": "hunter2"
}
```

Successful response: 
```
201 Created
Authorization: Bearer eyJ0eXAiOiJKV1Q.eyJleGFtcGQ5M.PRyeTAp
```


Error response (userid already exists): `409 Conflict`

### POST /login

Use userid and password to log in and receive a authentication token.

Request:
```
POST /login

{
  "userid": "zehauser",
  "password": "hunter2"
}
```

Successful response:
```
204 No Content
Authorization: Bearer eyJ0eXAiOiJKV1Q.eyJleGFtcGQ5M.PRyeTAp
```
 
Error response (userid/password don't match): `403 Forbidden`

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
        "snippet": "It was a dark and stormy night, and..."
        "followed": true,
    }
]
```

Note that the `"followed"` flag (indicating whether the authenticated user 
follows `userid`) will not appear if the request is unauthenticated, or if 
the authenticated user is `userid`.

### GET /users/<userid_1>/followers/<userid_2>

Indicates whether or not `userid_2` follows `userid_1`. 
Requires authentication as `userid_2`.

Request:
```
GET /users/knuth/followers/zehauser
Authorization: Bearer eyJ0eXAiOiJKV1Q.eyJleGFtcGQ5M.PRyeTAp
```

Successful response (`zehauser` follows `knuth`): `204 No Content`

Successful response (`zehauser` does not follow `knuth`): `404 Not Found` 
(or: `knuth` does not exist)


### PUT /users/<userid_1>/followers/<userid_2>

Add `userid_2` as a follower of `userid_1`. 
Requires authentication as `userid_2`.

Request:
```
PUT /users/knuth/followers/zehauser
Authorization: Bearer eyJ0eXAiOiJKV1Q.eyJleGFtcGQ5M.PRyeTAp
```

Successful response: `201 Created`

Error response (`zehauser` already follows `knuth`): `409 Conflict`

### DELETE /users/<userid_1>/followers/<userid_2>

Removes `userid_2` as a follower of `userid_1`. 
Requires authentication as `userid_2`.

Request:
```
DELETE /users/knuth/followers/zehauser
Authorization: Bearer eyJ0eXAiOiJKV1Q.eyJleGFtcGQ5M.PRyeTAp
```

Successful response: `204 No Content`

Error response (`zehauser` does not follow `knuth`): `404 Conflict` 
(or: `knuth` does not exist)

