from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from app.events.models import Event
from app.tracks.models import Track

User = get_user_model()

PASSWORD = "testpass123"


def _make_user(email, is_organizer=False):
    return User.objects.create_user(email=email, name="Test", password=PASSWORD, is_organizer=is_organizer)


def _auth(client, user):
    res = client.post("/api/v1/auth/login/", {"email": user.email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def _make_event(organizer, max_attendees=100):
    now = timezone.now()
    return Event.objects.create(
        title="Session Test Event",
        description="desc",
        start_date=now,
        end_date=now + timezone.timedelta(days=1),
        venue_name="Venue",
        venue_address="Addr",
        max_attendees=max_attendees,
        organizer=organizer,
        status=Event.Status.PUBLISHED,
    )


def _make_track(event, name="Main Track"):
    return Track.objects.create(event=event, name=name, color="#6366f1")


class SessionAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organizer = _make_user("org@example.com", is_organizer=True)
        cls.attendee = _make_user("att@example.com", is_organizer=False)
        cls.event = _make_event(cls.organizer)
        cls.track = _make_track(cls.event, "Main")
        cls.track2 = _make_track(cls.event, "Side")

        # A fixed base time for scheduling
        cls.base = timezone.now().replace(microsecond=0) + timezone.timedelta(days=1)

    def setUp(self):
        self.client = APIClient()

    def _payload(self, track_pk, start_offset_h=0, duration_h=1, **kwargs):
        start = self.base + timezone.timedelta(hours=start_offset_h)
        end = start + timezone.timedelta(hours=duration_h)
        data = {
            "title": "A Session",
            "description": "desc",
            "track": track_pk,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "session_type": "talk",
        }
        data.update(kwargs)
        return data

    def test_create_session(self):
        _auth(self.client, self.organizer)
        res = self.client.post("/api/v1/sessions/", self._payload(self.track.pk, start_offset_h=0), format="json")
        self.assertEqual(res.status_code, 201)

    def test_create_non_organizer(self):
        _auth(self.client, self.attendee)
        res = self.client.post("/api/v1/sessions/", self._payload(self.track.pk, start_offset_h=2), format="json")
        self.assertEqual(res.status_code, 403)

    def test_overlap_same_track(self):
        _auth(self.client, self.organizer)
        # First session: 10:00 – 11:00
        self.client.post("/api/v1/sessions/", self._payload(self.track.pk, start_offset_h=10, duration_h=1), format="json")
        # Second session: 10:30 – 11:30 — overlaps
        res = self.client.post("/api/v1/sessions/", self._payload(self.track.pk, start_offset_h=10, duration_h=1, title="Overlap"), format="json")
        self.assertEqual(res.status_code, 400)

    def test_no_overlap_different_tracks(self):
        _auth(self.client, self.organizer)
        self.client.post("/api/v1/sessions/", self._payload(self.track.pk, start_offset_h=20, duration_h=1), format="json")
        res = self.client.post("/api/v1/sessions/", self._payload(self.track2.pk, start_offset_h=20, duration_h=1), format="json")
        self.assertEqual(res.status_code, 201)

    def test_back_to_back_allowed(self):
        _auth(self.client, self.organizer)
        # Session A: 30:00 – 31:00
        self.client.post("/api/v1/sessions/", self._payload(self.track.pk, start_offset_h=30, duration_h=1), format="json")
        # Session B: 31:00 – 32:00 — starts exactly when A ends
        res = self.client.post("/api/v1/sessions/", self._payload(self.track.pk, start_offset_h=31, duration_h=1, title="Back to Back"), format="json")
        self.assertEqual(res.status_code, 201)

    def test_end_before_start(self):
        _auth(self.client, self.organizer)
        start = self.base + timezone.timedelta(hours=40)
        end = start - timezone.timedelta(hours=1)
        res = self.client.post("/api/v1/sessions/", {
            "title": "Bad",
            "description": "x",
            "track": self.track.pk,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "session_type": "talk",
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_effective_capacity_inherits(self):
        _auth(self.client, self.organizer)
        res = self.client.post("/api/v1/sessions/", self._payload(self.track.pk, start_offset_h=50, duration_h=1), format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["effective_capacity"], self.event.max_attendees)
