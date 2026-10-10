"""Desktop UI for the Video to Audio Converter.

Run with python.exe for debugging or pythonw.exe for a console-free shortcut.
"""

from __future__ import annotations

import sys
from pathlib import Path
from threading import Event, Lock

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QLabel, QListWidget,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget,
)

from converter import (
    VIDEO_EXTENSIONS, ConversionCancelled, ConversionError,
    available_output_path, convert_video, destination_folder,
)

ROOT = Path(__file__).resolve().parent


def icon(name: str) -> QIcon:
    return QIcon(str(ROOT / "icons" / name))


class ConvertThread(QThread):
    progress_signal = pyqtSignal(int, int, str)
    error_signal = pyqtSignal(str)
    result_signal = pyqtSignal(int, object, bool)

    def __init__(self, paths: list[Path], fmt: str, output_dir: Path | None, bitrate: int):
        super().__init__()
        self.paths = paths
        self.fmt = fmt
        self.output_dir = output_dir
        self.bitrate = bitrate
        self._cancelled = Event()
        self._lock = Lock()
        self._process = None

    def _set_process(self, process):
        with self._lock:
            self._process = process
            if process is not None and self._cancelled.is_set() and process.poll() is None:
                process.terminate()

    def cancel(self):
        self._cancelled.set()
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                self._process.terminate()

    def run(self):
        completed = 0
        errors = []
        reserved_by_folder: dict[str, set[str]] = {}
        total = len(self.paths)

        for index, path in enumerate(self.paths):
            if self._cancelled.is_set():
                break
            try:
                folder = destination_folder(path, self.output_dir)
                reserved = reserved_by_folder.setdefault(str(folder).casefold(), set())
                destination = available_output_path(path, folder, self.fmt, reserved)

                def report(percent, i=index, name=path.name):
                    overall = min(100, int(100 * (i + percent / 100) / total))
                    self.progress_signal.emit(overall, percent, name)

                self.progress_signal.emit(int(index / total * 100), 0, path.name)
                convert_video(
                    path, destination, self.fmt, self.bitrate,
                    on_progress=report,
                    is_cancelled=self._cancelled.is_set,
                    on_process=self._set_process,
                )
                completed += 1
            except ConversionCancelled:
                break
            except (ConversionError, OSError, ValueError) as exc:
                message = f"{path.name}: {exc}"
                errors.append(message)
                self.error_signal.emit(message)
            except Exception as exc:
                message = f"{path.name}: Unexpected error: {exc}"
                errors.append(message)
                self.error_signal.emit(message)
            finally:
                overall = int((index + 1) / total * 100)
                if not self._cancelled.is_set():
                    self.progress_signal.emit(overall, 100, path.name)

        self.result_signal.emit(completed, errors, self._cancelled.is_set())


class VideoToAudioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video to Audio Converter")
        self.setWindowIcon(icon("Video to Audio.png"))
        self.resize(650, 530)
        self.video_paths: list[Path] = []
        self.output_dir: Path | None = None
        self.worker: ConvertThread | None = None
        self._close_when_finished = False
        self._build_ui()

    def _build_ui(self):
        content = QWidget(self)
        layout = QVBoxLayout(content)

        layout.addWidget(QLabel("Videos to convert"))
        self.video_list = QListWidget(self)
        self.video_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.video_list)

        file_controls = QHBoxLayout()
        self.select_btn = QPushButton("Select Videos", self)
        self.select_btn.setIcon(icon("add.png"))
        self.select_btn.clicked.connect(self.open_file_dialog)
        file_controls.addWidget(self.select_btn)
        self.remove_btn = QPushButton("Remove Selected", self)
        self.remove_btn.clicked.connect(self.remove_selected)
        file_controls.addWidget(self.remove_btn)
        self.clear_btn = QPushButton("Clear List", self)
        self.clear_btn.setIcon(icon("clear.png"))
        self.clear_btn.clicked.connect(self.clear_video_list)
        file_controls.addWidget(self.clear_btn)
        layout.addLayout(file_controls)

        settings = QHBoxLayout()
        settings.addWidget(QLabel("Output Format:"))
        self.format_combo = QComboBox(self)
        self.format_combo.addItems(["mp3", "wav", "aac"])
        self.format_combo.currentTextChanged.connect(self._update_bitrate)
        settings.addWidget(self.format_combo)
        settings.addWidget(QLabel("Bitrate:"))
        self.bitrate_combo = QComboBox(self)
        self.bitrate_combo.addItems(["64", "128", "192", "256", "320"])
        self.bitrate_combo.setCurrentText("128")
        settings.addWidget(self.bitrate_combo)
        layout.addLayout(settings)
        self._update_bitrate()

        location_actions = QHBoxLayout()
        self.output_btn = QPushButton("Choose output folder (optional)", self)
        self.output_btn.setIcon(icon("folder.png"))
        self.output_btn.clicked.connect(self.select_output_folder)
        location_actions.addWidget(self.output_btn)

        self.original_btn = QPushButton("Use source folders", self)
        self.original_btn.clicked.connect(self.use_original_folders)
        location_actions.addWidget(self.original_btn)
        layout.addLayout(location_actions)

        self.output_label = QLabel(self)
        self.output_label.setWordWrap(True)
        self.output_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.output_label)

        self.output_hint = QLabel(
            "Videos are in different folders. To keep all audio together, "
            "you can choose one output folder. This is optional.", self
        )
        self.output_hint.setWordWrap(True)
        layout.addWidget(self.output_hint)
        self._update_output_location()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Ready to convert", self)
        self.progress_label.setWordWrap(True)
        layout.addWidget(self.progress_label)

        actions = QHBoxLayout()
        self.convert_btn = QPushButton("Convert", self)
        self.convert_btn.setIcon(icon("convert.png"))
        self.convert_btn.clicked.connect(self.start_conversion)
        actions.addWidget(self.convert_btn)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        actions.addWidget(self.cancel_btn)
        layout.addLayout(actions)

        self.setCentralWidget(content)

    def _update_bitrate(self, _value=None):
        enabled = self.format_combo.currentText() != "wav"
        self.bitrate_combo.setEnabled(enabled)
        self.bitrate_combo.setToolTip(
            "" if enabled else "WAV uses uncompressed PCM audio; bitrate does not apply."
        )

    def add_files(self, files):
        seen = {str(path).casefold() for path in self.video_paths}
        for name in files:
            path = Path(name).resolve()
            key = str(path).casefold()
            if path.suffix.lower() not in VIDEO_EXTENSIONS or not path.is_file() or key in seen:
                continue
            self.video_paths.append(path)
            self.video_list.addItem(path.name)
            self.video_list.item(self.video_list.count() - 1).setToolTip(str(path))
            seen.add(key)
        self._update_output_location()

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.webm *.m4v)",
        )
        self.add_files(files)

    def remove_selected(self):
        for row in sorted((self.video_list.row(item) for item in self.video_list.selectedItems()), reverse=True):
            self.video_list.takeItem(row)
            del self.video_paths[row]
        if not self.video_paths:
            self.output_dir = None
        self._update_output_location()

    def clear_video_list(self):
        self.video_paths.clear()
        self.video_list.clear()
        self.output_dir = None
        self._update_output_location()

    def select_output_folder(self):
        initial = self.output_dir or (
            self.video_paths[0].parent if self.video_paths else Path.home()
        )
        directory = QFileDialog.getExistingDirectory(
            self, "Choose a common audio output folder (optional)", str(initial)
        )
        if directory:
            self.output_dir = Path(directory)
            self._update_output_location()

    def use_original_folders(self):
        self.output_dir = None
        self._update_output_location()

    def _update_output_location(self):
        """Keep the actual save destination visible before conversion."""
        folders = list(dict.fromkeys(str(path.parent) for path in self.video_paths))
        if self.output_dir is not None:
            self.output_label.setText(f"Save audio to: {self.output_dir} (chosen folder)")
            self.output_label.setToolTip(str(self.output_dir))
        elif not folders:
            self.output_label.setText(
                "Save audio to: Each video's original folder (automatic)"
            )
            self.output_label.setToolTip("")
        elif len(folders) == 1:
            self.output_label.setText(
                f"Save audio to: {folders[0]} (same folder as the videos)"
            )
            self.output_label.setToolTip(folders[0])
        else:
            visible = "\n".join(f"• {folder}" for folder in folders[:3])
            remaining = len(folders) - 3
            if remaining > 0:
                visible += f"\n... and {remaining} more (hover to see all)"
            self.output_label.setText(
                f"Save audio to: Original folders ({len(folders)} locations)\n{visible}"
            )
            self.output_label.setToolTip("\n".join(folders))

        self.output_hint.setVisible(self.output_dir is None and len(folders) > 1)
        self.original_btn.setEnabled(self.output_dir is not None)
        for index, path in enumerate(self.video_paths):
            self.video_list.item(index).setToolTip(
                f"Source: {path}\nSave audio to: {destination_folder(path, self.output_dir)}"
            )

    def _set_busy(self, busy):
        for control in (
            self.select_btn, self.remove_btn, self.clear_btn, self.format_combo,
            self.output_btn, self.original_btn, self.convert_btn, self.video_list,
        ):
            control.setEnabled(not busy)
        if not busy:
            self._update_bitrate()
        else:
            self.bitrate_combo.setEnabled(False)
        self.cancel_btn.setEnabled(busy)

    def start_conversion(self):
        if self.worker is not None:
            return
        if not self.video_paths:
            QMessageBox.warning(self, "Missing selection", "Select at least one video.")
            return
        if self.output_dir is not None and not self.output_dir.is_dir():
            QMessageBox.warning(self, "Missing folder", "The output folder no longer exists.")
            return

        self.worker = ConvertThread(
            list(self.video_paths), self.format_combo.currentText(),
            self.output_dir, int(self.bitrate_combo.currentText()),
        )
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.result_signal.connect(self._on_result)
        self.worker.finished.connect(self._on_thread_finished)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting conversion...")
        self._set_busy(True)
        self.worker.start()

    def _on_progress(self, overall, current, name):
        self.progress_bar.setValue(overall)
        self.progress_label.setText(f"{name}: {current}% (batch: {overall}%)")

    def cancel_conversion(self):
        if self.worker is not None:
            self.worker.cancel()
            self.cancel_btn.setEnabled(False)
            self.progress_label.setText("Cancelling conversion...")

    def _on_result(self, completed, errors, cancelled):
        if self._close_when_finished:
            return
        if cancelled:
            self.progress_label.setText(f"Cancelled. {completed} file(s) completed.")
            QMessageBox.information(self, "Cancelled", self.progress_label.text())
        elif errors:
            self.progress_label.setText(f"Finished: {completed} succeeded, {len(errors)} failed.")
            details = "\n".join(errors[:10])
            if len(errors) > 10:
                details += f"\n...and {len(errors) - 10} more."
            QMessageBox.warning(self, "Conversion results", self.progress_label.text() + "\n\n" + details)
        else:
            self.progress_bar.setValue(100)
            self.progress_label.setText(f"Complete: {completed} file(s) converted.")
            QMessageBox.information(self, "Complete", self.progress_label.text())

    def _on_thread_finished(self):
        self.worker = None
        self._set_busy(False)
        if self._close_when_finished:
            self.close()

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self._close_when_finished = True
            self.cancel_conversion()
            event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    window = VideoToAudioApp()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
