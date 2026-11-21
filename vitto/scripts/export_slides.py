import os
import subprocess
import tempfile
from pathlib import Path


root = Path(__file__).resolve().parent.parent
source = root / "apresentacao-vitto.pptx"
target = root / "apresentacao-vitto.pdf"
soffice = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")

with tempfile.TemporaryDirectory(prefix="vitto-pdf-", ignore_cleanup_errors=True) as profile:
    env = os.environ.copy()
    env["HOME"] = profile
    env["XDG_CONFIG_HOME"] = str(Path(profile) / "config")
    env["XDG_CACHE_HOME"] = str(Path(profile) / "cache")
    Path(env["XDG_CONFIG_HOME"]).mkdir()
    Path(env["XDG_CACHE_HOME"]).mkdir()
    command = [
        str(soffice),
        f"-env:UserInstallation={Path(profile).as_uri()}",
        "--invisible",
        "--headless",
        "--norestore",
        "--convert-to",
        "pdf",
        "--outdir",
        str(root),
        str(source),
    ]
    result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=120)
    print(result.stdout.strip())
    print(result.stderr.strip())

if not target.exists() or target.stat().st_size == 0:
    raise SystemExit("LibreOffice não gerou o PDF dos slides.")
print(f"PDF criado: {target}")
