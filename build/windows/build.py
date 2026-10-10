"""Build the standalone Windows application and optional Inno Setup installer.

This script creates a separate .venv-build: it never installs packages into
WhisperX, system Python, or the existing Video-to-Audio runtime venv.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
BUILD_VENV = PROJECT / ".venv-build"
APP_NAME = "Video-to-Audio"
VERSION = "0.1.0"


def python_in(venv: Path) -> Path:
    return venv / "Scripts" / "python.exe"


def run(*args: str | Path, env: dict[str, str] | None = None) -> None:
    print(">", subprocess.list2cmdline([str(arg) for arg in args]), flush=True)
    subprocess.run(
        [str(arg) for arg in args], cwd=PROJECT, env=env, check=True
    )


def find_iscc(explicit: str | None = None) -> Path | None:
    options: list[Path] = []
    if explicit:
        options.append(Path(explicit))
    if os.environ.get("INNO_SETUP_ISCC"):
        options.append(Path(os.environ["INNO_SETUP_ISCC"]))
    from_path = shutil.which("ISCC.exe")
    if from_path:
        options.append(Path(from_path))
    for key in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
        base = os.environ.get(key)
        if base:
            options.extend(
                [
                    Path(base) / "Inno Setup 6" / "ISCC.exe",
                    Path(base) / "Programs" / "Inno Setup 6" / "ISCC.exe",
                ]
            )
    for path in options:
        if path.is_file():
            return path.resolve()
    return None


def ensure_build_environment() -> Path:
    if not python_in(BUILD_VENV).is_file():
        print(f"Creating isolated build environment: {BUILD_VENV}")
        run(sys.executable, "-m", "venv", BUILD_VENV)
    python = python_in(BUILD_VENV)
    if not python.is_file():
        raise RuntimeError(f"Build environment's Python was not found: {python}")
    run(python, "-m", "pip", "install", "-r", PROJECT / "requirements.txt",
        "-r", PROJECT / "requirements-build.txt")
    return python


def run_tests(python: Path) -> None:
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    run(python, "-m", "unittest", "discover", "-s", "tests", "-v", env=env)


def pyinstaller_command(python: Path) -> list[str | Path]:
    """Use absolute asset paths because PyInstaller resolves data from --specpath."""
    icons = (PROJECT / "icons").resolve()
    if not icons.is_dir() or not (icons / "icon.ico").is_file():
        raise RuntimeError(f"Application icons were not found at: {icons}")
    return [
        python, "-m", "PyInstaller", "--clean", "--noconfirm",
        "--onedir", "--windowed", "--name", APP_NAME,
        "--icon", icons / "icon.ico",
        "--add-data", f"{icons}:icons",
        "--collect-all", "imageio_ffmpeg",
        "--distpath", PROJECT / "dist",
        "--workpath", PROJECT / "build" / "pyinstaller",
        "--specpath", PROJECT / "build" / "pyinstaller",
        PROJECT / "Video to Audio.py",
    ]


def build_app(python: Path) -> Path:
    run(*pyinstaller_command(python))

    bundle = PROJECT / "dist" / APP_NAME
    executable = bundle / f"{APP_NAME}.exe"
    if not executable.is_file():
        raise RuntimeError(f"Packaged GUI executable not found: {executable}")
    if not any(bundle.rglob("ffmpeg*.exe")):
        raise RuntimeError(
            "FFmpeg binary was not bundled. Do not distribute this build."
        )
    if not (bundle / "_internal" / "icons" / "Video to Audio.png").is_file():
        raise RuntimeError(
            "App icon resources are missing. Do not distribute this build."
        )
    print(f"Standalone application ready for manual testing: {executable}")
    return executable


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def build_installer(iscc: Path) -> Path:
    script = PROJECT / "installer" / "Video-to-Audio.iss"
    run(iscc, script)
    installer = PROJECT / "dist" / "installer" / f"{APP_NAME}-Setup-{VERSION}.exe"
    if not installer.is_file():
        raise RuntimeError(f"Inno Setup did not produce the expected file: {installer}")
    print(f"Installer ready for manual QA: {installer}")
    print(f"SHA256: {sha256(installer)}")
    return installer


def main() -> int:
    if os.name != "nt":
        raise SystemExit("Build the Windows executable on Windows.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--app-only", action="store_true",
        help="Build only the standalone app (skip Inno Setup installer).",
    )
    parser.add_argument(
        "--iscc", help="Path to Inno Setup 6 ISCC.exe (if not auto-detected)."
    )
    args = parser.parse_args()

    iscc = None if args.app_only else find_iscc(args.iscc)
    if not args.app_only and iscc is None:
        raise SystemExit(
            "Inno Setup 6 was not found. Install it first from "
            "https://jrsoftware.org/isdl.php, or pass --iscc PATH. "
            "Use --app-only to package the application without an installer."
        )

    python = ensure_build_environment()
    run_tests(python)
    build_app(python)

    if iscc is not None:
        build_installer(iscc)
    print("Build finished. Installer/manual GUI acceptance tests are still required.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Build failed (exit code {exc.returncode}).") from exc
