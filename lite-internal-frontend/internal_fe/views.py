import json
import requests

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from auth.utils import delete_user, create_user

import python_jwt as jwt


def get_api_response(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{settings.LITE_API_URL}/index", headers=headers)
    return response


class Home(TemplateView):
    template_name = "internal_fe/home.html"

    @property
    def api_bearer_token(self):
        if "oidc_id_token" in self.request.session:
            return self.request.session["oidc_id_token"]

        return ""

    def get_context_data(self, **kwargs):
        profile = {}
        is_authenticated = False
        if "oidc_id_token" in self.request.session:
            is_authenticated = self.request.user.is_authenticated
            profile = self.session_user_details

        return super().get_context_data(
            profile=json.dumps(profile, indent=4),
            api_response=get_api_response(self.api_bearer_token),
            is_authenticated=is_authenticated,
        )

    @property
    def session_user_details(self):
        token = self.request.session["oidc_id_token"]
        _, claim = jwt.process_jwt(token)
        return claim

    def post(self, request):
        if request.POST["action"] == "delete":
            delete_user(token=self.api_bearer_token)
        elif request.POST["action"] == "create":
            create_user(
                first_name=self.session_user_details["name"],
                last_name="",
                username=self.session_user_details["email"],
                email=self.session_user_details["email"],
            )
        return redirect(reverse("home"))
