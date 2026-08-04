"""
Android build.prop parser.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from android_agent.parsers.base import BaseParser


class BuildPropParser(BaseParser):
    """Parser for Android build.prop files."""

    @property
    def supported_types(self) -> list[str]:
        return ["build_prop"]

    def parse(self, path: str | Path) -> dict[str, Any]:
        """
        Parse a build.prop file.

        Args:
            path:
                Path to the build.prop file.

        Returns:
            Dictionary of Android properties.
        """

        path = Path(path)

        properties: dict[str, str] = {}

        with path.open("r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                line = line.strip()

                # Skip blank lines
                if not line:
                    continue

                # Skip comments
                if line.startswith("#"):
                    continue

                # Skip malformed lines
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)

                properties[key.strip()] = value.strip()

        return {
            "type": "build_prop",
            "properties": properties,
            "count": len(properties),
        }