"""lite_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from lite_api.views import OAuthAuthorize
from django.contrib import admin
from django.urls import path, include

from lite_api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('auth.urls')),
    path('authbroker/', include('authbroker_client.urls')),
    path("login", views.LoginView.as_view(), name="user_login"),
    path("index", views.Home.as_view(), name="index"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('oauth-init', views.OAuthAuthorize.as_view(), name="oauth_init"),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("api/exporters", views.ExportersListView.as_view(), name="exporters"),
    path("user-profile/", views.UserProfileView.as_view(), name="profile"),
]
