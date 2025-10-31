import os
from dotenv import load_dotenv
from graphbit import LlmClient
from utils.helper import get_current_weather
from graphbit import init, LlmConfig, Executor, Workflow, Node

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

SYSTEM_INSTRUCTION = (
    "You are a helpful and friendly assistant and your name is 'Vulval bot'."
    "You have access to pull weather data from an API."
    "Based on the previous conversation summary, create a new concise summary."
    "The summary should capture key details, questions, and themes."
    "The summary is for your internal context, so compress it as much as you can."
    "The final response must be a **plain JSON string**, without backticks, code blocks, or any other formatting."
    "'reply' for the user message and 'context_summary' for the updated conversation context."
)

TITLE_GENERATION_INSTRUCTION = (
    "You are an expert chat title generator. Your sole purpose is to analyze "
    "the user's first message in a conversation and provide a concise, "
    "relevant, and engaging title for the chat. Respond ONLY with the "
    "generated title text. Do not include any quotation marks, introductory "
    "phrases, or explanations. The title must be in 3 to 5 word."
)


class WeatherInformationPipeline:
    def __init__(self, api_key: str = OPENROUTER_API_KEY, model: str = "gpt-4o-mini"):
        init(log_level="info", enable_tracing=False)
        self.llm_config = LlmConfig.openrouter(api_key=api_key, model=model)
        self.executor = Executor(self.llm_config, timeout_seconds=60, debug=DEBUG)
        self.client = LlmClient(self.llm_config, debug=DEBUG)

    def create_workflow(self, query: str, context_summary: str) -> Workflow:
        workflow = Workflow("Instant Weather Pull")

        fetch_node = Node.agent(
            name="Weather Agent",
            prompt=f"""{SYSTEM_INSTRUCTION} Previous conversation summary: {context_summary} User message: {query}""",
            agent_id="weather_agent",
            tools=[get_current_weather],
        )

        workflow.add_node(fetch_node)
        workflow.validate()
        return workflow

    def chat(self, query: str, context_summary: str):
        """Run the simplified workflow."""
        workflow = self.create_workflow(query, context_summary)
        result = self.executor.execute(workflow)

        if result.is_success():
            return result.get_node_output("Weather Agent")
        else:
            error_msg = result.get_error()
            raise Exception(f"WeatherInformationPipeline failed! Error: {error_msg}")

    def generate_title(self, first_message_content, model_reply):
        response = self.client.complete(
            prompt=f"{TITLE_GENERATION_INSTRUCTION} user_input: {first_message_content}, model_response: {model_reply}",
            max_tokens=5,
            temperature=0.7,
        )

        return response
