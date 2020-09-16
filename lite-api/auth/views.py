import secrets
import logging

from requests.exceptions import HTTPError

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.views.generic.base import RedirectView, View
from django.shortcuts import redirect
from django.utils.encoding import force_bytes
from django.core.exceptions import SuspiciousOperation

from rest_framework import exceptions

from mozilla_django_oidc.utils import parse_www_authenticate_header
from mozilla_django_oidc.contrib.drf import OIDCAuthentication
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from auth.utils import (
    get_client,
    AUTHORISATION_URL,
    TOKEN_URL,
    TOKEN_SESSION_KEY,
    AUTHBROKER_CLIENT_SECRET,
)

LOGGER = logging.getLogger(__name__)


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return secrets.compare_digest(force_bytes(val1), force_bytes(val2))


class AuthView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        authorization_url, state = get_client(self.request).authorization_url(AUTHORISATION_URL)

        self.request.session[TOKEN_SESSION_KEY + "_oauth_state"] = state

        return authorization_url


class AuthCallbackView(View):
    def get(self, request, *args, **kwargs):

        auth_code = request.GET.get("code", None)
        auth_state = request.GET.get("state", None)

        if not auth_code:
            return HttpResponseBadRequest()

        state = self.request.session.get(TOKEN_SESSION_KEY + "_oauth_state", None)
        if not state:
            return HttpResponseServerError()

        if not constant_time_compare(auth_state, state):
            return HttpResponseServerError()

        try:
            token = get_client(self.request).fetch_token(
                TOKEN_URL, client_secret=AUTHBROKER_CLIENT_SECRET, code=auth_code,
            )

            self.request.session[TOKEN_SESSION_KEY] = dict(token)

            del self.request.session[TOKEN_SESSION_KEY + "_oauth_state"]

        # NOTE: the BaseException will be removed or narrowed at a later date. The try/except block is
        # here due to reports of the app raising a 500 if the url is copied.  Current theory is that
        # somehow the url with the authcode is being copied, which would cause `fetch_token` to raise
        # an exception. However, looking at the fetch_code method, I'm not entirely sure what exceptions it
        # would raise in this instance.
        except BaseException:
            raise BaseException

        # create the user
        user = authenticate(request)
        user.backend = "auth.backends.AuthbrokerBackend"

        if user is not None:
            login(request, user)

        return redirect(getattr(settings, "LOGIN_REDIRECT_URL", "/"))


class AuthBackend(OIDCAuthenticationBackend):

    def get_or_create_user(self, claims):
        """Returns a User instance if 1 user is found. Creates a user if not found
        and configured to do so. Returns nothing if multiple users are matched."""

        # email based filtering
        users = self.filter_users_by_claims(claims)

        email = claims.get('email')

        if len(users) == 1:
            return self.update_user(users[0], claims)
        elif len(users) > 1:
            # In the rare case that two user accounts have the same email address,
            # bail. Randomly selecting one seems really wrong.
            msg = 'Multiple users returned'
            raise SuspiciousOperation(msg)
        elif self.get_settings('OIDC_CREATE_USER', True):
            user = self.create_user(claims)
            return user
        else:
            LOGGER.debug('Login failed: No user with email %s found, and '
                         'OIDC_CREATE_USER is False', email)
            return None


class DRFAuthBackend(OIDCAuthentication):
    def authenticate(self, request, **kwargs):

        """
        Authenticate the request and return a tuple of (user, token) or None
        if there was no authentication attempt.
        """
        id_token = self.get_access_token(request)

        # get JWT, then verify

        if not id_token:
            return None

        claims = self.backend.verify_token(id_token)

        try:
            user = self.backend.get_or_create_user(claims)
        except HTTPError as exc:
            resp = exc.response

            # if the oidc provider returns 401, it means the token is invalid.
            # in that case, we want to return the upstream error message (which
            # we can get from the www-authentication header) in the response.
            if resp.status_code == 401 and 'www-authenticate' in resp.headers:
                data = parse_www_authenticate_header(resp.headers['www-authenticate'])
                raise exceptions.AuthenticationFailed(data['error_description'])

            # for all other http errors, just re-raise the exception.
            raise
        except SuspiciousOperation as exc:
            LOGGER.info('Login failed: %s', exc)
            raise exceptions.AuthenticationFailed('Login failed')

        if not user:
            msg = 'Login failed: No user found for the given access token.'
            raise exceptions.AuthenticationFailed(msg)

        return user, id_token
