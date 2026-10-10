"""Tests for input probing, naming, cancellation and actual audio extraction."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import imageio_ffmpeg

from converter import (
    ConversionCancelled, ConversionError, available_output_path,
    convert_video, duration_seconds, probe_media, progress_seconds,
)


class ParsingAndNamingTests(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(duration_seconds("Duration: 01:02:03.50, start: 0"), 3723.5)
        self.assertIsNone(duration_seconds("Duration: N/A"))

    def test_progress_timestamp(self):
        self.assertEqual(progress_seconds("00:00:12.50"), 12.5)
        self.assertIsNone(progress_seconds("N/A"))

    def test_unique_names_preserve_dots_and_existing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "meeting.v2.mp3").write_bytes(b"original")
            reserved = set()
            source = folder / "meeting.v2.mkv"
            first = available_output_path(source, folder, "mp3", reserved)
            second = available_output_path(source, folder, "mp3", reserved)
            self.assertEqual(first.name, "meeting.v2 (2).mp3")
            self.assertEqual(second.name, "meeting.v2 (3).mp3")
            self.assertEqual((folder / "meeting.v2.mp3").read_bytes(), b"original")

    def test_invalid_format_and_bitrate(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "source.mkv"
            with self.assertRaisesRegex(ConversionError, "Unsupported output format"):
                convert_video(file, file.with_suffix(".flac"), "flac", 128)
            with self.assertRaisesRegex(ConversionError, "Unsupported bitrate"):
                convert_video(file, file.with_suffix(".mp3"), "mp3", 17)

    def test_cancel_before_start(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.mkv"
            with self.assertRaises(ConversionCancelled):
                convert_video(source, source.with_suffix(".mp3"), "mp3", 128, is_cancelled=lambda: True)


class FFmpegIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    def _generate(self, target, has_audio=True):
        command = [self.ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
        command.extend(["-f", "lavfi", "-i", "color=c=black:s=32x32:r=5:d=1"])
        if has_audio:
            command.extend(["-f", "lavfi", "-i", "sine=frequency=440:duration=1"])
        command.extend(["-c:v", "mpeg4"])
        if has_audio:
            command.extend(["-c:a", "aac", "-shortest"])
        else:
            command.append("-an")
        command.append(str(target))
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_output_formats_without_a_console(self):
        video = self.folder / "meeting.v2.mkv"
        self._generate(video)
        self.assertGreater(probe_media(video, self.ffmpeg), 0.5)
        for fmt in ("mp3", "aac", "wav"):
            with self.subTest(fmt=fmt):
                output = self.folder / f"meeting.v2.{fmt}"
                updates = []
                convert_video(video, output, fmt, 128, on_progress=updates.append)
                self.assertTrue(output.exists())
                self.assertGreater(output.stat().st_size, 1000)
                self.assertEqual(updates[-1], 100)

    def test_silent_video_reports_clear_error(self):
        video = self.folder / "silent.mkv"
        self._generate(video, has_audio=False)
        with self.assertRaisesRegex(ConversionError, "No audio stream"):
            convert_video(video, self.folder / "silent.mp3", "mp3", 128)
        self.assertFalse((self.folder / "silent.mp3").exists())

    def test_preexisting_output_is_not_overwritten(self):
        video = self.folder / "input.mkv"
        self._generate(video)
        output = self.folder / "input.mp3"
        output.write_bytes(b"keep me")
        with self.assertRaisesRegex(ConversionError, "already exists"):
            convert_video(video, output, "mp3", 128)
        self.assertEqual(output.read_bytes(), b"keep me")

    def test_missing_input_reports_error(self):
        missing = self.folder / "missing.mkv"
        with self.assertRaisesRegex(ConversionError, "not found"):
            convert_video(missing, self.folder / "missing.mp3", "mp3", 128)

    def test_copy_fallback_keeps_existing_output_on_race(self):
        video = self.folder / "input.mkv"
        self._generate(video)
        output = self.folder / "input.mp3"

        def concurrent_output(_src, dst):
            Path(dst).write_bytes(b"another process")
            raise OSError("Hardlinks unavailable")

        with mock.patch("converter.os.link", side_effect=concurrent_output):
            with self.assertRaisesRegex(ConversionError, "already exists"):
                convert_video(video, output, "mp3", 128)
        self.assertEqual(output.read_bytes(), b"another process")

    def test_copy_fallback_succeeds_without_hardlinks(self):
        video = self.folder / "input.mkv"
        self._generate(video)
        output = self.folder / "input.mp3"
        with mock.patch("converter.os.link", side_effect=OSError("Unavailable")):
            convert_video(video, output, "mp3", 128)
        self.assertGreater(output.stat().st_size, 1000)
