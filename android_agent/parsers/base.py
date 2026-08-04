"""
Base parser interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseParser(ABC):
    """Base class for all Android parsers."""

    @property
    @abstractmethod
    def supported_types(self) -> list[str]:
        """
        Return the file types this parser supports.
        """
        raise NotImplementedError

    @abstractmethod
    def parse(self, path: str | Path) -> dict[str, Any]:
        """
        Parse a file and return structured data.
        """
        raise NotImplementedError