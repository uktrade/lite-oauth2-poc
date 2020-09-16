import secrets
import urllib.parse as urlparse
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes
from django.views.generic.base import RedirectView, View

from auth import utils


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return secrets.compare_digest(force_bytes(val1), force_bytes(val2))


def add_user_type_to_url(source_url, params):

    url_parts = list(urlparse.urlparse(source_url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlparse.urlunparse(url_parts)


class AuthView(RedirectView):
    """
    Auth wrapper which connects to api
    """

    def get_redirect_url(self, *args, **kwargs):
        authorization_url, state = utils.get_client(self.request).authorization_url(utils.AUTHORISATION_URL)

        self.request.session[utils.TOKEN_SESSION_KEY + "_oauth_state"] = state

        updated_url = add_user_type_to_url(authorization_url, {"user_type": "internal"})

        return updated_url


class AuthCallbackView(View):
    """
    Auth process for exporter, only called by 'great sso'
    """

    def get(self, request, *args, **kwargs):
        auth_code = request.GET.get("code", None)
        auth_state = request.GET.get("state", None)

        if not auth_code:
            return redirect(reverse_lazy("auth:login"))

        state = self.request.session.get(utils.TOKEN_SESSION_KEY + "_oauth_state", None)
        if not state:
            return HttpResponseServerError()

        if not constant_time_compare(auth_state, state):
            return HttpResponseServerError()

        client = utils.get_client(self.request)

        try:
            token = client.fetch_token(
                utils.TOKEN_URL, client_secret=settings.AUTHBROKER_CLIENT_SECRET, code=auth_code
            )

            self.request.session[utils.TOKEN_SESSION_KEY] = dict(token)

            del self.request.session[utils.TOKEN_SESSION_KEY + "_oauth_state"]

        except Exception:
            raise Exception

        return redirect(settings.LOGIN_REDIRECT_URL)
