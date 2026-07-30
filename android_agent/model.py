"""
Vertex AI model wrapper.

Only this file should communicate directly with Vertex AI.
"""

from __future__ import annotations

import vertexai
from vertexai.generative_models import GenerativeModel

from android_agent.config import (
    LOCATION,
    MODEL_NAME,
)
from android_agent.prompt import SYSTEM_PROMPT


class ModelProvider:
    """Handles all communication with Vertex AI."""

    def __init__(self) -> None:
        vertexai.init(location=LOCATION)

        self._model = GenerativeModel(
            MODEL_NAME,
            system_instruction=[SYSTEM_PROMPT],
        )

        self._chat = self._model.start_chat()

    def send(self, message: str) -> str:
        """Send a message to Gemini and return its response."""

        response = self._chat.send_message(message)
        return response.text.strip()
