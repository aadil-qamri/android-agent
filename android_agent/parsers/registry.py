"""
Parser registry.
"""

from __future__ import annotations

from android_agent.parsers.base import BaseParser
from android_agent.parsers.build_prop import BuildPropParser
from android_agent.parsers.jar import JarParser


class ParserRegistry:
    """Registry of available parsers."""

    def __init__(self) -> None:
        self._parsers: dict[str, BaseParser] = {}

        self.register(BuildPropParser())
        self.register(JarParser())

    def register(self, parser: BaseParser) -> None:
        """
        Register a parser.
        """

        for file_type in parser.supported_types:
            self._parsers[file_type] = parser

    def get(self, file_type: str) -> BaseParser | None:
        """
        Return a parser for a file type.
        """

        return self._parsers.get(file_type)

    def supported_types(self) -> list[str]:
        """
        Return all supported file types.
        """

        return sorted(self._parsers.keys())