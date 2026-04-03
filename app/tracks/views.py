from rest_framework import permissions
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from app.accounts.permissions import IsEventOrganizer

from .models import Track
from .serializers import TrackSerializer


class TrackViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = TrackSerializer

    def get_queryset(self):
        return Track.objects.select_related("event")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsEventOrganizer()]

    def get_object(self):
        obj = super().get_object()
        obj.organizer = obj.event.organizer
        return obj
