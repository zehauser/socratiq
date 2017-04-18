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

Returns basic public information about a user, if the user exists.

Request:
```
GET /users/zehauser
```

Successful response:
```
200 OK

{
  "userid": "zehauser",
  "name": "Zach Hauser"
}
```

Error response (no such user): `404 Not Found`

### PUT /users/\<userid\>

Creates a user account.

Request:
```
PUT /users/zehauser

{
  "name": "Zach Hauser",
  "email": "zehauser@foo.bar",
  "password": "hunter2"
}
```

Successful response: `201 Created`

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

