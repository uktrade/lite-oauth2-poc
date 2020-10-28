from django.http import JsonResponse
from rest_framework import permissions, generics, mixins, status

from lite_api import serializers


class Home(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            data={"status": f"Hello {request.user.email}"},
            status=status.HTTP_200_OK,
        )


class RetrieveCreateDestroyUser(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.UserSerializer
    http_method_names = ["get", "post", "delete"]

    def get(self, request):
        return self.retrieve(request)

    def post(self, request):
        return self.create(request)

    def delete(self, request):
        self.get_object().delete()
        return JsonResponse(data={}, status=204)

    def get_object(self):
        return self.request.user
