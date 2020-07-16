import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import RedirectView
from requests_oauthlib import OAuth2Session
from rest_framework import status
from rest_framework.generics import GenericAPIView
from oauth2_provider.views import ProtectedResourceView
from urllib.parse import urljoin

from lite_api import serializers
from lite_api.settings import env

TOKEN_SESSION_KEY = env("TOKEN_SESSION_KEY")
AUTHBROKER_URL = env("AUTHORIZATION_SERVER")
AUTHORISATION_URL = urljoin(AUTHBROKER_URL, "o/authorize/")
API_CLIENT_ID = env("API_CLIENT_ID")
API_CLIENT_CALLBACK_URL = env("API_CLIENT_CALLBACK_URL")


def get_oauth_client(request, client_id, callback_url, **kwargs):
    redirect_uri = request.build_absolute_uri(callback_url)

    return OAuth2Session(
        client_id,
        redirect_uri=redirect_uri,
        token=request.session.get(TOKEN_SESSION_KEY, None),
        **kwargs,
    )


class OAuthAuthorize(RedirectView):
    def get_redirect_url(self, *args, **kwargs):

        authorization_url, state = get_oauth_client(
            self.request, API_CLIENT_ID, API_CLIENT_CALLBACK_URL
        ).authorization_url(AUTHORISATION_URL)

        self.request.session[TOKEN_SESSION_KEY + "_oauth_state"] = state

        return authorization_url


class Home(ProtectedResourceView, GenericAPIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            data={"status": "Hello World !!"}, status=status.HTTP_200_OK,
        )


class ExportersListView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_active=True, is_superuser=False)
        serializer = serializers.UserSerializer(users, many=True)

        return JsonResponse(
            data={"exporters": json.dumps(serializer.data)}, status=status.HTTP_200_OK,
        )


class UserProfileView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            json.dumps(
                {
                    "id": request.resource_owner.id,
                    "username": request.resource_owner.username,
                    "email": request.resource_owner.email,
                    "first_name": request.resource_owner.first_name,
                    "last_name": request.resource_owner.last_name,
                }
            ),
            content_type="application/json",
        )
