import os
import hmac
import json
import time
import hashlib
import requests
from functools import wraps
from urllib.parse import parse_qsl
from users.models import User
from google import genai
from google.genai import types
from django.http import JsonResponse

# config
GENAI_API = os.environ.get('GENAI_API')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEATHER_API = os.environ.get('WEATHER_API')
VALID_AUTH_DATE_WINDOW_SECONDS = int(os.environ.get('VALID_AUTH_DATE_WINDOW_SECONDS'))

# https://ai.google.dev/gemini-api/docs
gemini_client = genai.Client(api_key=GENAI_API)


system_instruction = (
	"You are a helpful and friendly assistant and your name is 'Vulval bot'."
	"You have access to pull weather data from an API."
	"Based on the entire conversation history, provide a response to the user's message."
	"Then, create a new, concise summary of the *entire conversation so far*. "
	"The summary should capture key details, questions, and themes to inform future turns."
	"The summary is for your internal context, so compress it as much as you can."
	"The final response must be a JSON object string with two keys: "
	"'reply' for the user message and 'context_summary' for the updated conversation context."
)


# ==================================================================
# API cal for get current weather data
def get_current_weather(location: str) -> str:
	url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API}&q={location}'
	try:
		return requests.get(url).text
	except:
		return f"Failed to fetching weather data!"


# return model reply
def generate_model_response(history):
	# pass the history with current question, sys_instruct, and external api call functionality
	model = gemini_client.models.generate_content(
		model="gemini-2.5-flash",
		contents=history,
		config=types.GenerateContentConfig(
			max_output_tokens=1000,
			temperature=0.3,
			system_instruction=system_instruction,
			tools=[get_current_weather]
		)
	)

	return model.text


# ======================================================================
# decorator for views
def check_tg_data_string(f):
	@wraps(f)
	def inner(request, *args, **kwargs):
		tg_init_data = request.headers.get("X-Telegram-Init-Data")

		# if no datastring found
		if not tg_init_data:
			return JsonResponse({"error": "Data String mising!"}, status=401)

		# parse tg_init_data
		try:
			init_data = dict(parse_qsl(tg_init_data, strict_parsing=True))
		except:
			return JsonResponse({"error": "Invalid data_string!"}, status=401)
			
		# extract hash
		received_hash = init_data.pop('hash', None)
		if not received_hash:
			return JsonResponse({"error": "Invalid data_string!"}, status=401)

		# Check auth_date (timestamp)
		auth_date_str = init_data.get('auth_date')
		if not auth_date_str:
			return JsonResponse({"error": "Invalid data_string!"}, status=401)

		try:
			auth_date = int(auth_date_str)
			current_unix_time = int(time.time())

			# Check if the data is too old
			if current_unix_time - auth_date > VALID_AUTH_DATE_WINDOW_SECONDS:
				return JsonResponse({"error": "Invalid data_string!"}, status=401)

		except:
			return JsonResponse({"error": "Invalid data_string!"}, status=401)


		# Construct data-check-string
		# Sort fields alphabetically and format as 'key=<value>'
		# https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
		data_check_string = "\n".join(
			f"{k}={v}" for k, v in sorted(init_data.items(), key=lambda item: item[0])
		)

		# Calculate secret key
		secret_key = hmac.new(
			key=b'WebAppData',
			msg=BOT_TOKEN.encode('utf-8'),
			digestmod=hashlib.sha256
		).digest()

		# Calculate signature hash
		computed_hash = hmac.new(
			key=secret_key,
			msg=data_check_string.encode('utf-8'),
			digestmod=hashlib.sha256
		).hexdigest()

		# Compare received hash with calculated hash
		if computed_hash != received_hash:
			return JsonResponse({'error': 'Validation failed!'}, status=401)

		# get user info from parsed data string
		telegram_user_data = json.loads(init_data.get('user'))
		telegram_user_id = telegram_user_data.get('id')
		telegram_user_name = telegram_user_data.get('username')
		
		# get_or_create to retrieve or create the user
		try:
			current_user, created = User.objects.get_or_create(
				telegram_id = telegram_user_id,
				defaults = {"username" : telegram_user_name}
			)
			# username might change, update it here
			if not created and current_user.username != telegram_user_name:
				current_user.username = telegram_user_name
				current_user.save()
		except:
			return JsonResponse({'error': 'Something went wrong!'}, status=500)

		return f(request, current_user, *args, ** kwargs)
	return inner