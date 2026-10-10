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
