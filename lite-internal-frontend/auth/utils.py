import requests
import functools
from django.conf import settings


def create_user(data):
    response = requests.post(f"{settings.LITE_API_URL}/user-profile/", data=data)
    response.raise_for_status()
    return response.json()


def delete_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{settings.LITE_API_URL}/user-profile/", headers=headers
    )
    response.raise_for_status()


def get_user(user_id):
    response = requests.get(
        f"{settings.LITE_API_URL}/user-profile/", data={"id": user_id}
    )
    response.raise_for_status()
    return response.json()
