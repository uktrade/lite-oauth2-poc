"""
Django settings for lite_api project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from django.urls import reverse_lazy
from environ import Env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENV_FILE = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_FILE):
    Env.read_env(ENV_FILE)

env = Env(
    DEBUG=(bool, False),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.sites',
    'rest_framework',
    'oauth2_provider',
    'mozilla_django_oidc',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        # 'mozilla_django_oidc.contrib.drf.OIDCAuthentication',
        'auth.views.DRFAuthBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


AUTHENTICATION_BACKENDS = (
    'auth.views.AuthBackend',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lite_api.urls'

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", True)
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME", default="api")

# requests_oauthlib
OAUTHLIB_INSECURE_TRANSPORT = env("OAUTHLIB_INSECURE_TRANSPORT", default=0)

FEATURE_ENFORCE_STAFF_SSO_ENABLED = env.bool('FEATURE_ENFORCE_STAFF_SSO_ENABLED', default=False)
# authbroker config
if FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    INSTALLED_APPS.append("authbroker_client",)

    AUTHBROKER_URL = env("AUTHBROKER_URL")
    AUTHBROKER_CLIENT_ID = env("AUTHBROKER_CLIENT_ID")
    AUTHBROKER_CLIENT_SECRET = env("AUTHBROKER_CLIENT_SECRET")
    AUTHBROKER_TOKEN_SESSION_KEY = env("AUTHBROKER_TOKEN_SESSION_KEY")
    AUTHBROKER_STAFF_SSO_SCOPE = env('AUTHBROKER_STAFF_SSO_SCOPE')

    DIRECTORY_SSO_AUTHBROKER_URL = env("DIRECTORY_SSO_AUTHBROKER_URL")
    DIRECTORY_SSO_AUTHBROKER_CLIENT_ID = env("DIRECTORY_SSO_AUTHBROKER_CLIENT_ID")
    DIRECTORY_SSO_AUTHBROKER_CLIENT_SECRET = env("DIRECTORY_SSO_AUTHBROKER_CLIENT_SECRET")

    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        "auth.backends.AuthbrokerBackend",
        "authbroker_client.backends.AuthbrokerBackend",
    ]

    LOGIN_URL = reverse_lazy("user_login")
    LOGIN_REDIRECT_URL = reverse_lazy("oauth_init")
else:
    LOGIN_URL = "/accounts/login/"
    LOGIN_REDIRECT_URL = '/api/exporters'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lite_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': env.db(),
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

SITE_ID = 1

TOKEN_SESSION_KEY = env.str('TOKEN_SESSION_KEY')

# OIDC
OIDC_RP_CLIENT_ID = env.str('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = env.str('OIDC_RP_CLIENT_SECRET')
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_STORE_ID_TOKEN = True
OIDC_RP_SCOPES = 'openid email first_name last_name'
OIDC_USE_NONCE = False
OIDC_CREATE_USER = True

OIDC_PROVIDER_URL = env.str('OIDC_PROVIDER_URL')
OIDC_OP_JWKS_ENDPOINT = f'{OIDC_PROVIDER_URL}/.well-known/jwks.json'
OIDC_OP_AUTHORIZATION_ENDPOINT = f'{OIDC_PROVIDER_URL}/authorize'
OIDC_OP_TOKEN_ENDPOINT = f'{OIDC_PROVIDER_URL}/oauth/token'
OIDC_OP_USER_ENDPOINT = f'{OIDC_PROVIDER_URL}/userinfo'

OIDC_DRF_AUTH_BACKEND = 'auth.views.AuthBackend'
