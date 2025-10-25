import json
from django.test import TestCase
from utils.ai import generate_model_response


class AiTest(TestCase):
    def test_generate_model_response(self):
        history = [{"role": "user", "parts": [{"text": "What is your name?"}]}]

        response = generate_model_response(history)
        response_content = json.loads(response[7:-3])
        model_reply = response_content["reply"]
        self.assertEqual(model_reply, "My name is Vulval bot.")
