# API Documentation: /login endpoint

## /login

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