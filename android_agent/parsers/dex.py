"""
android_agent.parsers.dex

Parser for Dalvik Executable (DEX) files.
"""

from __future__ import annotations

from pathlib import Path

from androguard.core.dex import DEX

from android_agent.parsers.base import BaseParser
from android_agent.storage.bytecode import BytecodeStore


class DexParser(BaseParser):
    """Parser for Dalvik Executable (DEX) files."""

    def __init__(self, bytecode_store: BytecodeStore) -> None:
        self.bytecode_store = bytecode_store

    @property
    def supported_types(self) -> list[str]:
        return ["dex"]

    def parse(
        self,
        path: str | Path,
        jar_name: str,
        dex_name: str,
        dex_size: int,
        compressed_size: int,
    ) -> dict:
        """
        Parse a DEX file and store detailed bytecode data in SQLite.
        """

        path = Path(path)

        packages = set()
        class_count = 0

        try:
            with path.open("rb") as f:
                dex = DEX(f.read())

            dex_id = self.bytecode_store.add_dex_file(
                jar_name=jar_name,
                dex_name=dex_name,
                size=dex_size,
                compressed_size=compressed_size,
            )

            for cls in dex.get_classes():
                name = cls.get_name()

                # TODO:
                # Handle DEX classes without a package path.

                package = name[1:].rsplit("/", 1)[0]
                packages.add(package)

                class_id = self.bytecode_store.add_class(
                    dex_id=dex_id,
                    name=name,
                    superclass=cls.get_superclassname(),
                    access=cls.get_access_flags_string(),
                )

                for interface in cls.get_interfaces():
                    self.bytecode_store.add_class_interface(
                        class_id=class_id,
                        interface=interface,
                    )

                for method in cls.get_methods():
                    method_id = self.bytecode_store.add_method(
                        class_id=class_id,
                        name=method.get_name(),
                        descriptor=method.get_descriptor(),
                        access=method.get_access_flags_string(),
                    )

                    code = method.get_code()

                    if code is not None:
                        offset = 0

                        for instruction in method.get_instructions():
                            self.bytecode_store.add_instruction(
                                method_id=method_id,
                                offset=offset,
                                opcode=instruction.get_name(),
                                output=instruction.get_output(),
                            )

                            offset += instruction.get_length() // 2

                class_count += 1

            self.bytecode_store.commit()

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
            "class_count": class_count,
            "package_count": len(packages),
            "classes": [],
            "packages": sorted(packages),
        }