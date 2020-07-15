from django.shortcuts import render
from django.views.generic import TemplateView

from auth.utils import get_client, get_profile


class Start(TemplateView):
    def get(self, request, **kwargs):
        return render(request, "start.html")


class Home(TemplateView):
    def get(self, request, **kwargs):
        profile = get_profile(get_client(self.request))
        return render(request, "home.html", context={"profile": profile})
