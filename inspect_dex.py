from pathlib import Path
import tempfile
import zipfile

from androguard.core.dex import DEX


jar_path = Path("knowledge/android11/raw/framework.jar")

wanted = {
    "invoke-direct",
    "invoke-virtual",
    "invoke-static",
    "invoke-interface",
    "invoke-super",
}

found = set()

with zipfile.ZipFile(jar_path) as jar:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "classes.dex"

        with jar.open("classes.dex") as src:
            temp_path.write_bytes(src.read())

        dex = DEX(temp_path.read_bytes())

        for cls in dex.get_classes():
            for method in cls.get_methods():
                code = method.get_code()

                if code is None:
                    continue

                for instruction in method.get_instructions():
                    opcode = instruction.get_name()

                    if opcode not in wanted or opcode in found:
                        continue

                    print("=" * 60)
                    print("Class:", cls.get_name())
                    print("Method:", method.get_name())
                    print("Descriptor:", method.get_descriptor())
                    print("Instruction type:", type(instruction))
                    print("Opcode:", opcode)
                    print("Output:", instruction.get_output())
                    print("Operands:", instruction.get_operands())
                    print("Ref kind:", instruction.get_ref_kind())
                    print("Hex:", instruction.get_hex())

                    found.add(opcode)

                    if found == wanted:
                        break

                if found == wanted:
                    break

            if found == wanted:
                break

print()
print("Found:", sorted(found))
print("Missing:", sorted(wanted - found))