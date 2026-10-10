# Video to Audio Converter

A desktop video-to-audio converter for Windows, based on [NSTechBytes/Video-to-Audio](https://github.com/NSTechBytes/Video-to-Audio). This fork fixes console-free launching, progress reporting, batch error handling and installation instructions.

## Features

- Extract MP3, WAV or AAC from MP4, MKV, MOV, AVI, WEBM and M4V files.
- Convert batches, with an individual error report for files without audio.
- Show real FFmpeg progress (no simulated timer), and cancel an active conversion.
- Preserve existing outputs by automatically choosing a unique name when needed.
- Keep the interface responsive with a background worker.
- Launch from the Windows Start menu using pythonw.exe without opening a terminal.
- Use a private Python virtual environment; no changes to system Python or WhisperX.

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

1. Select one or more videos.
2. Choose MP3, WAV or AAC, and bitrate (64–320 kbps) for MP3/AAC.
3. Select a destination folder and press **Convert**.
4. Follow the actual conversion and batch progress. Press **Cancel** to stop.
5. Existing output files are never intentionally replaced; a numbered filename is chosen when necessary.

WAV uses uncompressed 16-bit PCM and ignores the bitrate option. A raw AAC output is an ADTS audio file. An input without an audio stream is reported as a failed file, and remaining files continue processing. If a media file does not report its duration, per-file progress may stay at its starting value until conversion completes.

On cancellation or an FFmpeg error, the current temporary output is deleted. Already completed audio files are kept.

## Troubleshooting

- **Cannot import PyQt5 or imageio_ffmpeg:** ensure the application and installation commands use the venv's Python executable.
- **No audio stream found:** confirm that the video actually has an audio track.
- **Errors converting one file:** try another input. The interface reports the FFmpeg message for that file.
- **Desktop shortcut does not launch:** verify TargetPath, Arguments and WorkingDirectory, then run the terminal command above.
- **PowerShell blocks Activate.ps1:** activation is unnecessary; use the venv Python executable instead.

## Tests

~~~powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

Tests include FFmpeg extraction to all three formats, filename conflicts, audio-less input, cancellation-before-start and headless GUI initialization. GitHub Actions tests on Windows with Python 3.12.

## Credits and license

Originally created by **Nasir Shahbaz** for [NSTechBytes](https://github.com/NSTechBytes). This repository includes additional maintenance and reliability improvements.

The repository's [LICENSE](LICENSE) is **Apache License 2.0** (the upstream README incorrectly called it MIT). Original icon assets and attribution are preserved.
