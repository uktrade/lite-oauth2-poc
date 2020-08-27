import os

from jwcrypto.jwk import JWK
import requests

from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from auth.utils import get_client, get_profile

import python_jwt as jwt


def get_api_response(jwt):
    headers = {"Authorization": f"Bearer {jwt}"}
    response = requests.get('http://localhost:8000/', headers=headers)
    return response


class Start(TemplateView):
    template_name = "internal_fe/start.html"


class Home(TemplateView):
    template_name = "internal_fe/home.html"

    def get_context_data(self, **kwargs):
        jwt = self.request.session.get('jwt', '')
        api_says = get_api_response(jwt)
        return super().get_context_data(api_says=api_says)