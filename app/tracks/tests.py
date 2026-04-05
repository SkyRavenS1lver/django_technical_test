from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from app.events.models import Event

User = get_user_model()

PASSWORD = "testpass123"


def _make_user(email, is_organizer=False):
    return User.objects.create_user(email=email, name="Test", password=PASSWORD, is_organizer=is_organizer)


def _auth(client, user):
    res = client.post("/api/v1/auth/login/", {"email": user.email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def _make_event(organizer, title="Track Test Event"):
    now = timezone.now()
    return Event.objects.create(
        title=title,
        description="desc",
        start_date=now,
        end_date=now + timezone.timedelta(hours=4),
        venue_name="Venue",
        venue_address="Addr",
        max_attendees=50,
        organizer=organizer,
        status=Event.Status.PUBLISHED,
    )


class TrackAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organizer = _make_user("org@example.com", is_organizer=True)
        cls.other_org = _make_user("other@example.com", is_organizer=True)
        cls.attendee = _make_user("att@example.com", is_organizer=False)
        cls.event = _make_event(cls.organizer)
        cls.event2 = _make_event(cls.other_org, title="Other Event")

    def setUp(self):
        self.client = APIClient()

    def _url(self, event=None):
        e = event or self.event
        return f"/api/v1/events/{e.slug}/tracks/"

    def _payload(self, name="Backend"):
        return {"name": name, "color": "#6366f1"}

    def test_create_track_as_organizer(self):
        _auth(self.client, self.organizer)
        res = self.client.post(self._url(), self._payload("Backend"), format="json")
        self.assertEqual(res.status_code, 201)

    def test_create_track_as_non_organizer(self):
        _auth(self.client, self.attendee)
        res = self.client.post(self._url(), self._payload("Frontend"), format="json")
        self.assertEqual(res.status_code, 403)

    def test_create_track_unauthenticated(self):
        res = self.client.post(self._url(), self._payload("Security"), format="json")
        self.assertEqual(res.status_code, 401)

    def test_duplicate_name_same_event(self):
        _auth(self.client, self.organizer)
        self.client.post(self._url(), self._payload("Keynote"), format="json")
        res = self.client.post(self._url(), self._payload("Keynote"), format="json")
        self.assertEqual(res.status_code, 400)

    def test_same_name_different_events(self):
        _auth(self.client, self.organizer)
        res1 = self.client.post(self._url(self.event), self._payload("Workshop"), format="json")
        self.assertEqual(res1.status_code, 201)

        _auth(self.client, self.other_org)
        res2 = self.client.post(self._url(self.event2), self._payload("Workshop"), format="json")
        self.assertEqual(res2.status_code, 201)
