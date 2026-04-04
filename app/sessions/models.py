from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Speaker(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    photo = models.ImageField(upload_to="speakers/", blank=True, null=True)
    company = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="speaker_profiles",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Session(models.Model):
    class SessionType(models.TextChoices):
        TALK = "talk", "Talk"
        WORKSHOP = "workshop", "Workshop"
        PANEL = "panel", "Panel"
        KEYNOTE = "keynote", "Keynote"

    title = models.CharField(max_length=255)
    description = models.TextField()
    track = models.ForeignKey(
        "tracks.Track",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    speaker = models.ForeignKey(
        Speaker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    room = models.CharField(max_length=255, blank=True)
    session_type = models.CharField(
        max_length=20, choices=SessionType.choices, default=SessionType.TALK
    )
    capacity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="session_end_after_start",
            )
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})

        if self.track_id and self.start_time and self.end_time:
            overlapping = Session.objects.filter(
                track_id=self.track_id,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError(
                    "This session overlaps with an existing session in the same track."
                )
