import os
import json
from django.test import TestCase
from utils.helper import get_current_weather
from django.http import HttpRequest
from chats.models import User
from utils.helper import check_tg_data_string
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


class WeatherPullTest(TestCase):
    def test_get_current_weather(self):
        location = "Dhaka"
        response = get_current_weather(location)
        response_data = json.loads(response)
        self.assertEqual(response_data["location"]["name"], location)

    def test_get_current_weather_error(self):
        location = "asdfsdafdsa"
        response = get_current_weather(location)
        self.assertEqual(response, "Failed to fetching weather data!")


# Dummy view to wrap
def dummy_view(request, current_user):
    return {"user_id": current_user.telegram_id, "username": current_user.username}


class CheckTgDataStringTest(TestCase):
    def setUp(self):
        self.BOT_TOKEN = BOT_TOKEN
        # provide a valid sample data string
        self.sample_datastring = "query_id=AAEPsHoIAwAAAA-weghhrZhz&user=%7B%22id%22%3A6584709135%2C%22first_name%22%3A%22Mahfuz%22%2C%22last_name%22%3A%22Rahman%22%2C%22username%22%3A%22mahfuz5676%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FzF4ipl95HZ3J3ZK5TNHrl6dj87Ai1RWUwEI8ZUCKaqnw_G7kp67smDoKmx8xLvjn.svg%22%7D&auth_date=1755325669&signature=d-tB-7rgB-2hQWiihLDkYkK52uRXQbjzL5CIqel6WZBZMd_ISJoUY04ItkODYzd-MvxbQjW-6yvgGqjD-0_GBg&hash=e2b90c067a2db136301d428fbf088ec99334c8b679f2ec866a004b179abd07f7"

    def test_missing_header(self):
        request = HttpRequest()
        # no header
        request.headers = {}
        wrapped_view = check_tg_data_string(dummy_view)
        response = wrapped_view(request)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_data, {"error": "Data String mising!"})

    def test_invalid_datastring(self):
        request = HttpRequest()
        request.headers = {"X-Telegram-Init-Data": "invalid_string"}
        wrapped_view = check_tg_data_string(dummy_view)
        response = wrapped_view(request)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_data, {"error": "Invalid data_string!"})

    def test_valid_datastring_creates_user(self):
        # Replace hash and auth_date so it passes your decorator logic
        request = HttpRequest()
        request.headers = {"X-Telegram-Init-Data": self.sample_datastring}

        wrapped_view = check_tg_data_string(dummy_view)
        response_data = wrapped_view(request)

        # Check user is created
        user = User.objects.get(username=response_data["username"])
        self.assertEqual(response_data["user_id"], user.telegram_id)
        self.assertEqual(response_data["username"], user.username)
