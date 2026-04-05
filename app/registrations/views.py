from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Registration
from .serializers import RegistrationSerializer


class RegistrationViewSet(ModelViewSet):
    serializer_class = RegistrationSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Registration.objects.select_related("event", "attendee").all()
        return Registration.objects.filter(attendee=user).select_related("event", "attendee")

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.attendee != request.user:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        instance.status = Registration.Status.CANCELLED
        instance.save(update_fields=["status"])
        return Response(RegistrationSerializer(instance, context={"request": request}).data)
