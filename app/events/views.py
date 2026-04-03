from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.accounts.permissions import IsEventOrganizer, IsOrganizer
from app.tracks.serializers import TrackSerializer

from .filters import EventFilter
from .models import Event
from .serializers import EventDetailSerializer, EventListSerializer, EventWriteSerializer


class EventViewSet(ModelViewSet):
    lookup_field = "slug"
    filterset_class = EventFilter
    search_fields = ["title", "description", "venue_name"]
    ordering_fields = ["start_date", "created_at", "title", "max_attendees"]
    ordering = ["-start_date"]

    def get_queryset(self):
        qs = Event.objects.select_related("organizer").prefetch_related("tracks")
        if not self.request.user.is_authenticated:
            return qs.filter(status=Event.Status.PUBLISHED)
        if self.action == "list":
            # Authenticated non-organizers see published; organizers see their own + published
            user = self.request.user
            if user.is_organizer:
                from django.db.models import Q
                return qs.filter(Q(status=Event.Status.PUBLISHED) | Q(organizer=user))
        return qs

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsOrganizer()]
        return [permissions.IsAuthenticated(), IsEventOrganizer()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return EventWriteSerializer
        if self.action == "retrieve":
            return EventDetailSerializer
        return EventListSerializer

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="tracks", permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def tracks(self, request, slug=None):
        event = self.get_object()
        if request.method == "GET":
            tracks = event.tracks.all()
            return Response(TrackSerializer(tracks, many=True).data)

        # POST — only the organizer can add tracks
        if event.organizer != request.user:
            return Response({"detail": "Only the event organizer can add tracks."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
