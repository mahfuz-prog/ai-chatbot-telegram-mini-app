import json
from django.test import TestCase
from django.http import JsonResponse
from unittest.mock import patch
from users.models import User
from chats.models import Chat, Message, ChatContext
from chats import service


class ChatServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(telegram_id=1111, username="john_doe")
        self.chat = Chat.objects.create(user=self.user, title="Test Chat")

    def test_user_chats_returns_user_chats(self):
        response = service.user_chats(self.user)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("chat_list", data)
        self.assertIsInstance(response, JsonResponse)

    def test_create_new_chat_success(self):
        data = {"title": "Brand New Chat"}
        response = service.create_new_chat(data, self.user)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertIn("new_chat", response_data)

    def test_create_new_chat_invalid(self):
        # invalid since title is too long (based on serializer constraint)
        data = {"title": "X" * 100}
        response = service.create_new_chat(data, self.user)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response_data)

    def test_get_single_chat_invalid_id(self):
        response = service.get_single_chat(self.user, "invalid_hex")
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response_data)

    def test_delete_chat_success(self):
        response = service.delete_user_chat(self.user, self.chat.id)
        self.assertEqual(response.status_code, 204)

    def test_delete_chat_permission_denied(self):
        other_user = User.objects.create(telegram_id=9999, username="bob")
        chat = Chat.objects.create(user=other_user, title="Other Chat")
        response = service.delete_user_chat(self.user, chat.id)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertIn("error", response_data)


class InboxServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(telegram_id=2222, username="alice")
        self.chat = Chat.objects.create(user=self.user)
        self.context = ChatContext.objects.create(
            chat=self.chat, context_data="no context availabl"
        )

    @patch("chats.service.check_chat_permission", return_value=None)
    @patch(
        "chats.service.extract_data_from_model_response",
        return_value=("Model Reply", {"context": "new"}),
    )
    @patch(
        "chats.service.WeatherInformationPipeline.generate_title",
        return_value="Auto Title",
    )
    @patch(
        "chats.service.WeatherInformationPipeline.chat",
        return_value={"reply": "Weather is sunny."},
    )
    def test_inbox_success_flow(
        self, mock_chat, mock_title, mock_extract, mock_permission
    ):
        """Test successful inbox flow with mocked pipeline"""
        data = {"chat_id": self.chat.id, "content": "Hello AI"}

        response = service.inbox(data, self.user)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertIn("model", response_data)
        self.assertTrue(Message.objects.filter(chat=self.chat).count() >= 2)
        self.assertEqual(response_data.get("title"), "Auto Title")

    def test_inbox_invalid_data(self):
        """Test invalid request data returns 400"""
        data = {"chat_id": "invalid", "content": ""}
        response = service.inbox(data, self.user)
        self.assertEqual(response.status_code, 400)

    def test_inbox_chat_not_found(self):
        """Test when chat ID doesn’t exist returns 404"""
        data = {"chat_id": 9999, "content": "Hello?"}
        response = service.inbox(data, self.user)
        self.assertEqual(response.status_code, 404)

    @patch(
        "chats.service.WeatherInformationPipeline.chat",
        side_effect=Exception("AI error"),
    )
    def test_inbox_ai_failure(self, mock_ai):
        """Test when pipeline.chat fails returns 500"""
        data = {"chat_id": self.chat.id, "content": "Test error"}

        response = service.inbox(data, self.user)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response_data)
