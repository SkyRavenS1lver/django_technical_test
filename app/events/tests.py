from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Event

User = get_user_model()

PASSWORD = "testpass123"


def _make_user(email, is_organizer=False):
    return User.objects.create_user(email=email, name="Test", password=PASSWORD, is_organizer=is_organizer)


def _auth(client, user):
    res = client.post("/api/v1/auth/login/", {"email": user.email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def _make_event(organizer, title="Test Event", status=Event.Status.PUBLISHED):
    now = timezone.now()
    return Event.objects.create(
        title=title,
        description="A test event.",
        start_date=now,
        end_date=now + timezone.timedelta(hours=4),
        venue_name="Venue",
        venue_address="123 St",
        max_attendees=100,
        organizer=organizer,
        status=status,
    )


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organizer = _make_user("org@example.com", is_organizer=True)

    def test_slug_auto_generated(self):
        event = _make_event(self.organizer, title="My Awesome Event")
        self.assertEqual(event.slug, "my-awesome-event")

    def test_slug_collision_resolved(self):
        e1 = _make_event(self.organizer, title="Same Title")
        e2 = _make_event(self.organizer, title="Same Title")
        self.assertNotEqual(e1.slug, e2.slug)
        self.assertEqual(e1.slug, "same-title")
        self.assertEqual(e2.slug, "same-title-1")

    def test_end_before_start_raises(self):
        now = timezone.now()
        event = Event(
            title="Bad Dates",
            description="x",
            start_date=now,
            end_date=now - timezone.timedelta(hours=1),
            venue_name="V",
            venue_address="A",
            max_attendees=10,
            organizer=self.organizer,
        )
        with self.assertRaises(ValidationError):
            event.full_clean()


class EventAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organizer = _make_user("org@example.com", is_organizer=True)
        cls.other_org = _make_user("other@example.com", is_organizer=True)
        cls.attendee = _make_user("att@example.com", is_organizer=False)
        cls.published = _make_event(cls.organizer, title="Published", status=Event.Status.PUBLISHED)
        cls.draft = _make_event(cls.organizer, title="Draft Event", status=Event.Status.DRAFT)

    def setUp(self):
        self.client = APIClient()

    def _event_payload(self, title="New Event"):
        now = timezone.now()
        return {
            "title": title,
            "description": "desc",
            "start_date": now.isoformat(),
            "end_date": (now + timezone.timedelta(hours=2)).isoformat(),
            "venue_name": "Hall",
            "venue_address": "1 Road",
            "max_attendees": 50,
            "status": "draft",
        }

    def test_list_unauthenticated_sees_only_published(self):
        res = self.client.get("/api/v1/events/")
        self.assertEqual(res.status_code, 200)
        slugs = [e["slug"] for e in res.data["results"]]
        self.assertIn(self.published.slug, slugs)
        self.assertNotIn(self.draft.slug, slugs)

    def test_organizer_sees_own_draft(self):
        _auth(self.client, self.organizer)
        res = self.client.get("/api/v1/events/")
        slugs = [e["slug"] for e in res.data["results"]]
        self.assertIn(self.draft.slug, slugs)

    def test_create_as_organizer(self):
        _auth(self.client, self.organizer)
        res = self.client.post("/api/v1/events/", self._event_payload(), format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["title"], "New Event")

    def test_create_as_attendee(self):
        _auth(self.client, self.attendee)
        res = self.client.post("/api/v1/events/", self._event_payload(), format="json")
        self.assertEqual(res.status_code, 403)

    def test_create_unauthenticated(self):
        res = self.client.post("/api/v1/events/", self._event_payload(), format="json")
        self.assertEqual(res.status_code, 401)

    def test_update_own_event(self):
        _auth(self.client, self.organizer)
        res = self.client.patch(f"/api/v1/events/{self.published.slug}/", {"title": "Updated"}, format="json")
        self.assertEqual(res.status_code, 200)

    def test_update_other_event(self):
        _auth(self.client, self.other_org)
        res = self.client.patch(f"/api/v1/events/{self.published.slug}/", {"title": "Hacked"}, format="json")
        self.assertEqual(res.status_code, 403)

    def test_filter_by_status(self):
        res = self.client.get("/api/v1/events/?status=published")
        for event in res.data["results"]:
            self.assertEqual(event["status"], "published")
