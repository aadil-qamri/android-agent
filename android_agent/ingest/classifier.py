"""
android_agent.ingest.classifier

Classifies files discovered by the scanner.
"""

from pathlib import Path


class Classifier:
    """Classifies files based on extension and filename."""

    FILE_TYPES = {
        ".apk": "apk",
        ".jar": "jar",
        ".dex": "dex",
        ".odex": "odex",
        ".oat": "oat",
        ".vdex": "vdex",
        ".xml": "xml",
        ".prop": "prop",
        ".rc": "init_rc",
        ".conf": "config",
        ".json": "json",
        ".txt": "text",
        ".smali": "smali",
        ".java": "java",
        ".kt": "kotlin",
        ".so": "native_library",
    }

    def classify(self, path: str | Path) -> str:
        """
        Classify a file.

        Args:
            path:
                File path.

        Returns:
            Classification string.
        """

        path = Path(path)

        if path.name == "build.prop":
            return "build_prop"

        if path.name.endswith(".xml") and "permissions" in path.parts:
            return "permission_xml"

        return self.FILE_TYPES.get(
            path.suffix.lower(),
            "unknown",
        )
