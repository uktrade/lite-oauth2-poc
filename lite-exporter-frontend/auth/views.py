import urllib.parse as urlparse

from urllib.parse import urlencode
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, View

from auth.utils import get_client, AUTHORISATION_URL, TOKEN_SESSION_KEY, TOKEN_URL, get_profile


def add_user_type_to_url(source_url, params):

    url_parts = list(urlparse.urlparse(source_url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    print(urlparse.urlunparse(url_parts))
    return urlparse.urlunparse(url_parts)


class AuthView(RedirectView):
    """
    Auth wrapper which connects to api
    """

    def get_redirect_url(self, *args, **kwargs):
        authorization_url, state = get_client(self.request).authorization_url(AUTHORISATION_URL)

        self.request.session[TOKEN_SESSION_KEY + "_oauth_state"] = state

        updated_url = add_user_type_to_url(authorization_url, {"user_type": "exporter"})

        return updated_url


class AuthCallbackView(View):
    """
    Auth process for exporter, only called by 'great sso'
    """

    def get(self, request, *args, **kwargs):
        auth_code = request.GET.get("code", None)
        if not auth_code:
            return redirect(reverse_lazy("auth:login"))

        state = request.GET.get("state", None)

        if not state:
            return HttpResponseServerError()

        client = get_client(self.request)

        try:
            token = client.fetch_token(
                TOKEN_URL, client_secret=settings.AUTHBROKER_CLIENT_SECRET, code=auth_code
            )

            self.request.session[TOKEN_SESSION_KEY] = dict(token)

        except Exception:
            raise Exception

        return redirect(getattr(settings, "LOGIN_REDIRECT_URL", "/"))
