from django.contrib.auth import get_user_model

from auth.utils import get_client, has_valid_token, get_profile


class AuthbrokerBackend:
    def authenticate(self, request, **kwargs):
        client = get_client(request)
        if not has_valid_token(client):
            return

        User = get_user_model()

        profile = get_profile(client)
        if not profile.get("email"):
            return

        user, created = User.objects.get_or_create(email=profile["email"])
        if created:
            user.set_unusable_password()
            user.save()

        return user


    def get_user(self, user_id):
        User = get_user_model()

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
