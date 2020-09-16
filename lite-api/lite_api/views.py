import json
from urllib.parse import urljoin, urlencode, urlparse, parse_qsl, urlunparse

from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic.base import RedirectView
from requests_oauthlib import OAuth2Session
from rest_framework import permissions, generics, mixins, status

from lite_api import serializers
from lite_api.settings import env


TOKEN_SESSION_KEY = env("TOKEN_SESSION_KEY")
AUTHORIZATION_SERVER = env("AUTHORIZATION_SERVER")
AUTHORISATION_URL = urljoin(AUTHORIZATION_SERVER, "o/authorize/")

LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL

EXPORTER_FE_API_CLIENT_ID = env("EXPORTER_FE_API_CLIENT_ID")
EXPORTER_FE_API_CLIENT_CALLBACK_URL = env("EXPORTER_FE_API_CLIENT_CALLBACK_URL")
INTERNAL_FE_API_CLIENT_ID = env("INTERNAL_FE_API_CLIENT_ID")
INTERNAL_FE_API_CLIENT_CALLBACK_URL = env("INTERNAL_FE_API_CLIENT_CALLBACK_URL")


def add_params_to_url(source_url, params):

    url_parts = list(urlparse(source_url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)


def get_oauth_client(request, state, client_id, callback_url, **kwargs):
    redirect_uri = request.build_absolute_uri(callback_url)

    return OAuth2Session(
        client_id,
        redirect_uri=redirect_uri,
        state=state,
        token=request.session.get(TOKEN_SESSION_KEY, None),
        **kwargs,
    )


class OAuthAuthorize(RedirectView):
    def get_redirect_url(self, *args, **kwargs):

        client_id = self.request.GET["client_id"]
        client_callback_url = self.request.GET["client_callback_url"]
        state = self.request.GET["state"]

        authorization_url, _state = get_oauth_client(
            self.request, state, client_id, client_callback_url
        ).authorization_url(AUTHORISATION_URL)

        self.request.session[TOKEN_SESSION_KEY + "_oauth_state"] = state

        return authorization_url


class LoginView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):

        url_parts = list(urlparse(self.request.GET["next"]))
        query = dict(parse_qsl(url_parts[4]))

        # Assume exporter if the param is omitted
        user_type = query.get("user_type", "exporter")
        if user_type == "exporter":
            settings.LOGIN_REDIRECT_URL = add_params_to_url(
                reverse("oauth_init"),
                {
                    "client_id": EXPORTER_FE_API_CLIENT_ID,
                    "client_callback_url": EXPORTER_FE_API_CLIENT_CALLBACK_URL,
                    "state": query.get("state"),
                },
            )
            return reverse("auth:login")
        elif user_type == "internal":
            settings.LOGIN_REDIRECT_URL = add_params_to_url(
                reverse("oauth_init"),
                {
                    "client_id": INTERNAL_FE_API_CLIENT_ID,
                    "client_callback_url": INTERNAL_FE_API_CLIENT_CALLBACK_URL,
                    "state": query.get("state"),
                },
            )
            return reverse("authbroker_client:login")
        else:
            return reverse("login")


class Home(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            data={"status": f"Hello {request.user.email}"}, status=status.HTTP_200_OK,
        )


class RetrieveCreateDestroyUser(mixins.RetrieveModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.UserSerializer
    http_method_names = ['get', 'post', 'delete']

    def get(self, request):
        return self.retrieve(request)

    def post(self, request):
        return self.create(request)

    def delete(self, request):
        self.get_object().delete()
        return JsonResponse(data={}, status=204)

    def get_object(self):
        return self.request.user


class ExportersListView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_active=True, is_superuser=False)
        serializer = serializers.UserSerializer(users, many=True)

        return JsonResponse(
            data={"exporters": json.dumps(serializer.data)}, status=status.HTTP_200_OK,
        )
