import os
import json

from jwcrypto.jwk import JWK
import requests

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from auth.utils import get_client, get_profile

import python_jwt as jwt


def get_api_response(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f'{settings.LITE_API_URL}/index', headers=headers)
    return response


def create_user(**data):
    response = requests.post(f'{settings.LITE_API_URL}/user-profile/', data=data)
    response.raise_for_status()

def delete_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f'{settings.LITE_API_URL}/user-profile/', headers=headers)
    response.raise_for_status()


class Home(TemplateView):
    template_name = "internal_fe/home.html"

    @property
    def api_bearer_token(self):
        if 'jwt' in self.request.session:
            return self.request.session['jwt']
        elif settings.TOKEN_SESSION_KEY in self.request.session:
            return self.request.session[settings.TOKEN_SESSION_KEY]['access_token']

    def get_context_data(self, **kwargs):
        if 'jwt' in self.request.session:
            is_authenticated = self.request.user.is_authenticated
            profile = self.session_user_details
        else:
            client = get_client(self.request)
            is_authenticated = client.authorized
            response = get_profile(client)
            profile = response.json() if response.status_code == 200 else {}
        return super().get_context_data(
            profile=json.dumps(profile, indent=4),
            api_response=get_api_response(self.api_bearer_token),
            is_authenticated=is_authenticated
        )

    @property
    def session_user_details(self):
        token = self.request.session['jwt']
        _, claim = jwt.process_jwt(token)
        return claim

    def post(self, request):
        if request.POST['action'] == 'delete':
            delete_user(token=self.api_bearer_token)
        elif request.POST['action'] == 'create':
            create_user(
                first_name=self.session_user_details['name'],
                last_name='',
                username=self.session_user_details['email'],
                email=self.session_user_details['email']
            )
        return redirect(reverse('home'))
