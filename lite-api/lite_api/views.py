import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from oauth2_provider.views import ProtectedResourceView

from lite_api import serializers


class ExportersListView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_active=True, is_superuser=False)
        serializer = serializers.UserSerializer(users, many=True)

        return JsonResponse(
            data={"exporters": json.dumps(serializer.data)}, status=status.HTTP_200_OK,
        )


class UserProfileView(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            json.dumps(
                {
                    "id": request.resource_owner.id,
                    "username": request.resource_owner.username,
                    "email": request.resource_owner.email,
                    "first_name": request.resource_owner.first_name,
                    "last_name": request.resource_owner.last_name,
                }
            ),
            content_type="application/json",
        )
