import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

logger = logging.getLogger(__name__)

from .models import Registration
from .serializers import RegistrationSerializer


class RegistrationViewSet(ModelViewSet):
    serializer_class = RegistrationSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Registration.objects.none()
        user = self.request.user
        if user.is_staff:
            return Registration.objects.select_related("event", "attendee").all()
        return Registration.objects.filter(attendee=user).select_related("event", "attendee")

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        registration = serializer.save()
        logger.info(
            "Registration %s: user=%s event=%s",
            registration.status,
            registration.attendee.email,
            registration.event.slug,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.attendee != request.user:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        instance.status = Registration.Status.CANCELLED
        instance.save(update_fields=["status"])
        logger.info("Registration cancelled: user=%s event=%s", request.user.email, instance.event.slug)
        return Response(RegistrationSerializer(instance, context={"request": request}).data)
