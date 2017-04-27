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

### /login endpoint

[Click here to see documentation for the `/login` endpoints.](docs/login-docs.md)

### /users endpoints

[Click here to see documentation for the `/users` endpoints.](docs/users-docs.md) 
(User list, user info, create user, manage user follower relationships.)

### /articles endpoints

[Click here to see documentation for the `/articles` endpoints.](docs/articles-docs.md)

### /tags endpoints

[Click here to see documentation for the `/tags` endpoints.](docs/tags-docs.md)