"""Static packaging checks runnable on development machines and in CI.

These tests do not claim that a Windows installer has been successfully built.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "build" / "windows" / "build.py"
SPEC = importlib.util.spec_from_file_location("windows_build", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
windows_build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(windows_build)


class PackagingTests(unittest.TestCase):
    def test_version_matches_inno_and_expected_output(self):
        self.assertEqual(windows_build.VERSION, "0.3.1")
        self.assertEqual(windows_build.APP_NAME, "Video-to-Audio")
        installer = (ROOT / "installer" / "Video-to-Audio.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn('#define MyAppVersion "0.3.1"', installer)
        self.assertIn("PrivilegesRequired=lowest", installer)
        self.assertIn("DefaultDirName={localappdata}", installer)
        self.assertIn("UninstallDisplayIcon=", installer)

    def test_pyinstaller_instructions_bundle_icons_and_ffmpeg(self):
        command = list(map(str, windows_build.pyinstaller_command(Path("python.exe"))))
        self.assertEqual(command[command.index("--add-data") + 1],
                         f"{(ROOT / 'icons').resolve()}:icons")
        self.assertEqual(command[command.index("--icon") + 1],
                         str((ROOT / "icons" / "icon.ico").resolve()))
        self.assertIn("--onedir", command)
        self.assertIn("--windowed", command)
        self.assertEqual(command[command.index("--collect-all") + 1],
                         "imageio_ffmpeg")
        self.assertEqual(command[command.index("--specpath") + 1],
                         str(ROOT / "build" / "pyinstaller"))
        self.assertIn('".venv-build"', SCRIPT.read_text(encoding="utf-8"))

    def test_missing_icons_fail_before_pyinstaller_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(windows_build, "PROJECT", Path(directory)):
                with self.assertRaisesRegex(RuntimeError, "icons were not found"):
                    windows_build.pyinstaller_command(Path("python.exe"))

    def test_iscc_lookup_accepts_explicit_path(self):
        with tempfile.TemporaryDirectory() as directory:
            compiler = Path(directory) / "ISCC.exe"
            compiler.write_bytes(b"placeholder")
            self.assertEqual(
                windows_build.find_iscc(str(compiler)), compiler.resolve()
            )

    def test_bilingual_setup_languages_and_shortcuts(self):
        script = (ROOT / "installer" / "Video-to-Audio.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn('Name: "en"; MessagesFile: "compiler:Default.isl"', script)
        self.assertIn("BrazilianPortuguese.isl", script)
        self.assertIn("ptbr.DesktopShortcut=", script)
        self.assertIn("ptbr.LaunchApp=", script)
        self.assertIn('Description: "{cm:DesktopShortcut}"', script)
        self.assertIn('Description: "{cm:LaunchApp}"', script)

    def test_build_runs_syntax_gate_before_dependency_installation(self):
        builder = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('def check_source_syntax(python: Path)', builder)
        self.assertIn('PROJECT / "i18n.py"', builder)
        self.assertIn('PROJECT / "tests"', builder)
        self.assertIn('PROJECT / "build" / "windows" / "build.py"', builder)
        self.assertLess(
            builder.index("    check_source_syntax(Path(sys.executable))"),
            builder.index("    python = ensure_build_environment()"),
        )

    def test_english_first_and_translated_license_by_installer_language(self):
        setup = (ROOT / "installer" / "Video-to-Audio.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn("LanguageDetectionMethod=none", setup)
        # An upgrade must not silently preselect Portuguese from the last install.
        self.assertIn("UsePreviousLanguage=no", setup)
        self.assertIn("ShowLanguageDialog=yes", setup)
        self.assertIn("en.SelectLanguageTitle=Setup language / Idioma da instalação", setup)
        self.assertIn("ptbr.SelectLanguageLabel=Select the installer language / Selecione o idioma do instalador:", setup)
        english = 'Name: "en"; MessagesFile: "compiler:Default.isl";'
        portuguese = 'Name: "ptbr"; MessagesFile: "compiler:Languages\\BrazilianPortuguese.isl";'
        self.assertLess(setup.index(english), setup.index(portuguese))
        self.assertIn('LicenseFile: "..\\LICENSE"', setup)
        self.assertIn('LicenseFile: "..\\installer\\LICENSE.pt-BR.txt"', setup)
        self.assertIn('Source: "..\\installer\\LICENSE.pt-BR.txt"; DestDir: "{app}"', setup)

        original = (ROOT / "LICENSE").read_text(encoding="utf-8").strip()
        localized = (ROOT / "installer" / "LICENSE.pt-BR.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("TRADUÇÃO INFORMATIVA", localized)
        self.assertIn("NÃO é uma versão oficial", localized)
        self.assertIn("LICENÇA APACHE", localized)
        self.assertIn("TERMOS E CONDIÇÕES DE USO", localized)
        for heading in (
            "1. Definições.", "2. Concessão de licença de direitos autorais.",
            "3. Concessão de licença de patentes.", "4. Redistribuição.",
            "5. Submissão de Contribuições.", "6. Marcas.",
            "7. Isenção de garantias.", "8. Limitação de responsabilidade.",
            "9. Aceitação de garantias ou responsabilidades adicionais.",
        ):
            self.assertIn(heading, localized)
        self.assertIn("APÊNDICE: Como aplicar a Licença Apache", localized)
        self.assertIn("ÚNICA VERSÃO JURIDICAMENTE VINCULANTE", localized)
        self.assertTrue(localized.rstrip().endswith(original))

    def test_includes_full_gpl_and_bsd_texts_in_installer(self):
        setup = (ROOT / "installer" / "Video-to-Audio.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'Source: "..\\LICENSES\\GPL-3.0-only.txt"; DestDir: "{app}\\licenses"',
            setup,
        )
        self.assertIn(
            'Source: "..\\LICENSES\\BSD-2-Clause-imageio-ffmpeg.txt"; '
            'DestDir: "{app}\\licenses"',
            setup,
        )
        self.assertIn('Source: "..\\LICENSE"; DestDir: "{app}"', setup)
        gpl = (ROOT / "LICENSES" / "GPL-3.0-only.txt").read_text(encoding="utf-8")
        bsd = (ROOT / "LICENSES" / "BSD-2-Clause-imageio-ffmpeg.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("GNU GENERAL PUBLIC LICENSE", gpl)
        self.assertIn("Version 3, 29 June 2007", gpl)
        self.assertIn("BSD 2-Clause License", bsd)
        self.assertIn("imageio", bsd)
        audit_script = ROOT / "scripts" / "audit_windows_distribution.ps1"
        self.assertTrue(audit_script.is_file())
        self.assertIn("ffmpeg-inventory.json", audit_script.read_text(encoding="utf-8"))
