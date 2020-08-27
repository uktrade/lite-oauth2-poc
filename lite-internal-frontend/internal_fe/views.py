import os

from jwcrypto.jwk import JWK

from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from auth.utils import get_client, get_profile

import python_jwt as jwt


class Start(TemplateView):
    template_name = "internal_fe/start.html"


class Home(TemplateView):
    template_name = "internal_fe/home.html"
