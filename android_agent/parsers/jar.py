"""
android_agent.parsers.jar

Parser for Java archive (JAR) files.
"""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from android_agent.parsers.base import BaseParser
from android_agent.parsers.dex import DexParser
from android_agent.storage.bytecode import BytecodeStore


class JarParser(BaseParser):
    """Parser for JAR files."""

    def __init__(self, bytecode_store: BytecodeStore) -> None:
        self.bytecode_store = bytecode_store
        self.dex_parser = DexParser(bytecode_store)

    @property
    def supported_types(self) -> list[str]:
        return ["jar"]

    def parse(self, path: str | Path) -> dict:
        path = Path(path)

        dex_files = []
        compat_configs = []
        resource_files = []
        manifest = None
        other_files = []

        with zipfile.ZipFile(path, "r") as jar:
            infos = sorted(jar.infolist(), key=lambda i: i.filename)
            entries = [info.filename for info in infos]

            for info in infos:
                entry = info.filename

                if entry.endswith(".dex"):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir) / entry

                        with jar.open(entry) as src:
                            with temp_path.open("wb") as dst:
                                dst.write(src.read())

                        print(f"Parsing {entry} from {path.name}")

                        parsed = self.dex_parser.parse(
                            temp_path,
                            jar_name=path.name,
                            dex_name=entry,
                            dex_size=info.file_size,
                            compressed_size=info.compress_size,
                        )

                    dex_files.append(
                        {
                            "name": entry,
                            "size": info.file_size,
                            "compressed_size": info.compress_size,
                            "parsed": parsed,
                        }
                    )

                elif entry.endswith("_compat_config.xml"):
                    compat_configs.append(entry)

                elif entry.startswith("res/"):
                    resource_files.append(entry)

                elif entry == "META-INF/MANIFEST.MF":
                    manifest = entry

                else:
                    other_files.append(entry)

        return {
            "type": "jar",
            "entry_count": len(entries),
            "contains_classes_dex": bool(dex_files),
            "dex_files": dex_files,
            "compat_configs": compat_configs,
            "resource_files": resource_files,
            "manifest": manifest,
            "other_files": other_files,
            "entries": entries,
        }
