from django.contrib.auth.views import LogoutView
from django.urls import path

import auth.views

app_name = "auth"

urlpatterns = [
    path("login/", auth.views.AuthView.as_view(), name="login"),
    path("callback", auth.views.AuthCallbackView.as_view(), name="callback"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
