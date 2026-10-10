"""Static packaging checks runnable on development machines and in CI.

These tests do not claim that a Windows installer has been successfully built.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "build" / "windows" / "build.py"
SPEC = importlib.util.spec_from_file_location("windows_build", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
windows_build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(windows_build)


class PackagingTests(unittest.TestCase):
    def test_version_matches_inno_and_expected_output(self):
        self.assertEqual(windows_build.VERSION, "0.1.0")
        self.assertEqual(windows_build.APP_NAME, "Video-to-Audio")
        installer = (ROOT / "installer" / "Video-to-Audio.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn('#define MyAppVersion "0.1.0"', installer)
        self.assertIn("PrivilegesRequired=lowest", installer)
        self.assertIn("DefaultDirName={localappdata}", installer)
        self.assertIn("UninstallDisplayIcon=", installer)

    def test_pyinstaller_instructions_bundle_icons_and_ffmpeg(self):
        builder = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"--collect-all", "imageio_ffmpeg"', builder)
        self.assertIn('"--add-data", "icons:icons"', builder)
        self.assertIn('"--onedir", "--windowed"', builder)
        self.assertIn('".venv-build"', builder)

    def test_iscc_lookup_accepts_explicit_path(self):
        with tempfile.TemporaryDirectory() as directory:
            compiler = Path(directory) / "ISCC.exe"
            compiler.write_bytes(b"placeholder")
            self.assertEqual(
                windows_build.find_iscc(str(compiler)), compiler.resolve()
            )
