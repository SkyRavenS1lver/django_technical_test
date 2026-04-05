from rest_framework import serializers

from app.events.models import Event

from .models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(slug_field="slug", queryset=Event.objects.all())
    attendee = serializers.StringRelatedField(read_only=True)
    status = serializers.ChoiceField(choices=Registration.Status.choices, read_only=True)

    class Meta:
        model = Registration
        fields = ("id", "event", "attendee", "registered_at", "status")
        read_only_fields = ("attendee", "registered_at")

    def validate(self, attrs):
        user = self.context["request"].user
        event = attrs["event"]
        if Registration.objects.filter(attendee=user, event=event).exists():
            raise serializers.ValidationError(
                {"event": "You are already registered for this event."}
            )
        confirmed_count = event.registrations.filter(status=Registration.Status.CONFIRMED).count()
        attrs["status"] = (
            Registration.Status.WAITLISTED
            if confirmed_count >= event.max_attendees
            else Registration.Status.CONFIRMED
        )
        return attrs

    def create(self, validated_data):
        validated_data["attendee"] = self.context["request"].user
        return super().create(validated_data)
