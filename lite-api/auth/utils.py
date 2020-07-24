import functools
from urllib.parse import urljoin

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from requests_oauthlib import OAuth2Session


TOKEN_SESSION_KEY = "_authbroker_token"
AUTHBROKER_URL = settings.DIRECTORY_SSO_AUTHBROKER_URL
AUTHBROKER_CLIENT_ID = settings.DIRECTORY_SSO_AUTHBROKER_CLIENT_ID
AUTHBROKER_CLIENT_SECRET = settings.DIRECTORY_SSO_AUTHBROKER_CLIENT_SECRET
PROFILE_URL = urljoin(AUTHBROKER_URL, "sso/oauth2/user-profile/v1/")
INTROSPECT_URL = urljoin(AUTHBROKER_URL, "sso/oauth2/introspect/")
TOKEN_URL = urljoin(AUTHBROKER_URL, "sso/oauth2/token/")
AUTHORISATION_URL = urljoin(AUTHBROKER_URL, "sso/oauth2/authorize/")
SCOPE = "profile"
TOKEN_CHECK_PERIOD_SECONDS = 60


def get_client(request, **kwargs):
    callback_url = reverse("auth:callback")
    redirect_uri = request.build_absolute_uri(callback_url)

    return OAuth2Session(
        AUTHBROKER_CLIENT_ID,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        token=request.session.get(TOKEN_SESSION_KEY, None),
        **kwargs
    )


def has_valid_token(client):
    """Does the session have a valid token?"""

    return client.authorized


def get_profile(client):
    return client.get(PROFILE_URL).json()
