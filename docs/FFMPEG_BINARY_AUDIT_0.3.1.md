# Binary provenance and FFmpeg license audit — 0.3.1 Windows preview

**Audit date:** 2026-10-10. **Status:** identity and GPL family identified; **public binary redistribution remains blocked** pending complete corresponding-source and other component compliance.

## Evidence supplied

The Windows operator supplied `Video-to-Audio-auditoria.zip` containing six locally generated audit files: `audit-summary.json`, `ffmpeg-inventory.json`, `ffmpeg-0-version.txt`, `ffmpeg-0-buildconf.txt`, `ffmpeg-0-license.txt`, and `python-dependencies.txt`. No source video, MP3, user directory path or other personal data is included in this documentation.

| Evidence field | Verified value |
| --- | --- |
| Audited source commit | `62af9dd64fc5d68b2536d908cdc6e2668fde2dcc` |
| Installer name | `Video-to-Audio-Setup-0.3.1.exe` |
| Installer SHA-256 | `805c4a82368254edfb2f276df585437268ee75f6c6207bf9b0c35c6a8e80eed7` |
| Packaged application files | 150 |
| Bundled FFmpeg executables | 1 |
| FFmpeg relative path | `_internal/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe` |
| FFmpeg size | 87,638,016 bytes |
| FFmpeg SHA-256 | `2ce797a0f88d7f067180338fb227f7b1928ea727bd9a4d7a1d022f7c52af71a3` |
| FFmpeg build banner | `7.1-essentials_build-www.gyan.dev` |
| Build toolchain | GCC 14.2.0 (MSYS2) |
| Audit collected (UTC) | 2026-10-10T07:12:08.7850831Z |

The checksum and binary fields are **reported by the local audit**, not independently downloaded and rehashed against an official archive.

## Licensing interpretation

The *actual bundled executable* prints:

> ffmpeg is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License ... either version 3 ... or (at your option) any later version.

The configuration contains:

- `--enable-gpl`: GPL-covered FFmpeg code enabled.
- `--enable-version3`: GPLv3 license-family selection.
- `--enable-static`: FFmpeg and enabled libraries were built into the static executable; verify each bundled component's licensing/source obligations.
- `--enable-libx264`, `--enable-libx265`, and `--enable-libxvid`, plus others including `--enable-libmp3lame`, `--enable-libopus`, `--enable-libvorbis`.
- `--enable-nonfree` **does not appear** in the captured configuration.

**Conclusion (narrow):** This specific FFmpeg executable *declares GPLv3-or-later*, not merely LGPL. It is **not flagged** with `--enable-nonfree`; that is favorable but **not an affirmative legal compliance certification**. Gyan.dev's official page also describes its static FFmpeg builds as GPLv3. The choice to make this application GPLv3-based is technically consistent with the binary's declared license, but this alone does not authorize distribution.

**Important distinction:** Running FFmpeg as a separate process is technically different from linking against FFmpeg libraries. Still, bundling and redistributing this GPLv3 FFmpeg executable requires its own compliant license and corresponding-source delivery. No conclusion is claimed about whether any separate-process interaction legally creates one combined work.

## Exact build Python dependencies from local audit

| Package | Version |
| --- | --- |
| PyQt5 | 5.15.11 |
| PyQt5-Qt5 | 5.15.2 |
| PyQt5_sip | 12.20.0 |
| imageio-ffmpeg | 0.6.0 |
| pyinstaller | 6.22.3 |
| pyinstaller-hooks-contrib | 2026.8 |
| altgraph | 0.17.5 |
| packaging | 26.3 |
| pefile | 2024.8.26 |
| pywin32-ctypes | 0.2.3 |
| setuptools | 84.0.0 |

These values describe **the examined build environment** only. The project's declared requirements still contain version ranges; a later build is not automatically identical without locks/source artifact hashes.

## What is still required to distribute

1. **Exact FFmpeg source/provenance:** identify an accessible, source-matching archive/commit for FFmpeg **7.1 Gyan essentials build** and its compilation scripts and patches, plus enabled external libraries and their sources/build configurations where required. A generic FFmpeg homepage, latest release, or different Gyan build is not proof of corresponding source for the exact 87,638,016-byte binary.
2. **FFmpeg licensing package:** include applicable complete license, third-party attribution, actual configure options and precise version, and fulfill GPLv3 corresponding-source distribution or network-access obligations, including source of statically linked GPL-covered components. GPLv3-only text is now in `LICENSES` but does **not** replace corresponding source.
3. **PyQt5 / Qt distribution:** the installed versions are identified, but a file-by-file library/module/Qt plugin inventory and associated GPL/LGPL texts, copyright, source/relinking provisions as applicable remain unverified. Riverbank confirms GPLv3 PyQt and LGPL-licensed Qt in GPL PyQt wheels.
4. **App's legal presentation:** installer currently presents the original Apache-2.0 license page and unofficial Portuguese translation. Before public distribution, clarify the distinct upstream Apache-2.0 license, GPLv3 licensing of the combined distributed application and copyrightable new contributions, FFmpeg notice, source-access URL and no-warranty notices.
5. **Final release build:** reproduce and audit the final redistributable, record the final commit/manifest/hash, run manual QA and provide exact corresponding source at least as accessible as the installer. Do not claim hosted GitHub Actions success while runs are blocked.
6. **Dependency provenance:** compare the FFmpeg binary SHA-256 with a genuine package/download source if possible, rather than trusting a filename and version banner alone.

## Decision / release gate

- FFmpeg identity: **CONFIRMED by local evidence**.
- GPLv3 family: **CONFIRMED by `-L` output**.
- Nonfree flag: **NOT PRESENT in output**, not a complete proof of redistribution eligibility.
- Exact source and dependency compliance: **NOT VERIFIED**.
- Binary publication: **HOLD**. Continue preparing free/open-source GPLv3 release without paid GitHub Actions, but do not publish this installer yet.

## Primary references

- [FFmpeg licensing and legal considerations](https://ffmpeg.org/legal.html)
- [Official Gyan.dev Windows FFmpeg builds — static builds described as GPLv3](https://www.gyan.dev/ffmpeg/builds/)
- [GNU GPLv3 corresponding source (section 6)](https://www.gnu.org/licenses/gpl-3.0.html)
- [GNU FAQ — equivalent network access to corresponding source](https://www.gnu.org/licenses/gpl-faq.en.html)
- [Riverbank PyQt GPL/commercial terms](https://en.riverbankcomputing.com/software/pyqt)
- [Qt open-source license obligations](https://www.qt.io/development/open-source-lgpl-obligations)

This is an engineering audit and not legal advice.
