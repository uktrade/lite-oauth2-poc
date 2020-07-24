# Example Exporter frontend

Example frontend to communicate with API and to demonstrate authentication and authorization.
Staff-SSO is used for authentication and authorization is handled using OAuth2.

API is acting as both Resource server and Authorization server.

## Setup

Example environment variables are provided in `local.env`. Create a file `.env` and update them with real values.

```

# Register an application in the API admin and update the client_id and client_secret below
#
# Auth
AUTHBROKER_CLIENT_ID=example-client-id
AUTHBROKER_CLIENT_SECRET=example-client-secret
AUTHBROKER_URL=http://localhost:8000
TOKEN_SESSION_KEY=

# requests_oauthlib
OAUTHLIB_INSECURE_TRANSPORT=1

```
