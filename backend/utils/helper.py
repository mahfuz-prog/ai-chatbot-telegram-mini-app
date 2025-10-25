import os
import hmac
import json
import time
import logging
import hashlib
import requests
from functools import wraps
from urllib.parse import parse_qsl
from users.models import User
from django.http import JsonResponse
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VALID_AUTH_DATE_WINDOW_SECONDS = int(os.getenv("VALID_AUTH_DATE_WINDOW_SECONDS"))
WEATHER_API = os.getenv("WEATHER_API")


# API call for get current weather data
def get_current_weather(location: str) -> str:
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API}&q={location}"
    try:
        response = requests.get(url)
        if "error" in response.json():
            return "Failed to fetching weather data!"
        return response.text
    except Exception as e:
        logging.error(f"Failed to pull weather info. Error: {str(e)}")
        return "Failed to fetching weather data!"


# decorator for views
def check_tg_data_string(f):
    @wraps(f)
    def inner(request, *args, **kwargs):
        tg_init_data = request.headers.get("X-Telegram-Init-Data")

        # if no datastring found
        if not tg_init_data:
            logging.error("X-Telegram-Init-Data is not present in headers")
            return JsonResponse({"error": "Data String mising!"}, status=401)

        # parse tg_init_data
        try:
            init_data = dict(parse_qsl(tg_init_data, strict_parsing=True))
        except Exception as e:
            logging.error(f"Failed to patse X-Telegram-Init-Data. error: {str(e)}")
            return JsonResponse({"error": "Invalid data_string!"}, status=401)

        # extract hash
        received_hash = init_data.pop("hash", None)
        if not received_hash:
            logging.error("X-Telegram-Init-Data don't have a hash")
            return JsonResponse({"error": "Invalid data_string!"}, status=401)

        # Check auth_date (timestamp)
        auth_date_str = init_data.get("auth_date")
        if not auth_date_str:
            logging.error("X-Telegram-Init-Data don't have a auth_date")
            return JsonResponse({"error": "Invalid data_string!"}, status=401)

        try:
            auth_date = int(auth_date_str)
            current_unix_time = int(time.time())

            # Check if the data is too old
            if current_unix_time - auth_date > VALID_AUTH_DATE_WINDOW_SECONDS:
                logging.warning("Date expired X-Telegram-Init-Data")
                return JsonResponse({"error": "Invalid data_string!"}, status=401)
        except Exception as e:
            logging.error(
                f"Failed to validate X-Telegram-Init-Data date. error: {str(e)}"
            )
            return JsonResponse({"error": "Invalid data_string!"}, status=401)

        # Construct data-check-string
        # Sort fields alphabetically and format as 'key=<value>'
        # https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(init_data.items(), key=lambda item: item[0])
        )

        # Calculate secret key
        secret_key = hmac.new(
            key=b"WebAppData", msg=BOT_TOKEN.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()

        # Calculate signature hash
        computed_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Compare received hash with calculated hash
        if computed_hash != received_hash:
            logging.error(
                "Data string validation failed. hash mismatch computed_hash != received_hash"
            )
            return JsonResponse({"error": "Validation failed!"}, status=401)

        # get user info from parsed data string
        telegram_user_data = json.loads(init_data.get("user"))
        telegram_user_id = telegram_user_data.get("id")
        telegram_user_name = telegram_user_data.get("username")

        # get_or_create to retrieve or create the user
        try:
            current_user, created = User.objects.get_or_create(
                telegram_id=telegram_user_id, defaults={"username": telegram_user_name}
            )
            # username might change, update it here
            if not created and current_user.username != telegram_user_name:
                current_user.username = telegram_user_name
                current_user.save()
        except Exception as e:
            logging.warning(f"Failed to create or load user. error: {str(e)}")
            return JsonResponse({"error": "Something went wrong!"}, status=500)

        return f(request, current_user, *args, **kwargs)

    return inner
