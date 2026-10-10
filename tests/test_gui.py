"""Smoke-test the Qt interface in headless mode."""

import os
import runpy
import unittest
from pathlib import Path

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
