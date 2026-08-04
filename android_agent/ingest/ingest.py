"""
android_agent.ingest.ingest

Coordinates the knowledge ingestion pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

from android_agent.ingest.classifier import Classifier
from android_agent.ingest.metadata import MetadataExtractor
from android_agent.ingest.scanner import Scanner
from android_agent.parsers.registry import ParserRegistry


class Ingestor:
    """Coordinates the ingestion pipeline."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.scanner = Scanner(self.root)
        self.classifier = Classifier()
        self.metadata = MetadataExtractor()
        self.registry = ParserRegistry()

    def ingest(self) -> list[dict]:
        """
        Run the ingestion pipeline.

        Returns:
            List of metadata records.
        """

        records: list[dict] = []

        for file in self.scanner.scan():
            file_type = self.classifier.classify(file)

            record = self.metadata.extract(file, file_type)

            parser = self.registry.get(file_type)

            if parser is not None:
                record["parsed"] = parser.parse(file)

            records.append(record)

        return records
    

    def save(
        self,
        output: str | Path,
        records: list[dict],
    ) -> None:
        """
        Save metadata records as JSON.
        """

        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)

        with output.open("w", encoding="utf-8") as f:
            json.dump(
                records,
                f,
                indent=4,
                ensure_ascii=False,
            )
