from allauth.account.adapter import DefaultAccountAdapter

from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):

    def is_safe_url(self, url):
        if url:
            return url_has_allowed_host_and_scheme(url, allowed_hosts=settings.ALLOWED_REDIRECT_HOSTS)