from pathlib import Path
import tempfile
import zipfile

from androguard.core.dex import DEX


jar_path = Path("knowledge/android11/raw/framework.jar")

with zipfile.ZipFile(jar_path) as jar:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "classes.dex"

        with jar.open("classes.dex") as src:
            temp_path.write_bytes(src.read())

        dex = DEX(temp_path.read_bytes())
        dex_classes = dex.get_classes()

        print(type(dex_classes[0]))
        print()

        cls = dex_classes[0]

        print("Name:", cls.get_name())
        print("Superclass:", cls.get_superclassname())
        print("Interfaces:", cls.get_interfaces())
        print("Access:", cls.get_access_flags_string())

        methods = cls.get_methods()

        print(f"\nMethod count: {len(methods)}")

        if methods:
            method = methods[0]

            print(type(method))
            print()

            print("Name:", method.get_name())
            print("Descriptor:", method.get_descriptor())
            print("Access:", method.get_access_flags_string())
            print("Class:", method.get_class_name())
            print("Short:", method.get_short_string())

            code = method.get_code()

            print("\nCode:", code)
            print("Code type:", type(code))

            if code is not None:
                instructions = method.get_instructions()

                print("\nInstructions type:", type(instructions))

                for instruction in method.get_instructions():
                    hex_data = instruction.get_hex()
                    print(type(instruction))
                    print("Name:", instruction.get_name())
                    print("Output:", instruction.get_output())
                    print("Size:", instruction.get_length())
                    print("get_length():", instruction.get_length())
                    print("Hex:", hex_data)
                    print("Hex byte length:", len(hex_data.split()))
                    print()

        print("\nSearching for method without code...")

        found = False

        for cls in dex_classes:
            for method in cls.get_methods():
                code = method.get_code()

                if code is None:
                    print("\nFound method without code:")
                    print("Class:", cls.get_name())
                    print("Name:", method.get_name())
                    print("Descriptor:", method.get_descriptor())
                    print("Access:", method.get_access_flags_string())

                    found = True
                    break

            if found:
                break

        if not found:
            print("No method without code found.")