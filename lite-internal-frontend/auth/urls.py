from django.urls import path

import auth.views

app_name = "auth"

urlpatterns = [
    path("login/", auth.views.oauth2_login, name="login"),
    path("callback/", auth.views.oauth2_callback, name="callback"),
]
