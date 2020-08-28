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
    response = requests.post(f'{settings.LITE_API_URL}/user/', data=data)
    response.raise_for_status()

def delete_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f'{settings.LITE_API_URL}/user/', headers=headers)
    response.raise_for_status()


class Start(TemplateView):
    template_name = "internal_fe/start.html"


class Home(TemplateView):
    template_name = "internal_fe/home.html"

    def get_context_data(self, **kwargs):
        if 'jwt' not in self.request.session:
            profile = get_profile(get_client(self.request))
            return super().get_context_data(profile=json.dumps(profile, indent=4))
        else:
            token = self.request.session['jwt']
            api_response = get_api_response(token)
            return super().get_context_data(
                profile=json.dumps(self.session_user_details, indent=4),
                api_response=api_response
            )

    @property
    def session_user_details(self):
        if 'jwt' not in self.request.session:
            return {}
        token = self.request.session['jwt']
        _, claim = jwt.process_jwt(token)
        return claim

    def post(self, request):
        if request.POST['action'] == 'delete':
            delete_user(token=self.request.session['jwt'])
        elif request.POST['action'] == 'create':
            create_user(
                first_name=self.session_user_details['name'],
                last_name='',
                username=self.session_user_details['email'],
                email=self.session_user_details['email']
            )
        return redirect(reverse('home'))
