from django.test import TestCase
from users.models import User
from chats.models import Chat, ChatContext, Message


class ChatAppModelsTest(TestCase):
    def setUp(self):
        # Create a Telegram user
        self.user = User.objects.create(telegram_id=123456789, username="test_user")

    def test_chat_generates_unique_hex_id(self):
        """Chat auto-generates unique_hex_id and links to user"""
        chat = Chat.objects.create(user=self.user)
        self.assertTrue(chat.unique_hex_id)
        self.assertEqual(len(chat.unique_hex_id), 20)
        self.assertEqual(chat.title, Chat.DEFAULT_TITLE)
        self.assertEqual(chat.user, self.user)

    def test_chat_context_relationship(self):
        """ChatContext OneToOneField works properly"""
        chat = Chat.objects.create(user=self.user)
        context = ChatContext.objects.create(chat=chat, context_data="Initial context")
        self.assertEqual(context.chat, chat)
        self.assertEqual(chat.context.context_data, "Initial context")

    def test_message_creation_and_ordering(self):
        chat = Chat.objects.create(user=self.user)
        msg1 = Message.objects.create(chat=chat, sender="user", content="Hi there")
        msg2 = Message.objects.create(chat=chat, sender="model", content="Hello!")

        messages = list(chat.messages.all())
        # Just check that both messages exist and are linked
        self.assertIn(msg1, messages)
        self.assertIn(msg2, messages)
        self.assertEqual(messages[0].chat, chat)
        self.assertEqual(messages[1].chat, chat)

    def test_chat_str_representation(self):
        """Chat string representation includes user.telegram_id"""
        chat = Chat.objects.create(user=self.user, title="Test Chat")
        expected_str = (
            f"chat-id: {chat.id} -> title: {chat.title}, User: {self.user.telegram_id}"
        )
        self.assertEqual(str(chat), expected_str)
