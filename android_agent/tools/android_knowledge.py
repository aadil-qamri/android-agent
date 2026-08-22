"""
android_agent.tools.android_knowledge

Tools for querying Android framework knowledge stored in SQLite.
"""

from __future__ import annotations

from typing import Any

from android_agent.storage.bytecode import BytecodeStore


class AndroidKnowledgeTool:
    """Provide access to Android framework bytecode knowledge."""

    def __init__(self, database_path: str) -> None:
        self.store = BytecodeStore(database_path)

    def search_class(
        self,
        name: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search for Android classes by name."""

        return self.store.find_classes(
            name=name,
            limit=limit,
        )

    def get_class(
        self,
        class_id: int,
    ) -> dict[str, Any] | None:
        """Get detailed information about a class."""

        return self.store.get_class(class_id)

    def search_method(
        self,
        name: str,
        limit: int = 20,
        class_name: str | None = None,
        descriptor: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for Android methods by name."""

        return self.store.find_methods(
            name=name,
            limit=limit,
            class_name=class_name,
            descriptor=descriptor,
        )

    def get_method_instructions(
        self,
        method_id: int,
    ) -> list[dict[str, Any]]:
        """Get the instructions belonging to a method."""

        return self.store.get_instructions(method_id)

    def get_method_calls(
        self,
        method_id: int,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get methods called by a method."""

        return self.store.get_method_calls(
            method_id=method_id,
            limit=limit,
        )

    def close(self) -> None:
        """Close the underlying knowledge database."""

        self.store.close()
