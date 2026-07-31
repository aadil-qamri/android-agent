"""
android_agent.ingest.metadata

Extracts filesystem metadata from discovered files.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class MetadataExtractor:
    """Extract metadata from files."""

    def extract(self, path: str | Path, file_type: str) -> dict:
        """
        Extract metadata for a file.

        Args:
            path:
                Path to the file.

            file_type:
                Classification returned by Classifier.

        Returns:
            Dictionary containing file metadata.
        """

        path = Path(path)

        stat = path.stat()

        return {
            "name": path.name,
            "path": str(path),
            "parent": str(path.parent),
            "extension": path.suffix.lower(),
            "type": file_type,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "sha256": self._sha256(path),
        }

    @staticmethod
    def _sha256(path: Path) -> str:
        """
        Compute the SHA-256 hash of a file.
        """

        hasher = hashlib.sha256()

        with path.open("rb") as file:
            while chunk := file.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()
