from django.apps import AppConfig

from allauth.socialaccount.signals import social_account_added, social_account_updated

from lite_api.signals import redirect_with_jwt


class LiteApiConfig(AppConfig):
    name = 'lite_api'

    def ready(self):
        social_account_updated.connect(redirect_with_jwt)
        social_account_added.connect(redirect_with_jwt)
