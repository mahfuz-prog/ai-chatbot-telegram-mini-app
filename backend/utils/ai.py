import os
import json
import logging
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# config
GENAI_API = os.getenv("GENAI_API")
WEATHER_API = os.getenv("WEATHER_API")

# https://ai.google.dev/gemini-api/docs
gemini_client = genai.Client(api_key=GENAI_API)


SYSTEM_INSTRUCTION = (
    "You are a helpful and friendly assistant and your name is 'Vulval bot'."
    "You have access to pull weather data from an API."
    "Based on the entire conversation history, provide a response to the user's message."
    "Then, create a new, concise summary of the *entire conversation so far*. "
    "The summary should capture key details, questions, and themes to inform future turns."
    "The summary is for your internal context, so compress it as much as you can."
    "The final response must be a JSON object string with two keys: "
    "'reply' for the user message and 'context_summary' for the updated conversation context."
)

TITLE_GENERATION_INSTRUCTION = (
    "You are an expert chat title generator. Your sole purpose is to analyze "
    "the user's first message in a conversation and provide a concise, "
    "relevant, and engaging title for the chat. Respond ONLY with the "
    "generated title text. Do not include any quotation marks, introductory "
    "phrases, or explanations. The title must be in 3 to 5 word."
)


# API call for get current weather data
def get_current_weather(location: str) -> str:
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API}&q={location}"
    try:
        return requests.get(url).text
    except Exception as e:
        logging.error(f"Failed to pull weather info. Error: {str(e)}")
        return "Failed to fetching weather data!"


def generate_model_response(history):
    # pass the history with current question, tool calling functionality
    model = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=history,
        config=types.GenerateContentConfig(
            max_output_tokens=1000,
            temperature=0.3,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[get_current_weather],
        ),
    )

    return model.text


def prepare_gemini_history(chat, user_message_content):
    """Prepares the conversation history for the LLM."""
    gemini_history = []

    # If there's an existing context, add it as a system instruction or initial prompt
    if hasattr(chat, "context") and chat.context.context_data:
        context_data = chat.context.context_data
        # Place context as the first user message for the model to use it
        gemini_history.append(
            {"role": "user", "parts": [{"text": f"System Context: {context_data}"}]}
        )

    # Add the current user's message
    gemini_history.append({"role": "user", "parts": [{"text": user_message_content}]})

    return gemini_history


def extract_json_from_model_response(data):
    """
    data look like

        ```json
            {
                "reply": "",
                "context_summary": ""
            }
        ```
    """
    try:
        response_content = json.loads(data[7:-3])
        model_reply = response_content["reply"]
        new_context = response_content["context_summary"]
        return (model_reply, new_context)
    except Exception as e:
        logging.error(f"Failed to extract data from model response. error {str(e)}")
        raise


def generate_chat_title(first_message_content, model_reply):
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{TITLE_GENERATION_INSTRUCTION} user_input: {first_message_content}, model_response: {model_reply}",
    )

    return response.text
