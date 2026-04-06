import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.accounts.permissions import IsEventOrganizer, IsOrganizer
from app.sessions.serializers import SessionSerializer
from app.tracks.serializers import TrackSerializer

from .filters import EventFilter
from .models import Event
from .serializers import EventDetailSerializer, EventListSerializer, EventWriteSerializer

logger = logging.getLogger(__name__)

_EVENTS_VERSION_KEY = "events:version"


def _event_cache_version():
    return cache.get(_EVENTS_VERSION_KEY, 0)


def _invalidate_event_list_cache():
    cache.set(_EVENTS_VERSION_KEY, _event_cache_version() + 1, timeout=None)


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

    def list(self, request, *args, **kwargs):
        # Only cache unauthenticated requests
        if request.user.is_authenticated:
            return super().list(request, *args, **kwargs)

        version = _event_cache_version()
        cache_key = f"events:list:{version}:{request.get_full_path()}"
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug("Event list cache hit: %s", cache_key)
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        logger.debug("Event list cached: %s", cache_key)
        return response

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
        event = serializer.save(organizer=self.request.user)
        _invalidate_event_list_cache()
        logger.info("Event created: '%s' by %s", event.title, self.request.user.email)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        _invalidate_event_list_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        _invalidate_event_list_cache()

    @action(detail=True, methods=["get", "post"], url_path="tracks", permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def tracks(self, request, slug=None, **kwargs):
        event = self.get_object()
        if request.method == "GET":
            tracks = event.tracks.all()
            return Response(TrackSerializer(tracks, many=True).data)

        # POST — only the organizer can add tracks
        if event.organizer != request.user:
            return Response({"detail": "Only the event organizer can add tracks."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from django.db import IntegrityError
        try:
            serializer.save(event=event)
        except IntegrityError:
            return Response(
                {"name": ["A track with this name already exists for this event."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="sessions", permission_classes=[permissions.AllowAny])
    def sessions(self, request, slug=None, **kwargs):
        event = self.get_object()
        from app.sessions.models import Session
        sessions = Session.objects.filter(
            track__event=event
        ).select_related("track", "speaker").order_by("start_time")
        return Response(SessionSerializer(sessions, many=True).data)

    @action(detail=True, methods=["post"], url_path="register", permission_classes=[permissions.IsAuthenticated])
    def register(self, request, slug=None, **kwargs):
        event = self.get_object()
        from app.registrations.serializers import RegistrationSerializer
        serializer = RegistrationSerializer(
            data={"event": event.slug},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="registrations", permission_classes=[permissions.IsAuthenticated, IsEventOrganizer])
    def registrations(self, request, slug=None, **kwargs):
        event = self.get_object()
        from app.registrations.models import Registration
        from app.registrations.serializers import RegistrationSerializer
        regs = Registration.objects.filter(event=event).select_related("attendee").order_by("-registered_at")
        return Response(RegistrationSerializer(regs, many=True, context={"request": request}).data)
