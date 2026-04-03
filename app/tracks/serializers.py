from rest_framework import serializers

from .models import Track


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ("id", "event", "name", "description", "color")
        read_only_fields = ("event",)
