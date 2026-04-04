from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from app.accounts.permissions import IsEventOrganizer

from .filters import SessionFilter
from .models import Session, Speaker
from .serializers import SessionSerializer, SpeakerSerializer


class SpeakerViewSet(ModelViewSet):
    serializer_class = SpeakerSerializer
    queryset = Speaker.objects.select_related("user")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class SessionViewSet(ModelViewSet):
    serializer_class = SessionSerializer
    filterset_class = SessionFilter
    ordering_fields = ["start_time", "session_type"]
    ordering = ["start_time"]

    def get_queryset(self):
        return Session.objects.select_related("track__event", "speaker")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsEventOrganizer()]

    def get_object(self):
        obj = super().get_object()
        obj.organizer = obj.track.event.organizer
        return obj
