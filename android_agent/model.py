"""
Model provider backed by the Google Gen AI SDK.
"""

from __future__ import annotations

from google import genai
from google.genai import types

from android_agent.config import LOCATION, MODEL_NAME, PROJECT_ID
from android_agent.prompt import SYSTEM_PROMPT


class ModelProvider:
    """Wrapper around the Google Gen AI SDK."""

    def __init__(self) -> None:
        self.client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )

        self.chat = self.client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )

    def send(self, message: str) -> str:
        """Send a message to Gemini and return the response."""

        response = self.chat.send_message(message)

        if response.text:
            return response.text.strip()

        return "The model returned an empty response."
