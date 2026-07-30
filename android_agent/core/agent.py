"""
Core Android Agent.

This class is the brain of the application.
"""

from __future__ import annotations

from android_agent.core.model import ModelProvider


class AndroidAgent:
    """Main AI Agent."""

    def __init__(self) -> None:
        self.model = ModelProvider()

    def ask(self, message: str) -> str:
        """
        Send a message to the language model
        and return its response.
        """
        return self.model.send(message)
