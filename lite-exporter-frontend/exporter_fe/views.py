import os

from re import template
from django.shortcuts import render
from django.views.generic import TemplateView

from auth.utils import get_client, get_profile


class Start(TemplateView):
    template_name = os.path.join("exporter_fe", "start.html")


class Home(TemplateView):
    template_name = os.path.join("exporter_fe", "home.html")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_profile(get_client(self.request))
        return context
