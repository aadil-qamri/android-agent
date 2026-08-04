"""
Knowledge ingestion entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path

from android_agent.ingest.ingest import Ingestor


def main() -> None:
    """Run the knowledge ingestion pipeline."""

    if len(sys.argv) != 2:
        print("Usage:")
        print("  python ingest_knowledge.py <knowledge_directory>")
        sys.exit(1)

    root = Path(sys.argv[1])

    ingestor = Ingestor(root)

    records = ingestor.ingest()

    output = root / "index.json"

    ingestor.save(output, records)

    print(f"Ingested {len(records)} files.")
    print(f"Saved index to: {output}")


if __name__ == "__main__":
    main()
