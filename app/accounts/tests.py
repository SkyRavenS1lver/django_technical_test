from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()

PASSWORD = "testpass123"


def _make_user(email, name="Test User", is_organizer=False, password=PASSWORD):
    return User.objects.create_user(email=email, name=name, password=password, is_organizer=is_organizer)


def _auth(client, user, password=PASSWORD):
    res = client.post("/api/v1/auth/login/", {"email": user.email, "password": password}, format="json")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


class UserModelTest(TestCase):
    def test_create_user(self):
        user = _make_user("user@example.com", name="Alice")
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.name, "Alice")
        self.assertFalse(user.is_organizer)
        self.assertTrue(user.check_password(PASSWORD))

    def test_create_superuser(self):
        user = User.objects.create_superuser(email="admin@example.com", password=PASSWORD)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password=PASSWORD)


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_returns_tokens(self):
        res = self.client.post("/api/v1/auth/register/", {
            "email": "new@example.com", "name": "New User", "password": PASSWORD,
        }, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_register_duplicate_email(self):
        _make_user("dup@example.com")
        res = self.client.post("/api/v1/auth/register/", {
            "email": "dup@example.com", "name": "Dup", "password": PASSWORD,
        }, format="json")
        self.assertEqual(res.status_code, 400)

    def test_login_returns_tokens(self):
        user = _make_user("login@example.com")
        res = self.client.post("/api/v1/auth/login/", {"email": user.email, "password": PASSWORD}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)

    def test_login_wrong_password(self):
        user = _make_user("wp@example.com")
        res = self.client.post("/api/v1/auth/login/", {"email": user.email, "password": "wrongpass"}, format="json")
        self.assertEqual(res.status_code, 401)

    def test_me_requires_auth(self):
        res = self.client.get("/api/v1/auth/me/")
        self.assertEqual(res.status_code, 401)

    def test_me_returns_user(self):
        user = _make_user("me@example.com")
        _auth(self.client, user)
        res = self.client.get("/api/v1/auth/me/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["email"], user.email)
