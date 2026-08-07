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

        class_records = []

        for cls in dex_classes:
            class_records.append(
                {
                    "name": cls.get_name(),
                    "superclass": cls.get_superclassname(),
                    "interfaces": cls.get_interfaces(),
                    "access": cls.get_access_flags_string(),
                }
            )

        print(class_records[0])
        print(f"\nTotal classes: {len(class_records)}")