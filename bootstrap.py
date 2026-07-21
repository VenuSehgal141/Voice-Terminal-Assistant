"""Bootstrap installer and environment helper for the project.

Provides:
- automatic venv creation if missing
- dependency installation with fallbacks for Windows audio
- detection of available Python interpreter
- helper to run the app with the right interpreter
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VENV_DIR = ROOT / "venv"
REQUIREMENTS = ROOT / "requirements.txt"

PY_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"


def run(cmd, check=True):
    print(f"$ {cmd}")
    subprocess.check_call(cmd, shell=True)


def ensure_venv():
    if VENV_DIR.exists():
        print("venv already present")
        return
    # Try to create a venv using a sensible Python interpreter.
    candidates = []

    # 1) Explicit override via env var
    env_python = os.environ.get("BOOTSTRAP_PYTHON")
    if env_python:
        candidates.append(env_python)

    # 2) Current interpreter
    candidates.append(sys.executable)

    # 3) Common names
    for name in ("python3", "python", "py"):
        p = shutil.which(name)
        if p:
            candidates.append(p)

    # 4) Windows-specific common location used earlier
    common = Path("F:/py/python.exe")
    if common.exists():
        candidates.append(str(common))

    # Deduplicate while preserving order
    seen = set()
    candidates = [c for c in candidates if not (c in seen or seen.add(c))]

    for py in candidates:
        try:
            print(f"Creating virtual environment using: {py}")
            run(f'"{py}" -m venv venv')
            return
        except Exception:
            print(f"Failed to create venv with: {py}")

    # Last resort: try current interpreter directly (may raise)
    print("Creating virtual environment with current interpreter...")
    run(f"{sys.executable} -m venv venv")


def install_requirements():
    pip = VENV_DIR / "Scripts" / "pip.exe" if os.name == "nt" else VENV_DIR / "bin" / "pip"
    if not pip.exists():
        raise SystemExit("pip not found in venv")

    print("Installing requirements (core packages)...")
    run(f'"{pip}" install --upgrade pip setuptools wheel')
    # Install core packages; pocketsphinx build is optional on Windows
    run(f'"{pip}" install SpeechRecognition pyaudio pydub python-dotenv')

    if os.name == "nt":
        print("Skipping pocketsphinx build on Windows by default (optional). To install, follow README instructions.")
    else:
        run(f'"{pip}" install pocketsphinx')


def print_help():
    print("Bootstrap helper commands:")
    print("  python bootstrap.py install")
    print("  python bootstrap.py run [--use-venv|--system]")
    print("    --use-venv   Run using the project's venv Python (creates venv if missing)")
    print("    --system     Run using the system Python interpreter")


def run_app():
    python = VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"
    if not python.exists():
        raise SystemExit("virtualenv not found; run 'python bootstrap.py install' first")

    run(f'"{python}" main.py')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "install":
        ensure_venv()
        install_requirements()

    elif cmd == "run":
        # parse optional flags
        flags = sys.argv[2:]
        use_venv = None
        if "--use-venv" in flags:
            use_venv = True
        elif "--system" in flags:
            use_venv = False

        if use_venv is None:
            # prefer venv if present
            use_venv = VENV_DIR.exists()

        if use_venv:
            # ensure venv exists (create if missing)
            ensure_venv()
            run_app()
        else:
            # Run using system python
            run(f'"{sys.executable}" main.py')

    else:
        print_help()
