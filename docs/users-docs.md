# API Documentation: /users endpoints

## /users

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

## /users/\<userid\>

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
  "institution": "Pomona College",
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
  "email": "zack.hauser@pomona.edu",
  "institution": "Pomona College",
  "password": "hunter2"
}
```

Successful response: 
```
201 Created
Authorization: Bearer eyJ0eXAiOiJKV1Q.eyJleGFtcGQ5M.PRyeTAp
```


Error response (userid already exists): `409 Conflict`

Error response (email domain does not match institution's): `422 Unprocessable Entity`

## /users/<userid_1>/followers/<userid_2>

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

