from django.contrib.auth import get_user_model
from rest_framework import serializers

from app.tracks.serializers import TrackSerializer

from .models import Event

User = get_user_model()


class EventListSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source="organizer.name", read_only=True)

    class Meta:
        model = Event
        fields = (
            "id", "title", "slug", "start_date", "end_date",
            "venue_name", "max_attendees", "status", "banner", "organizer_name",
        )


class EventDetailSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source="organizer.name", read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = (
            "id", "title", "slug", "description", "start_date", "end_date",
            "venue_name", "venue_address", "max_attendees", "status",
            "banner", "organizer_name", "tracks", "created_at", "updated_at",
        )


class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "title", "description", "start_date", "end_date",
            "venue_name", "venue_address", "max_attendees", "status", "banner",
        )

    def validate(self, data):
        start = data.get("start_date", getattr(self.instance, "start_date", None))
        end = data.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and end <= start:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})
        return data

    def create(self, validated_data):
        validated_data["organizer"] = self.context["request"].user
        return super().create(validated_data)
