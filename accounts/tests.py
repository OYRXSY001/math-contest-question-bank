from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def test_project_uses_custom_user_model(self):
        user = get_user_model().objects.create_user("alice", password="safe-pass-123")

        self.assertEqual(user._meta.label, "accounts.User")
        self.assertTrue(user.check_password("safe-pass-123"))
