"""
android_agent.ingest.scanner

Recursively scans a knowledge directory and returns all discovered files.
"""

from pathlib import Path


class Scanner:
    """Recursively scans directories for files."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def scan(self) -> list[Path]:
        """
        Scan the root directory recursively.

        Returns:
            A sorted list of file paths.

        Raises:
            FileNotFoundError:
                If the root directory does not exist.

            NotADirectoryError:
                If the supplied path is not a directory.
        """

        if not self.root.exists():
            raise FileNotFoundError(
                f"Directory not found: {self.root}"
            )

        if not self.root.is_dir():
            raise NotADirectoryError(
                f"Not a directory: {self.root}"
            )

        files: list[Path] = []

        for path in self.root.rglob("*"):
            # Ignore hidden files/directories
            if any(part.startswith(".") for part in path.parts):
                continue

            if path.is_file():
                # Ignore generated index files
                if path.name == "index.json":
                    continue

                files.append(path)

        return sorted(files)
