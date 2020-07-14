import json

from django.contrib.auth.models import User
from django.http import JsonResponse
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
