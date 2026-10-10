"""Smoke-test the Qt interface in headless mode."""

import os
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

APP = runpy.run_path(str(Path(__file__).resolve().parents[1] / "Video to Audio.py"))


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_window_and_format_specific_bitrate(self):
        window = APP["VideoToAudioApp"]()
        window.set_language("en")
        self.assertIn("Video to Audio", window.windowTitle())
        self.assertFalse(window.cancel_btn.isEnabled())
        window.format_combo.setCurrentText("wav")
        self.assertFalse(window.bitrate_combo.isEnabled())
        window.format_combo.setCurrentText("mp3")
        self.assertTrue(window.bitrate_combo.isEnabled())
        window.close()

    def test_output_location_is_automatic_and_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            first.mkdir()
            second.mkdir()
            one = first / "meeting.mkv"
            two = second / "meeting.mkv"
            one.write_bytes(b"fake video")
            two.write_bytes(b"fake video")

            window = APP["VideoToAudioApp"]()
            window.set_language("en")
            window.add_files([str(one)])
            self.assertIsNone(window.output_dir)
            self.assertIn(str(first), window.output_label.text())
            self.assertTrue(window.output_hint.isHidden())

            window.add_files([str(two)])
            self.assertIn("2 locations", window.output_label.text())
            self.assertIn(str(first), window.output_label.text())
            self.assertIn(str(second), window.output_label.text())
            self.assertFalse(window.output_hint.isHidden())
            self.assertIn(str(second), window.video_list.item(1).toolTip())

            window.output_dir = root
            window._update_output_location()
            self.assertIn("(chosen folder)", window.output_label.text())
            self.assertTrue(window.output_hint.isHidden())
            self.assertTrue(window.original_btn.isEnabled())
            self.assertIn(f"Save audio to: {root}", window.video_list.item(0).toolTip())

            window.use_original_folders()
            self.assertIsNone(window.output_dir)
            self.assertFalse(window.original_btn.isEnabled())
            self.assertFalse(window.output_hint.isHidden())

            window.clear_video_list()
            self.assertIsNone(window.output_dir)
            self.assertEqual(window.video_list.count(), 0)
            self.assertIn("(automatic)", window.output_label.text())
            window.close()

    def test_folder_picker_is_optional_and_cancellation_preserves_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "example.mkv"
            source.write_bytes(b"fake video")
            window = APP["VideoToAudioApp"]()
            window.set_language("en")
            window.add_files([str(source)])
            with mock.patch.object(APP["QFileDialog"], "getExistingDirectory", return_value=""):
                window.select_output_folder()
            self.assertIsNone(window.output_dir)
            self.assertIn(str(root), window.output_label.text())
            window.close()

    def test_worker_targets_each_source_folder_or_optional_common_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            shared = root / "output"
            for folder in (first, second, shared):
                folder.mkdir()
            one = first / "meeting.mkv"
            two = second / "meeting.mkv"
            one.write_bytes(b"video")
            two.write_bytes(b"video")
            outputs = []

            def fake_convert(source, dest, fmt, bitrate, **kwargs):
                outputs.append(Path(dest))
                if kwargs.get("on_progress"):
                    kwargs["on_progress"](100)

            with mock.patch.dict(
                APP["ConvertThread"].run.__globals__,
                {"convert_video": fake_convert},
            ):
                default_worker = APP["ConvertThread"]([one, two], "mp3", None, 128)
                default_worker.run()
                self.assertEqual(
                    outputs, [first / "meeting.mp3", second / "meeting.mp3"]
                )

                outputs.clear()
                shared_worker = APP["ConvertThread"](
                    [one, two], "mp3", shared, 128
                )
                shared_worker.run()
                self.assertEqual(
                    outputs, [shared / "meeting.mp3", shared / "meeting (2).mp3"]
                )

    def test_success_clears_batch_but_keeps_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "example.mkv"
            source.write_bytes(b"video")
            window = APP["VideoToAudioApp"]()
            window.set_language("en")
            window.add_files([str(source)])
            window.output_dir = root
            window._update_output_location()
            with mock.patch.object(APP["QMessageBox"], "information") as info:
                window._on_result(1, [], False)
            info.assert_called_once()
            self.assertEqual(window.video_list.count(), 0)
            self.assertEqual(window.video_paths, [])
            self.assertIsNone(window.output_dir)
            self.assertEqual(window.progress_bar.value(), 100)
            self.assertIn("Complete: 1", window.progress_label.text())
            window.close()

    def test_failure_and_cancellation_keep_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "example.mkv"
            source.write_bytes(b"video")
            window = APP["VideoToAudioApp"]()
            window.set_language("en")
            window.add_files([str(source)])
            with mock.patch.object(APP["QMessageBox"], "warning"):
                window._on_result(
                    0, ["example.mkv: No audio stream found: example.mkv"], False
                )
            self.assertEqual(window.video_list.count(), 1)
            with mock.patch.object(APP["QMessageBox"], "information"):
                window._on_result(0, [], True)
            self.assertEqual(window.video_list.count(), 1)
            window.close()

    def test_portuguese_localization_and_switch_back_to_english(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "gravacao.mkv"
            source.write_bytes(b"video")
            window = APP["VideoToAudioApp"]()
            window.set_language("pt_BR")
            window.add_files([str(source)])
            self.assertIn("Conversor de Vídeo para Áudio", window.windowTitle())
            self.assertEqual(window.convert_btn.text(), "Converter")
            self.assertEqual(window.clear_btn.text(), "Limpar lista")
            self.assertIn("Salvar áudio em:", window.output_label.text())
            self.assertEqual(window.language_label.text(), "Idioma:")
            self.assertIn("Nenhuma faixa de áudio", window._localized_error(
                "gravacao.mkv: No audio stream found: gravacao.mkv"
            ))
            with mock.patch.object(APP["QMessageBox"], "information") as info:
                window._on_result(1, [], False)
            self.assertIn("Concluído: 1", info.call_args.args[2])
            self.assertEqual(window.video_list.count(), 0)
            window.set_language("en")
            self.assertEqual(window.convert_btn.text(), "Convert")
            self.assertEqual(window.language_label.text(), "Language:")
            window.close()

    def test_manual_language_setting_is_persisted(self):
        window = APP["VideoToAudioApp"]()
        settings = window.settings
        previous = settings.value("ui/language", None)
        try:
            window.language_combo.setCurrentIndex(
                window.language_combo.findData("pt_BR")
            )
            self.assertEqual(settings.value("ui/language"), "pt_BR")
            self.assertEqual(window.language, "pt_BR")
        finally:
            if previous is None:
                settings.remove("ui/language")
            else:
                settings.setValue("ui/language", previous)
            window.close()

    def test_language_combo_changes_all_visible_text_both_directions(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "meeting.mkv"
            source.write_bytes(b"test")
            window = APP["VideoToAudioApp"]()
            settings = window.settings
            previous = settings.value("ui/language", None)
            try:
                window.language_combo.setCurrentIndex(
                    window.language_combo.findData("en")
                )
                self.assertEqual(window.language_combo.itemData(0), "en")
                self.assertEqual(window.language_combo.itemData(1), "pt_BR")
                self.assertEqual(window.language, "en")
                window.add_files([str(source)])
                window._set_status("progress", name="meeting.mkv", current=20, overall=20)
                self.assertEqual(window.select_btn.text(), "Select Videos")
                self.assertIn("Save audio to:", window.output_label.text())
                self.assertIn("(batch: 20%)", window.progress_label.text())

                window.language_combo.setCurrentIndex(
                    window.language_combo.findData("pt_BR")
                )
                self.assertEqual(window.language, "pt_BR")
                self.assertEqual(window.select_btn.text(), "Selecionar vídeos")
                self.assertEqual(window.original_btn.text(), "Usar pastas de origem")
                self.assertIn("Salvar áudio em:", window.output_label.text())
                self.assertIn("Origem:", window.video_list.item(0).toolTip())
                self.assertIn("(lote: 20%)", window.progress_label.text())
                self.assertIn("Vídeo", window.windowTitle())

                window.language_combo.setCurrentIndex(
                    window.language_combo.findData("en")
                )
                self.assertEqual(window.language, "en")
                self.assertEqual(window.clear_btn.text(), "Clear List")
                self.assertEqual(window.convert_btn.text(), "Convert")
                self.assertIn("Save audio to:", window.output_label.text())
                self.assertIn("Source:", window.video_list.item(0).toolTip())
                self.assertIn("(batch: 20%)", window.progress_label.text())
            finally:
                if previous is None:
                    settings.remove("ui/language")
                else:
                    settings.setValue("ui/language", previous)
                window.close()

    def test_legacy_auto_setting_migrates_to_english_default(self):
        window = APP["VideoToAudioApp"]()
        settings = window.settings
        previous = settings.value("ui/language", None)
        try:
            settings.setValue("ui/language", "auto")
            other = APP["VideoToAudioApp"]()
            try:
                self.assertEqual(other.language_choice, "en")
                self.assertEqual(other.language_combo.currentData(), "en")
                self.assertEqual(other.convert_btn.text(), "Convert")
            finally:
                other.close()
        finally:
            if previous is None:
                settings.remove("ui/language")
            else:
                settings.setValue("ui/language", previous)
            window.close()
