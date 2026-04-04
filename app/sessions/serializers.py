from rest_framework import serializers

from .models import Session, Speaker


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ("id", "name", "bio", "photo", "company", "website", "user")


class SessionSerializer(serializers.ModelSerializer):
    effective_capacity = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Session
        fields = (
            "id",
            "title",
            "description",
            "track",
            "speaker",
            "start_time",
            "end_time",
            "room",
            "session_type",
            "capacity",
            "effective_capacity",
        )

    def get_effective_capacity(self, obj):
        if obj.capacity is not None:
            return obj.capacity
        try:
            return obj.track.event.max_attendees
        except AttributeError:
            return None

    def validate(self, data):
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        track = data.get("track")

        instance = self.instance

        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError(
                    {"end_time": "End time must be after start time."}
                )

            if track:
                overlapping = Session.objects.filter(
                    track=track,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                )
                if instance:
                    overlapping = overlapping.exclude(pk=instance.pk)
                if overlapping.exists():
                    raise serializers.ValidationError(
                        "This session overlaps with an existing session in the same track."
                    )

        return data
