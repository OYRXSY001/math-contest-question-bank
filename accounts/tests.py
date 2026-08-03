from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserModelTests(TestCase):
    def test_project_uses_custom_user_model(self):
        user = get_user_model().objects.create_user("alice", password="safe-pass-123")

        self.assertEqual(user._meta.label, "accounts.User")
        self.assertTrue(user.check_password("safe-pass-123"))

    def test_registration_logs_user_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-user",
                "password1": "safe-pass-987",
                "password2": "safe-pass-987",
            },
        )

        self.assertRedirects(response, reverse("home"))
        user = get_user_model().objects.get(username="new-user")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
