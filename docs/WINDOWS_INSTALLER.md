# Windows installer — candidate build 0.2.0

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
2. Checks Python syntax first (including i18n.py and test files), then creates an isolated .venv-build and installs dependencies.
3. Runs automated tests.
4. Uses PyInstaller with onedir + windowed settings to bundle the GUI, icons and FFmpeg. Resource paths are absolute because PyInstaller resolves added data relative to the generated spec file under build/pyinstaller.
5. Checks that application executable, FFmpeg binary and icons exist.
6. Calls Inno Setup and reports the installer's SHA256.

This preview uses version 0.2.0 to distinguish the new pt-BR build from the earlier 0.1.0 test installation. The installer should upgrade an existing 0.1.0 install rather than creating a second application entry.

Generated files:

- Standalone app: dist\Video-to-Audio\Video-to-Audio.exe
- Local preview installer: dist\installer\Video-to-Audio-Setup-0.2.0.exe

If Inno Setup is not installed yet, create only the standalone GUI:

~~~powershell
.\venv\Scripts\python.exe .\build\windows\build.py --app-only
~~~

If it is installed in a nonstandard location:

~~~powershell
.\venv\Scripts\python.exe .\build\windows\build.py --iscc "C:\YourPath\ISCC.exe"
~~~

Do not commit dist, the generated build/pyinstaller directory, .venv-build or converted audio files. Source-controlled build/windows scripts must remain tracked.

## Installer behavior

- Per-user installation in %LOCALAPPDATA%\Programs\Video-to-Audio without administrator privileges.
- Start menu shortcut and an optional desktop shortcut (off by default).
- Windows uninstaller and optional launch at the end.
- No Python or FFmpeg prerequisite on recipient computers.
- Uninstall does not delete videos or converted audio in other folders.

## Acceptance checklist — REQUIRED before publishing

First validate the existing app GUI on PR #1, then on a Windows test system:

- [ ] Build passes tests and creates both files above (31 tests expected with pt-BR localization, post-conversion reset and syntax preflight).
- [ ] The standalone EXE starts by double-click, without a terminal window.
- [ ] Convert one MKV to MP3 without picking a folder and play the audio.
- [ ] After confirming a fully successful conversion, the input list is cleared and the final completion status remains visible.
- [ ] After a failed/cancelled conversion, the input list is retained so the user can retry.
- [ ] On Brazilian Portuguese Windows, the app defaults to Português (Brasil); language selector also supports English and Automatic (Windows).
- [ ] Changing language updates labels, progress, warnings and output location; the manual language choice is kept on a new launch.
- [ ] Installer wizard is available in English and Português Brasileiro; shortcuts, launch option and uninstall work in the chosen installer language.
- [ ] Mixed-source batch saves beside each original and displays correct paths.
- [ ] Shared folder and Use source folders actions work.
- [ ] Cancel conversion and test duplicate filenames on test media.
- [ ] Run installer in a normal Windows user account; verify shortcuts.
- [ ] Run the installed app without a Python install on PATH (ideally clean Windows VM).
- [ ] Convert a short video using the installed app and listen to MP3.
- [ ] Uninstall and confirm application files disappear but source videos/output audio remain.
- [ ] Upgrade the previously installed 0.1.0 preview to 0.2.0 without duplicate product entries (AppId unchanged).
- [ ] Resolve third-party binary redistribution requirements (THIRD_PARTY_NOTICES.md).
- [ ] Review Windows SmartScreen: the preview installer is not code-signed.

Do **not** publish a GitHub Release or tag 1.0.0 before this list is complete.

## Why one-directory bundling?

PyInstaller onedir includes the executable and its runtime dependencies in a folder. Inno Setup packages the folder into one simple installer; this is suitable for a Qt interface requiring bundled FFmpeg resources.

Official references:

- https://pyinstaller.org/en/stable/usage.html
- https://jrsoftware.org/ishelp/index.php?topic=compilercmdline
- https://jrsoftware.org/isdl.php
