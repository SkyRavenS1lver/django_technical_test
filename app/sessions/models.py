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
        indexes = [
            models.Index(fields=["start_time"]),
            models.Index(fields=["session_type"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="session_end_after_start",
            )
        ]

    def __str__(self):
        return self.title

    def clean(self):
        from django.db.models.fields import DateTimeField as DTField
        dt = DTField()
        try:
            start = dt.to_python(self.start_time)
            end = dt.to_python(self.end_time)
        except (ValueError, TypeError):
            return  # let clean_fields() report the format error

        if start and end:
            if end <= start:
                raise ValidationError({"end_time": "End time must be after start time."})

            if self.track_id:
                overlapping = Session.objects.filter(
                    track_id=self.track_id,
                    start_time__lt=end,
                    end_time__gt=start,
                ).exclude(pk=self.pk)
                if overlapping.exists():
                    raise ValidationError(
                        {"start_time": "This session overlaps with an existing session in the same track."}
                    )
