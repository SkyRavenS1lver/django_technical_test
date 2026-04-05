from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from app.events.models import Event
from .models import Registration

User = get_user_model()

PASSWORD = "testpass123"


def _make_user(email, is_organizer=False):
    return User.objects.create_user(email=email, name="Test", password=PASSWORD, is_organizer=is_organizer)


def _auth(client, user):
    res = client.post("/api/v1/auth/login/", {"email": user.email, "password": PASSWORD}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def _make_event(organizer, max_attendees=10, title="Reg Test Event"):
    now = timezone.now()
    return Event.objects.create(
        title=title,
        description="desc",
        start_date=now,
        end_date=now + timezone.timedelta(hours=4),
        venue_name="Venue",
        venue_address="Addr",
        max_attendees=max_attendees,
        organizer=organizer,
        status=Event.Status.PUBLISHED,
    )


class RegistrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organizer = _make_user("org@example.com", is_organizer=True)
        cls.attendee = _make_user("att@example.com")
        cls.other = _make_user("other@example.com")
        cls.event = _make_event(cls.organizer, max_attendees=2)

    def setUp(self):
        self.client = APIClient()
        # Clear registrations between tests so capacity tests are isolated
        Registration.objects.all().delete()

    def _register(self, event_slug=None):
        return self.client.post("/api/v1/registrations/", {
            "event": event_slug or self.event.slug,
        }, format="json")

    def test_register_confirmed(self):
        _auth(self.client, self.attendee)
        res = self._register()
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["status"], "confirmed")

    def test_register_duplicate(self):
        _auth(self.client, self.attendee)
        self._register()
        res = self._register()
        self.assertEqual(res.status_code, 400)

    def test_register_fills_to_waitlist(self):
        # Fill capacity (max_attendees=2) with two other users
        u1 = _make_user("u1@example.com")
        u2 = _make_user("u2@example.com")
        for u in (u1, u2):
            _auth(self.client, u)
            self._register()

        # Third user should be waitlisted
        _auth(self.client, self.attendee)
        res = self._register()
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["status"], "waitlisted")

    def test_cancel_registration(self):
        _auth(self.client, self.attendee)
        create_res = self._register()
        reg_id = create_res.data["id"]

        res = self.client.patch(f"/api/v1/registrations/{reg_id}/", {}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "cancelled")

    def test_cancel_other_users_registration(self):
        _auth(self.client, self.attendee)
        create_res = self._register()
        reg_id = create_res.data["id"]

        # other user's queryset excludes this registration → 404 (not 403)
        _auth(self.client, self.other)
        res = self.client.patch(f"/api/v1/registrations/{reg_id}/", {}, format="json")
        self.assertEqual(res.status_code, 404)

    def test_list_own_registrations_only(self):
        # attendee registers
        _auth(self.client, self.attendee)
        self._register()

        # other registers for a different event
        other_event = _make_event(self.organizer, title="Other Event")
        _auth(self.client, self.other)
        self.client.post("/api/v1/registrations/", {"event": other_event.slug}, format="json")

        # attendee should only see their own registration
        _auth(self.client, self.attendee)
        res = self.client.get("/api/v1/registrations/")
        self.assertEqual(res.status_code, 200)
        for reg in res.data["results"]:
            self.assertEqual(reg["event"], self.event.slug)
