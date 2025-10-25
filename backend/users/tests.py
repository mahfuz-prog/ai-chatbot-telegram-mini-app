from django.test import TestCase
from users.models import User
from django.utils import timezone
from datetime import timedelta


class ChatAppModelsTest(TestCase):
    def setUp(self):
        # Create a Telegram user
        self.user = User.objects.create(telegram_id=123456789, username="test_user")

    def test_user_model_str_and_ordering(self):
        """User string representation and ordering by -joined"""
        user1 = self.user
        user2 = User.objects.create(
            telegram_id=987654321,
            username="another_user",
            joined=timezone.now() + timedelta(seconds=1),  # make sure it's later
        )

        self.assertEqual(str(user1), f"{user1.username} -> tg: {user1.telegram_id}")

        users = list(User.objects.all())
        self.assertEqual(users[0], user2)  # newest user first
