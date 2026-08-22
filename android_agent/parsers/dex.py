"""
android_agent.parsers.dex

Parser for Dalvik Executable (DEX) files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from androguard.core.dex import DEX

from android_agent.parsers.base import BaseParser
from android_agent.storage.bytecode import BytecodeStore


class DexParser(BaseParser):
    """Parser for Dalvik Executable (DEX) files."""

    INVOKE_OPCODES = {
        "invoke-direct",
        "invoke-virtual",
        "invoke-static",
        "invoke-interface",
        "invoke-super",
    }

    def __init__(self, bytecode_store: BytecodeStore) -> None:
        self.bytecode_store = bytecode_store

    @property
    def supported_types(self) -> list[str]:
        return ["dex"]

    @staticmethod
    def _extract_method_reference(
        instruction: Any,
    ) -> tuple[str, str, str] | None:
        """Extract a referenced method from an invoke instruction."""

        opcode = instruction.get_name()

        if opcode not in DexParser.INVOKE_OPCODES:
            return None

        operands = instruction.get_operands()

        if not operands:
            return None

        reference = operands[-1]

        if not isinstance(reference, tuple) or len(reference) < 3:
            return None

        reference_text = reference[-1]

        if not isinstance(reference_text, str):
            return None

        separator = reference_text.find("->")

        if separator == -1:
            return None

        target_class = reference_text[:separator]
        method_reference = reference_text[separator + 2 :]

        descriptor_start = method_reference.find("(")

        if descriptor_start == -1:
            return None

        target_method = method_reference[:descriptor_start]
        target_descriptor = method_reference[descriptor_start:]

        if not target_class or not target_method or not target_descriptor:
            return None

        return (
            target_class,
            target_method,
            target_descriptor,
        )

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
                            opcode = instruction.get_name()
                            output = instruction.get_output()

                            self.bytecode_store.add_instruction(
                                method_id=method_id,
                                offset=offset,
                                opcode=opcode,
                                output=output,
                            )

                            method_reference = self._extract_method_reference(
                                instruction
                            )

                            if method_reference is not None:
                                (
                                    target_class,
                                    target_method,
                                    target_descriptor,
                                ) = method_reference

                                self.bytecode_store.add_method_call(
                                    caller_method_id=method_id,
                                    target_class=target_class,
                                    target_method=target_method,
                                    target_descriptor=target_descriptor,
                                    opcode=opcode,
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
