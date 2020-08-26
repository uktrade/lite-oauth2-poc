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

    def dispatch(self, request):
        if "jwt" in request.GET:
            request.session["jwt"] = self.request.GET["jwt"]
            return redirect(request.path)
        return super().dispatch(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "jwt" in self.request.session:
            _, context["profile"] = jwt.process_jwt(self.request.session["jwt"])
        return context
