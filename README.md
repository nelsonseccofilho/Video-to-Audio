# Video to Audio Converter

A desktop video-to-audio converter for Windows, based on [NSTechBytes/Video-to-Audio](https://github.com/NSTechBytes/Video-to-Audio). This fork fixes console-free launching, progress reporting, batch error handling and installation instructions.

## Features

- Extract MP3, WAV or AAC from MP4, MKV, MOV, AVI, WEBM and M4V files.
- Convert batches, with an individual error report for files without audio.
- Show real FFmpeg progress (no simulated timer), and cancel an active conversion.
- Preserve existing outputs by automatically choosing a unique name when needed.
- Save audio beside each video by default, including batches from different folders.
- Optionally choose a shared output folder; the interface always shows the active location.
- Keep the interface responsive with a background worker.
- Launch from the Windows Start menu using pythonw.exe without opening a terminal.
- Use a private Python virtual environment; no changes to system Python or WhisperX.
- Choose **English** (default) or **Português (Brasil)**; switching updates the interface immediately and saves the preference.
- Clear the input list automatically after a fully successful conversion; keep it on errors or cancellation.

## Windows / PowerShell installation

Requires Python 3.12 (the version covered by CI) and Git. Run each command separately:

~~~powershell
git clone https://github.com/nelsonseccofilho/Video-to-Audio.git
cd Video-to-Audio
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe ".\Video to Audio.py"
~~~

**No environment activation or execution-policy change is necessary.** The program uses the bundled FFmpeg binary provided by imageio-ffmpeg.

### Existing upstream clone

If you previously cloned NSTechBytes/Video-to-Audio into D:\git\Video-to-Audio and already created its virtual environment, keep that folder and use:

~~~powershell
cd D:\git\Video-to-Audio
git remote set-url origin https://github.com/nelsonseccofilho/Video-to-Audio.git
git pull --ff-only origin main
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe ".\Video to Audio.py"
~~~

These commands update **only this repository and its own venv**. They do not change the WhisperX installation.

### Start menu shortcut (no terminal window)

Run the following in PowerShell after installing into D:\git\Video-to-Audio:

~~~powershell
$dir = "D:\git\Video-to-Audio"
$shell = New-Object -ComObject WScript.Shell
$programs = [Environment]::GetFolderPath("Programs")
$link = $shell.CreateShortcut("$programs\Video-to-Audio.lnk")
$link.TargetPath = "$dir\venv\Scripts\pythonw.exe"
$link.Arguments = ('"{0}"' -f "$dir\Video to Audio.py")
$link.WorkingDirectory = $dir
$link.IconLocation = "$dir\icons\icon.ico"
$link.Save()
~~~

You can now search for **Video-to-Audio** from Start and pin it. If you have already created a shortcut pointing to this same folder/script, it continues to work after updating. For troubleshooting use python.exe instead of pythonw.exe to see errors in the terminal.

## Usage

1. Select one or more videos. By default, audio is saved **in the same folder as its source video**.
2. For videos from different folders, the interface displays each source folder and optionally suggests a single common destination. No dialog or manual folder selection is required.
3. If you want all audio together, choose **Choose output folder (optional)**. To return to automatic per-video destinations, choose **Use source folders**.
4. Check the **Save audio to** text before converting. For many folders, hover over that text or over each video for the full location.
5. Choose MP3, WAV or AAC, and bitrate (64–320 kbps) for MP3/AAC, then press **Convert**.
6. Follow real conversion and batch progress. Press **Cancel** to stop.
7. Existing output files are never intentionally replaced; a numbered filename is chosen when necessary.

After all files convert successfully, select **OK** on the completion dialog: the input list and any manually selected output folder are cleared for the next batch. The progress bar and completion message stay visible as confirmation. If a batch fails or is cancelled, the list remains available to retry.

The **Language / Idioma** selector lists two options alphabetically: English (the default) and Português (Brasil). Changing the selection retranslates the application immediately, including its buttons, status, paths, messages and tooltips, and saves the preference. The Windows installer separately supports English by default and Brazilian Portuguese. Its Brazilian Portuguese license screen includes a summary followed by the authoritative original English Apache-2.0 license; this is an informational aid, not an official legal translation.

WAV uses uncompressed 16-bit PCM and ignores the bitrate option. A raw AAC output is an ADTS audio file. An input without an audio stream is reported as a failed file, and remaining files continue processing. If a media file does not report its duration, per-file progress may stay at its starting value until conversion completes.

On cancellation or an FFmpeg error, the current temporary output is deleted. Already completed audio files are kept.

Selecting a destination folder is optional. Cancelling the folder picker leaves the previous destination unchanged. Clearing the video list resets the custom folder selection so a new batch does not silently reuse an old destination.

The output-folder experience follows the Nielsen Norman Group's principles of system-status visibility, user control and freedom, error prevention, and recognition over recall. See [Output-location UX decisions](docs/OUTPUT_LOCATION_UX.md) for the scenario matrix and references.

## Troubleshooting

- **Cannot import PyQt5 or imageio_ffmpeg:** ensure the application and installation commands use the venv's Python executable.
- **No audio stream found:** confirm that the video actually has an audio track.
- **Errors converting one file:** try another input. The interface reports the FFmpeg message for that file.
- **Desktop shortcut does not launch:** verify TargetPath, Arguments and WorkingDirectory, then run the terminal command above.
- **PowerShell blocks Activate.ps1:** activation is unnecessary; use the venv Python executable instead.

## Windows installer — preview

The preview installer is developed separately on branch **feat/windows-installer**. The English-first bilingual build with a complete pt-BR informational license translation is **0.3.1** (not an official public release).
See the [installer build guide](docs/WINDOWS_INSTALLER.md) for a locally built executable and Setup.exe.

When the branch is checked out, you can run the build on Windows with Python 3.12 and Inno Setup 6:

~~~powershell
.\venv\Scripts\python.exe .\build\windows\build.py
~~~

The script builds in its own .venv-build and **does not affect WhisperX**. It creates a testable standalone GUI and a versioned installer. This is **not yet an official release**: manual Windows installer testing and [third-party redistribution review](docs/THIRD_PARTY_NOTICES.md) are required. The PyQt5 library has GPLv3/commercial licensing and the bundled FFmpeg's license depends on its exact build configuration.

## Tests

~~~powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

Tests include FFmpeg extraction to all three formats, filename conflicts, audio-less input, cancellation-before-start, automatic output folders and headless GUI initialization. GitHub Actions is configured for Windows and Linux with Python 3.12; check the PR for the latest CI execution status.

## Credits and license

Originally created by **Nasir Shahbaz** for [NSTechBytes](https://github.com/NSTechBytes). This repository includes additional maintenance and reliability improvements.

The repository's [LICENSE](LICENSE) is **Apache License 2.0** (the upstream README incorrectly called it MIT). Original icon assets and attribution are preserved.
