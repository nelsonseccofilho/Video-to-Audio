"""Desktop UI for the Video to Audio Converter.

Run with python.exe for debugging or pythonw.exe for a console-free shortcut.
"""

from __future__ import annotations

import sys
from pathlib import Path
from threading import Event, Lock

from PyQt5.QtCore import QLibraryInfo, QSettings, QThread, QTranslator, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QLabel, QListWidget,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget,
)

from converter import (
    VIDEO_EXTENSIONS, ConversionCancelled, ConversionError,
    available_output_path, convert_video, destination_folder,
)
from i18n import SUPPORTED_CHOICES, effective_language, translate, translate_failure

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
        self.resize(650, 560)
        self.settings = QSettings("Video-to-Audio", "Video-to-Audio")
        self.language_choice = str(self.settings.value("ui/language", "en"))
        if self.language_choice not in SUPPORTED_CHOICES:
            self.language_choice = "auto"
        self.language = effective_language(self.language_choice)
        self._status_key = "ready"
        self._status_values = {}
        self.video_paths: list[Path] = []
        self.output_dir: Path | None = None
        self.worker: ConvertThread | None = None
        self._close_when_finished = False
        self._qt_translator = QTranslator(self)
        self._build_ui()
        self._apply_language()

    def _build_ui(self):
        content = QWidget(self)
        layout = QVBoxLayout(content)

        locale_row = QHBoxLayout()
        locale_row.addStretch()
        self.language_label = QLabel(self)
        locale_row.addWidget(self.language_label)
        self.language_combo = QComboBox(self)
        # List language names alphabetically; launch in English by default.
        self.language_combo.addItem("", "en")
        self.language_combo.addItem("", "pt_BR")
        self.language_combo.setCurrentIndex(
            self.language_combo.findData(self.language_choice)
        )
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        locale_row.addWidget(self.language_combo)
        layout.addLayout(locale_row)

        self.videos_label = QLabel(self)
        layout.addWidget(self.videos_label)
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
        self.format_label = QLabel(self)
        settings.addWidget(self.format_label)
        self.format_combo = QComboBox(self)
        self.format_combo.addItems(["mp3", "wav", "aac"])
        self.format_combo.currentTextChanged.connect(self._update_bitrate)
        settings.addWidget(self.format_combo)
        self.bitrate_label = QLabel(self)
        settings.addWidget(self.bitrate_label)
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

        self.output_hint = QLabel(self)
        self.output_hint.setWordWrap(True)
        layout.addWidget(self.output_hint)
        self._update_output_location()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        self.progress_label = QLabel(self)
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

    def _t(self, key: str, **values) -> str:
        return translate(self.language, key, **values)

    def _set_status(self, key: str, **values):
        self._status_key = key
        self._status_values = values
        self.progress_label.setText(self._t(key, **values))

    def _on_language_changed(self, _index):
        self.language_choice = str(self.language_combo.currentData())
        self.settings.setValue("ui/language", self.language_choice)
        self._apply_language()

    def set_language(self, choice: str, *, persist: bool = False):
        """Change locale without persisting in tests, or save a user selection."""
        if choice not in SUPPORTED_CHOICES:
            raise ValueError(f"Unsupported language choice: {choice}")
        self.language_choice = choice
        if persist:
            self.settings.setValue("ui/language", choice)
        index = self.language_combo.findData(choice)
        was_blocked = self.language_combo.blockSignals(True)
        self.language_combo.setCurrentIndex(index)
        self.language_combo.blockSignals(was_blocked)
        self._apply_language()

    def _load_qt_translation(self):
        """Translate Qt-managed dialog controls where language packs are available."""
        app = QApplication.instance()
        if app is None:
            return
        app.removeTranslator(self._qt_translator)
        self._qt_translator = QTranslator(self)
        if self.language == "en":
            return
        translations = Path(QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        for name in ("qtbase_pt_BR", "qtbase_pt", "qt_pt_BR", "qt_pt"):
            if self._qt_translator.load(name, str(translations)):
                app.installTranslator(self._qt_translator)
                break

    def _apply_language(self):
        self.language = effective_language(self.language_choice)
        self.setWindowTitle(self._t("window_title"))
        self.language_label.setText(self._t("language_label"))
        self._load_qt_translation()
        for choice, key in (
            ("en", "language_en"),
            ("pt_BR", "language_pt"),
        ):
            self.language_combo.setItemText(
                self.language_combo.findData(choice), self._t(key)
            )
        self.videos_label.setText(self._t("videos_label"))
        self.select_btn.setText(self._t("select_videos"))
        self.remove_btn.setText(self._t("remove_selected"))
        self.clear_btn.setText(self._t("clear_list"))
        self.format_label.setText(self._t("output_format"))
        self.bitrate_label.setText(self._t("bitrate"))
        self.output_btn.setText(self._t("choose_folder"))
        self.original_btn.setText(self._t("source_folders"))
        self.output_hint.setText(self._t("mixed_folders_hint"))
        self.convert_btn.setText(self._t("convert"))
        self.cancel_btn.setText(self._t("cancel"))
        self._update_bitrate()
        self._update_output_location()
        self.progress_label.setText(
            self._t(self._status_key, **self._status_values)
        )

    def _update_bitrate(self, _value=None):
        enabled = self.format_combo.currentText() != "wav"
        self.bitrate_combo.setEnabled(enabled)
        self.bitrate_combo.setToolTip(
            "" if enabled else self._t("wav_tooltip")
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
            self, self._t("video_dialog"), "", self._t("video_filter"),
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
            self, self._t("folder_dialog"), str(initial)
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
            self.output_label.setText(
                self._t("destination_custom", folder=self.output_dir)
            )
            self.output_label.setToolTip(str(self.output_dir))
        elif not folders:
            self.output_label.setText(self._t("destination_none"))
            self.output_label.setToolTip("")
        elif len(folders) == 1:
            self.output_label.setText(
                self._t("destination_single", folder=folders[0])
            )
            self.output_label.setToolTip(folders[0])
        else:
            visible = "\n".join(f"• {folder}" for folder in folders[:3])
            remaining = len(folders) - 3
            if remaining > 0:
                visible += "\n" + self._t("destination_more", count=remaining)
            self.output_label.setText(
                self._t("destination_multiple", count=len(folders), folders=visible)
            )
            self.output_label.setToolTip("\n".join(folders))

        self.output_hint.setVisible(self.output_dir is None and len(folders) > 1)
        self.original_btn.setEnabled(self.output_dir is not None)
        for index, path in enumerate(self.video_paths):
            self.video_list.item(index).setToolTip(
                self._t(
                    "destination_tooltip", source=path,
                    folder=destination_folder(path, self.output_dir),
                )
            )

    def _set_busy(self, busy):
        for control in (
            self.select_btn, self.remove_btn, self.clear_btn, self.format_combo,
            self.output_btn, self.original_btn, self.convert_btn, self.video_list,
            self.language_combo,
        ):
            control.setEnabled(not busy)
        if not busy:
            self._update_bitrate()
        else:
            self.bitrate_combo.setEnabled(False)
        self.cancel_btn.setEnabled(busy)
        self.original_btn.setEnabled(not busy and self.output_dir is not None)

    def start_conversion(self):
        if self.worker is not None:
            return
        if not self.video_paths:
            QMessageBox.warning(
                self, self._t("missing_selection_title"), self._t("missing_selection")
            )
            return
        if self.output_dir is not None and not self.output_dir.is_dir():
            QMessageBox.warning(
                self, self._t("missing_folder_title"), self._t("missing_folder")
            )
            return

        self.worker = ConvertThread(
            list(self.video_paths), self.format_combo.currentText(),
            self.output_dir, int(self.bitrate_combo.currentText()),
        )
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.result_signal.connect(self._on_result)
        self.worker.finished.connect(self._on_thread_finished)
        self.progress_bar.setValue(0)
        self._set_status("starting")
        self._set_busy(True)
        self.worker.start()

    def _on_progress(self, overall, current, name):
        self.progress_bar.setValue(overall)
        self._set_status("progress", name=name, current=current, overall=overall)

    def cancel_conversion(self):
        if self.worker is not None:
            self.worker.cancel()
            self.cancel_btn.setEnabled(False)
            self._set_status("cancelling")

    def _on_result(self, completed, errors, cancelled):
        if self._close_when_finished:
            return
        if cancelled:
            self._set_status("cancelled", completed=completed)
            QMessageBox.information(
                self, self._t("cancelled_title"), self.progress_label.text()
            )
        elif errors:
            self._set_status("partial", completed=completed, failed=len(errors))
            details = "\n".join(
                self._localized_error(error) for error in errors[:10]
            )
            if len(errors) > 10:
                details += "\n" + self._t(
                    "more_errors", count=len(errors) - 10
                )
            QMessageBox.warning(
                self, self._t("results_title"),
                self.progress_label.text() + "\n\n" + details,
            )
        else:
            self.progress_bar.setValue(100)
            self._set_status("complete", completed=completed)
            QMessageBox.information(
                self, self._t("complete_title"), self.progress_label.text()
            )
            # A new batch starts with an empty list. Keep the 100% progress
            # and completion status as confirmation of the finished operation.
            self.clear_video_list()

    def _localized_error(self, error: str) -> str:
        filename, separator, reason = error.partition(": ")
        if not separator:
            return translate_failure(self.language, error)
        return filename + separator + translate_failure(self.language, reason)

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
