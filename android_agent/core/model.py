"""
Model provider backed by the Google Gen AI SDK.
"""

from __future__ import annotations

from typing import Any, Callable

from google import genai
from google.genai import types

from android_agent.core.config import LOCATION, MODEL_NAME, PROJECT_ID
from android_agent.prompt import SYSTEM_PROMPT
from android_agent.tools.android_knowledge import AndroidKnowledgeTool


KNOWLEDGE_DB = "knowledge/android11/bytecode.db"


class ModelProvider:
    """Wrapper around the Google Gen AI SDK."""

    def __init__(self) -> None:
        self.client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )

        self.knowledge = AndroidKnowledgeTool(KNOWLEDGE_DB)

        self.tool_functions: dict[str, Callable[..., Any]] = {
            "search_android_class": self.knowledge.search_class,
            "get_android_class": self.knowledge.get_class,
            "search_android_method": self.knowledge.search_method,
            "get_android_method_instructions": (self.knowledge.get_method_instructions),
            "get_android_method_calls": self.knowledge.get_method_calls,
        }

        self.tools = self._create_tools()

        self.chat = self.client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=self.tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True,
                ),
            ),
        )

    def _create_tools(self) -> list[types.Tool]:
        """Create structured Android knowledge tool declarations."""

        search_class = types.FunctionDeclaration(
            name="search_android_class",
            description=(
                "Search the Android framework knowledge database for classes by name. "
                "Use this to identify a class and obtain its database ID before "
                "querying its methods or other class-related data."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Class name or part of a class name.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matching classes.",
                        "default": 20,
                    },
                },
                "required": ["name"],
            },
        )

        get_class = types.FunctionDeclaration(
            name="get_android_class",
            description=(
                "Get detailed information about an Android framework "
                "class using its database ID."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "class_id": {
                        "type": "integer",
                        "description": "Database ID of the class.",
                    },
                },
                "required": ["class_id"],
            },
        )

        search_method = types.FunctionDeclaration(
            name="search_android_method",
            description=(
                "Search the Android framework knowledge database for methods by name. "
                "Use class_name to restrict the search to a specific class. "
                "Use descriptor when the exact method signature is known. "
                "Use this when you need a method ID for further method-level queries."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Method name or part of a method name.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matching methods.",
                        "default": 20,
                    },
                    "class_name": {
                        "type": "string",
                        "description": (
                            "Optional fully qualified DEX class name to restrict "
                            "the method search to."
                        ),
                    },
                    "descriptor": {
                        "type": "string",
                        "description": (
                            "Optional DEX method descriptor, such as ()V or "
                            "(I)Ljava/lang/String;."
                        ),
                    },
                },
                "required": ["name"],
            },
        )

        get_instructions = types.FunctionDeclaration(
            name="get_android_method_instructions",
            description=(
                "Get the DEX instructions for an Android framework method "
                "using its database ID. Use this tool when instruction-level "
                "behavior needs to be verified from the knowledge database."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "integer",
                        "description": "Database ID of the method.",
                    },
                },
                "required": ["method_id"],
            },
        )

        get_method_calls = types.FunctionDeclaration(
            name="get_android_method_calls",
            description=(
                "Get the methods actually called by an Android framework method "
                "using its database ID. Use this when the user asks what methods "
                "a method calls, invokes, or delegates to."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "integer",
                        "description": "Database ID of the caller method.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of method calls to return.",
                        "default": 50,
                    },
                },
                "required": ["method_id"],
            },
        )

        return [
            types.Tool(
                function_declarations=[
                    search_class,
                    get_class,
                    search_method,
                    get_instructions,
                    get_method_calls,
                ]
            )
        ]

    def _execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a requested Android knowledge tool."""

        function = self.tool_functions.get(name)

        if function is None:
            return {
                "error": f"Unknown tool: {name}",
            }

        try:
            result = function(**arguments)

            return {
                "output": result,
            }

        except Exception as exc:
            return {
                "error": f"{type(exc).__name__}: {exc}",
            }

    def send(self, message: str) -> str:
        """Send a message to Gemini and handle tool calls manually."""

        response = self.chat.send_message(message)

        while response.function_calls:
            function_response_parts = []

            for function_call in response.function_calls:
                name = function_call.name
                arguments = function_call.args or {}

                result = self._execute_tool(
                    name=name,
                    arguments=arguments,
                )

                function_response_parts.append(
                    types.Part.from_function_response(
                        name=name,
                        response=result,
                    )
                )

            response = self.chat.send_message(function_response_parts)

        if response.text:
            return response.text.strip()

        return "The model returned an empty response."

    def close(self) -> None:
        """Close the knowledge database and Gemini client."""

        self.knowledge.close()
        self.client.close()
