"""
Command Line Interface for Android Agent.
"""

from __future__ import annotations

from android_agent.agent import AndroidAgent
from android_agent.config import APP_NAME, VERSION


def run() -> None:
    """Run the interactive CLI."""

    print("=" * 50)
    print(f"{APP_NAME} v{VERSION}")
    print("=" * 50)
    print("Type 'quit' or 'exit' to close.\n")

    agent = AndroidAgent()

    while True:
        try:
            user_input = input("You > ").strip()

            if not user_input:
                continue

            if user_input.lower() in {"quit", "exit"}:
                print("\nGoodbye.")
                break

            response = agent.ask(user_input)

            print(f"\n{APP_NAME} > {response}\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted.")
            break

        except Exception as exc:
            print(f"\nError: {exc}\n")
