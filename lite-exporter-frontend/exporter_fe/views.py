from django.shortcuts import render
from django.views.generic import TemplateView




class Home(TemplateView):
    def get(self, request, **kwargs):
        print(f"==> {request.user.is_authenticated}")
        return render(request, "start.html")