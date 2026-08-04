"""
android_agent.parsers.dex

Parser for Dalvik Executable (DEX) files.
"""

from __future__ import annotations
from pathlib import Path
from androguard.core.dex import DEX
from android_agent.parsers.base import BaseParser


class DexParser(BaseParser):
    """Parser for Dalvik Executable (DEX) files."""

    @property
    def supported_types(self) -> list[str]:
        return ["dex"]

    def parse(self, path: str | Path) -> dict:
        """
        Parse a DEX file.

        Args:
            path: Path to the DEX file.

        Returns:
            Parsed DEX metadata.
        """

        path = Path(path)

        classes = []
        packages = set()

        try:
            with path.open("rb") as f:
                dex = DEX(f.read())

            for cls in dex.get_classes():
                name = cls.get_name()
                classes.append(name)

                package = name[1:].rsplit("/", 1)[0]
                packages.add(package)

        except Exception as e:
            return {
            "type": "dex",
            "name": path.name,
            "error": str(e),
            "class_count": 0,
            "package_count": 0,
            "classes": [],
            "packages": [],
            }

        return {
    "type": "dex",
    "name": path.name,
    "class_count": len(classes),
    "package_count": len(packages),
    "classes": classes,
    "packages": sorted(packages),
    }