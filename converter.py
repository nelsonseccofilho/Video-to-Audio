"""FFmpeg-backed audio extraction with no dependency on an open console."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import imageio_ffmpeg

SUPPORTED_FORMATS = {
    "mp3": ("libmp3lame", "mp3"),
    "aac": ("aac", "adts"),
    "wav": ("pcm_s16le", "wav"),
}
BITRATES = {64, 128, 192, 256, 320}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"}


class ConversionError(Exception):
    """A recoverable, user-facing error affecting one input."""


class ConversionCancelled(Exception):
    """The current conversion was cancelled by the user."""


def duration_seconds(text: str) -> float | None:
    """Extract a media duration from FFmpeg's stream metadata or progress time."""
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    if match is None:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def progress_seconds(value: str) -> float | None:
    """Parse FFmpeg's HH:MM:SS.microseconds progress timestamp."""
    match = re.fullmatch(r"(\d+):(\d+):(\d+(?:\.\d+)?)", value.strip())
    if match is None:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def available_output_path(source: Path, output_dir: Path, fmt: str, reserved: set[str]) -> Path:
    """Reserve a unique filename, even with repeated basenames in a batch."""
    stem = source.stem
    index = 1
    while True:
        name = f"{stem}.{fmt}" if index == 1 else f"{stem} ({index}).{fmt}"
        candidate = output_dir / name
        key = name.casefold()
        if key not in reserved and not candidate.exists():
            reserved.add(key)
            return candidate
        index += 1


def probe_media(source: Path, ffmpeg: str) -> float | None:
    """Check for an audio stream and return the duration, if reported."""
    if not source.is_file():
        raise ConversionError(f"File not found: {source}")
    try:
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-i", str(source)],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConversionError(f"Cannot inspect video: {exc}") from exc
    metadata = result.stderr + result.stdout
    if not re.search(r"^\s*Stream #.*:\s*Audio:", metadata, re.MULTILINE):
        raise ConversionError(f"No audio stream found: {source.name}")
    return duration_seconds(metadata)


def convert_video(
    source: Path,
    destination: Path,
    fmt: str,
    bitrate: int,
    on_progress: Callable[[int], None] | None = None,
    is_cancelled: Callable[[], bool] | None = None,
    on_process: Callable[[subprocess.Popen | None], None] | None = None,
) -> None:
    """Convert an input to audio via FFmpeg; never overwrite an existing file.

    Progress callbacks represent the real output timestamp, not a UI timer.
    The temporary output is cleaned up on failure or cancellation.
    """
    source = Path(source)
    destination = Path(destination)
    if fmt not in SUPPORTED_FORMATS:
        raise ConversionError(f"Unsupported output format: {fmt}")
    if bitrate not in BITRATES:
        raise ConversionError(f"Unsupported bitrate: {bitrate}")
    if not destination.parent.is_dir():
        raise ConversionError(f"Output folder does not exist: {destination.parent}")
    if destination.exists():
        raise ConversionError(f"Output file already exists: {destination.name}")
    if is_cancelled and is_cancelled():
        raise ConversionCancelled()

    try:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise ConversionError(f"FFmpeg is unavailable: {exc}") from exc

    duration = probe_media(source, ffmpeg)
    if is_cancelled and is_cancelled():
        raise ConversionCancelled()

    codec, container = SUPPORTED_FORMATS[fmt]
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{destination.stem}-", suffix=f".{fmt}", dir=destination.parent
    )
    os.close(descriptor)
    temporary = Path(temp_name)
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
        "-nostats", "-progress", "pipe:1", "-y",
        "-i", str(source), "-map", "0:a:0", "-vn",
        "-c:a", codec,
    ]
    if fmt != "wav":
        command.extend(["-b:a", f"{bitrate}k"])
    command.extend(["-f", container, str(temporary)])

    process = None
    try:
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
            )
        except OSError as exc:
            raise ConversionError(f"Cannot start FFmpeg: {exc}") from exc

        if on_process:
            on_process(process)

        errors = []
        assert process.stdout is not None
        for line in process.stdout:
            if is_cancelled and is_cancelled():
                process.terminate()
                break
            row = line.strip()
            if row.startswith("out_time=") and duration and duration > 0:
                elapsed = progress_seconds(row.partition("=")[2])
                if elapsed is not None and on_progress:
                    on_progress(max(0, min(99, int(elapsed / duration * 100))))
            elif row and not row.startswith((
                "bitrate=", "total_size=", "out_time_ms=", "out_time_us=",
                "out_time=", "dup_frames=", "drop_frames=", "speed=",
                "progress=", "stream_",
            )):
                errors.append(row)
        try:
            code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise ConversionError("FFmpeg did not stop in time.")

        if is_cancelled and is_cancelled():
            raise ConversionCancelled()
        if code != 0:
            detail = " | ".join(errors[-4:])[-700:] or f"Exit code {code}"
            raise ConversionError(f"FFmpeg failed: {detail}")

        # An exclusive destination prevents overwriting another output.
        try:
            os.link(temporary, destination)
        except FileExistsError as exc:
            raise ConversionError(f"Output file already exists: {destination.name}") from exc
        except OSError:
            try:
                with temporary.open("rb") as reader, destination.open("xb") as writer:
                    shutil.copyfileobj(reader, writer)
            except Exception:
                destination.unlink(missing_ok=True)
                raise

        if on_progress:
            on_progress(100)
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        if on_process:
            on_process(None)
        temporary.unlink(missing_ok=True)
