from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from app.accounts.permissions import IsEventOrganizer

from .models import Track
from .serializers import TrackSerializer


class TrackViewSet(ModelViewSet):
    serializer_class = TrackSerializer

    def get_queryset(self):
        return Track.objects.select_related("event")

    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsEventOrganizer()]

    def get_object(self):
        obj = super().get_object()
        # Attach event to obj for IsEventOrganizer check
        obj.organizer = obj.event.organizer
        return obj
