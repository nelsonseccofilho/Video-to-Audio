# Windows installer — candidate build 0.1.0

This is a **local preview build**, not a validated or published release.

## Prerequisites

- Windows 10/11 x64 and Python 3.12.
- [Inno Setup 6](https://jrsoftware.org/isdl.php) to generate the installer.
- Checkout of feature branch feat/windows-installer. Inspect build scripts before executing them.

The build uses its own **.venv-build** and does not modify system Python, the runtime venv or WhisperX. PowerShell script execution policy does not need changing.

## Build a testable installer

Open Windows PowerShell in the repository directory:

~~~powershell
cd D:\git\Video-to-Audio
.\venv\Scripts\python.exe .\build\windows\build.py
~~~

The script:

1. Finds Inno Setup's ISCC.exe.
2. Creates an isolated .venv-build and installs dependencies.
3. Runs automated tests.
4. Uses PyInstaller with onedir + windowed settings to bundle the GUI, icons and FFmpeg.
5. Checks that application executable, FFmpeg binary and icons exist.
6. Calls Inno Setup and reports the installer's SHA256.

Generated files:

- Standalone app: dist\Video-to-Audio\Video-to-Audio.exe
- Local preview installer: dist\installer\Video-to-Audio-Setup-0.1.0.exe

If Inno Setup is not installed yet, create only the standalone GUI:

~~~powershell
.\venv\Scripts\python.exe .\build\windows\build.py --app-only
~~~

If it is installed in a nonstandard location:

~~~powershell
.\venv\Scripts\python.exe .\build\windows\build.py --iscc "C:\YourPath\ISCC.exe"
~~~

Do not commit dist, build, .venv-build or converted audio files.

## Installer behavior

- Per-user installation in %LOCALAPPDATA%\Programs\Video-to-Audio without administrator privileges.
- Start menu shortcut and an optional desktop shortcut (off by default).
- Windows uninstaller and optional launch at the end.
- No Python or FFmpeg prerequisite on recipient computers.
- Uninstall does not delete videos or converted audio in other folders.

## Acceptance checklist — REQUIRED before publishing

First validate the existing app GUI on PR #1, then on a Windows test system:

- [ ] Build passes tests and creates both files above.
- [ ] The standalone EXE starts by double-click, without a terminal window.
- [ ] Convert one MKV to MP3 without picking a folder and play the audio.
- [ ] Mixed-source batch saves beside each original and displays correct paths.
- [ ] Shared folder and Use source folders actions work.
- [ ] Cancel conversion and test duplicate filenames on test media.
- [ ] Run installer in a normal Windows user account; verify shortcuts.
- [ ] Run the installed app without a Python install on PATH (ideally clean Windows VM).
- [ ] Convert a short video using the installed app and listen to MP3.
- [ ] Uninstall and confirm application files disappear but source videos/output audio remain.
- [ ] Reinstall or upgrade without duplicate product entries.
- [ ] Resolve third-party binary redistribution requirements (THIRD_PARTY_NOTICES.md).
- [ ] Review Windows SmartScreen: the preview installer is not code-signed.

Do **not** publish a GitHub Release or tag 1.0.0 before this list is complete.

## Why one-directory bundling?

PyInstaller onedir includes the executable and its runtime dependencies in a folder. Inno Setup packages the folder into one simple installer; this is suitable for a Qt interface requiring bundled FFmpeg resources.

Official references:

- https://pyinstaller.org/en/stable/usage.html
- https://jrsoftware.org/ishelp/index.php?topic=compilercmdline
- https://jrsoftware.org/isdl.php
