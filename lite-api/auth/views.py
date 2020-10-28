import logging

from requests.exceptions import HTTPError
from django.core.exceptions import SuspiciousOperation
from rest_framework import exceptions

from mozilla_django_oidc.utils import parse_www_authenticate_header
from mozilla_django_oidc.contrib.drf import OIDCAuthentication
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

LOGGER = logging.getLogger(__name__)


class AuthBackend(OIDCAuthenticationBackend):
    def get_or_create_user(self, claims):
        """Returns a User instance if 1 user is found. Creates a user if not found
        and configured to do so. Returns nothing if multiple users are matched."""

        # email based filtering
        users = self.filter_users_by_claims(claims)

        email = claims.get("email")

        if len(users) == 1:
            return self.update_user(users[0], claims)
        elif len(users) > 1:
            # In the rare case that two user accounts have the same email address,
            # bail. Randomly selecting one seems really wrong.
            msg = "Multiple users returned"
            raise SuspiciousOperation(msg)
        elif self.get_settings("OIDC_CREATE_USER", True):
            user = self.create_user(claims)
            return user
        else:
            LOGGER.debug(
                "Login failed: No user with email %s found, and "
                "OIDC_CREATE_USER is False",
                email,
            )
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

        if id_token == "None":
            return None

        claims = self.backend.verify_token(id_token)

        try:
            user = self.backend.get_or_create_user(claims)
        except HTTPError as exc:
            resp = exc.response

            # if the oidc provider returns 401, it means the token is invalid.
            # in that case, we want to return the upstream error message (which
            # we can get from the www-authentication header) in the response.
            if resp.status_code == 401 and "www-authenticate" in resp.headers:
                data = parse_www_authenticate_header(resp.headers["www-authenticate"])
                raise exceptions.AuthenticationFailed(data["error_description"])

            # for all other http errors, just re-raise the exception.
            raise
        except SuspiciousOperation as exc:
            LOGGER.info("Login failed: %s", exc)
            raise exceptions.AuthenticationFailed("Login failed")

        if not user:
            msg = "Login failed: No user found for the given access token."
            raise exceptions.AuthenticationFailed(msg)

        return user, id_token
