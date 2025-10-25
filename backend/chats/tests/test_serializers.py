from django.test import TestCase
from users.models import User
from chats.models import Chat, Message
from chats.serializers import (
    ChatSerializer,
    MessageSerializer,
    ChatDetailSerializer,
    MessageInputSerializer,
)


class ChatSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(telegram_id=123456, username="john_doe")
        self.chat = Chat.objects.create(user=self.user, title="Hello Chat")

    def test_chat_serializer_fields(self):
        serializer = ChatSerializer(instance=self.chat)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("unique_hex_id", data)
        self.assertIn("title", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)


class MessageSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(telegram_id=123456, username="john_doe")
        self.chat = Chat.objects.create(user=self.user)
        self.message = Message.objects.create(
            chat=self.chat, sender="user", content="Hello!"
        )

    def test_message_serializer_fields(self):
        serializer = MessageSerializer(instance=self.message)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("sender", data)
        self.assertIn("content", data)
        self.assertIn("timestamp", data)


class ChatDetailSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(telegram_id=123456, username="john_doe")
        self.chat = Chat.objects.create(user=self.user, title="Detailed Chat")
        Message.objects.create(chat=self.chat, sender="user", content="Hi")
        Message.objects.create(chat=self.chat, sender="model", content="Hello!")

    def test_chat_detail_serializer_includes_messages(self):
        serializer = ChatDetailSerializer(instance=self.chat)
        data = serializer.data

        self.assertIn("messages", data)
        self.assertTrue(isinstance(data["messages"], list))
        self.assertGreater(len(data["messages"]), 0)
        self.assertIn("content", data["messages"][0])


class MessageInputSerializerTests(TestCase):
    def test_message_input_validation(self):
        data = {"chat_id": 1, "content": "Hi there!"}
        serializer = MessageInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_message_input_invalid(self):
        data = {"chat_id": "invalid", "content": ""}
        serializer = MessageInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
