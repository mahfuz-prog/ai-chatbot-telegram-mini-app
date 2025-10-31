from unittest.mock import patch, MagicMock
from django.test import TestCase
from utils.ai import WeatherInformationPipeline  # adjust import as needed


class WeatherInformationPipelineTests(TestCase):
    @patch("utils.ai.Executor")
    @patch("utils.ai.get_current_weather")
    def test_chat_success(self, mock_get_weather, mock_executor_cls):
        """Test WeatherInformationPipeline.chat returns a valid LLM output"""

        # Mock weather tool
        mock_get_weather.return_value = {
            "temperature": 25,
            "condition": "Cloudy",
            "city": "Dhaka",
        }

        # Mock executor result
        mock_executor = MagicMock()
        mock_result = MagicMock()
        mock_result.is_success.return_value = True
        mock_result.get_node_output.return_value = {
            "reply": "The weather in Dhaka is cloudy at 25°C.",
            "context_summary": "User asked about weather in Dhaka.",
        }
        mock_executor.execute.return_value = mock_result
        mock_executor_cls.return_value = mock_executor

        pipeline = WeatherInformationPipeline(
            api_key="fake_api_key", model="gpt-4o-mini"
        )

        result = pipeline.chat("What's the weather in Dhaka?", "Previous summary")

        self.assertIn("reply", result)
        self.assertIn("context_summary", result)
        self.assertEqual(result["reply"], "The weather in Dhaka is cloudy at 25°C.")

    @patch("utils.ai.Executor")
    def test_chat_failure(self, mock_executor_cls):
        """Test WeatherInformationPipeline.chat raises exception when execution fails"""
        mock_executor = MagicMock()
        mock_result = MagicMock()
        mock_result.is_success.return_value = False
        mock_result.get_error.return_value = "LLM timeout"
        mock_executor.execute.return_value = mock_result
        mock_executor_cls.return_value = mock_executor

        pipeline = WeatherInformationPipeline(
            api_key="fake_api_key", model="gpt-4o-mini"
        )

        with self.assertRaises(Exception) as ctx:
            pipeline.chat("Is it raining?", "Context summary")

        self.assertIn("WeatherInformationPipeline failed!", str(ctx.exception))

    @patch("utils.ai.LlmClient")
    def test_generate_title(self, mock_llm_client_cls):
        """Test generate_title returns the correct text"""
        mock_client = MagicMock()
        mock_client.complete.return_value = "Dhaka Weather Update"
        mock_llm_client_cls.return_value = mock_client

        pipeline = WeatherInformationPipeline(
            api_key="fake_api_key", model="gpt-4o-mini"
        )
        title = pipeline.generate_title("What's the weather in Dhaka?", "It's cloudy.")
        self.assertEqual(title, "Dhaka Weather Update")
