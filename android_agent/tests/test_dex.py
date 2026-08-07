from pathlib import Path
import tempfile
import zipfile

from androguard.core.dex import DEX

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JAR = PROJECT_ROOT / "knowledge/android11/raw/framework.jar"

with zipfile.ZipFile(JAR) as jar:
    for entry in sorted(jar.namelist()):
        if not entry.endswith(".dex"):
            continue

        print(f"\n=== Testing {entry} ===")

        with tempfile.TemporaryDirectory() as td:
            dex_path = Path(td) / entry

            with jar.open(entry) as src:
                dex_path.write_bytes(src.read())

            try:
                DEX(dex_path.read_bytes())
                print("SUCCESS")
            except Exception as e:
                print("FAILED")
                print(type(e).__name__)
                print(e)