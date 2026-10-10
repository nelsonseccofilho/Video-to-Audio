# Third-party components — preview build audit

This file documents components included in the Windows app and matters that **must be checked before publicly distributing installer binaries**. It is not a substitute for their complete license texts or a legal review.

| Component | Role | License / issue | Source |
| --- | --- | --- | --- |
| Video-to-Audio source and original icons | Project and UI | Apache License 2.0 as supplied in repository; retain original author attribution | [Original project](https://github.com/NSTechBytes/Video-to-Audio) |
| PyQt5 | Python Qt GUI binding | **GPL v3 or Riverbank commercial. Not LGPL.** Check GPLv3 distribution requirements for the combined packaged app; a commercial license is the alternative. | [Riverbank licensing](https://en.riverbankcomputing.com/software/pyqt) |
| Qt5 shared with PyQt wheels | UI toolkit | Qt modules have their own LGPL/GPL terms; confirm shipped libraries and notices. | [Qt licensing](https://doc.qt.io/qt-5/licensing.html) |
| imageio-ffmpeg | Python FFmpeg loader | BSD-2-Clause wrapper, including binary redistribution notice requirements. | [Package license](https://github.com/imageio/imageio-ffmpeg/blob/main/LICENSE) |
| FFmpeg executable supplied by imageio-ffmpeg | Video/audio conversion | **LGPL or GPL depending on exact FFmpeg build configuration and included codecs.** Verify binary version/configuration and corresponding license/source before public redistribution. | [FFmpeg license](https://ffmpeg.org/legal.html) |
| PyInstaller | Packaging-time tool | License and bundled bootloader notices must be respected. | [PyInstaller](https://pyinstaller.org/en/stable/license.html) |

## Chosen open-source route (in preparation)

The project owner intends to distribute the **combined desktop application under GPLv3 terms**, without charge, using the GPLv3 edition of PyQt5. The original upstream Apache-2.0 code retains its own license and attribution. See [open-source distribution policy](OPEN_SOURCE_DISTRIBUTION_POLICY.md).

Full license texts already staged for the preview include:
- Apache-2.0, still in the repository root **LICENSE**.
- GPLv3, in **LICENSES/GPL-3.0-only.txt**.
- imageio-ffmpeg's BSD-2-Clause notice, in **LICENSES/BSD-2-Clause-imageio-ffmpeg.txt**.

**This is not a complete binary-license package.** We still need the actual shipped Qt module terms/notices/source provisions, FFmpeg's *precise* build/license/source, the app's GPL notice/source access, and review of the installer license-selection page, which currently presents Apache-2.0 only. The presence of a GPL text does not certify compliance.

To collect evidence against the exact binary locally, run **scripts/audit_windows_distribution.ps1** after building. It writes ignored data to **dist/audit/**; inspect logs for private paths before sharing.

## Confirmed bundled FFmpeg from 0.3.1 Windows audit

A local evidence archive identifies exactly one FFmpeg executable:

- `ffmpeg-win-x86_64-v7.1.exe`, Gyan.dev 7.1 essentials build, SHA256 `2ce797a0f88d7f067180338fb227f7b1928ea727bd9a4d7a1d022f7c52af71a3`.
- Its own `-L` output declares **GNU GPL version 3 or later**.
- `-buildconf` confirms `--enable-gpl`, `--enable-version3`, `--enable-static`, `--enable-libx264`, and `--enable-libx265`; `--enable-nonfree` was **not reported**.
- Evidence also recorded `PyQt5==5.15.11`, `PyQt5-Qt5==5.15.2`, `PyQt5_sip==12.20.0`, and `imageio-ffmpeg==0.6.0`.

The precise **FFmpeg corresponding source**, its linked components, and exact Qt DLL/plugin licensing/source materials remain outstanding. A GPLv3 text without required source access is **not** sufficient to authorize publication. See [binary audit](FFMPEG_BINARY_AUDIT_0.3.1.md). This is distinct from a package named `imageio-ffmpeg` having a BSD-2-Clause Python wrapper.

## Release gate

**Local preview builds are permitted for functional testing, but do not publish the installer to GitHub Releases until:**

1. Finalize the chosen GPLv3 combined-distribution model, verify ownership and source-file license/attribution notices, provide access to complete corresponding source and update the installer-facing license screen (the current one is Apache-centric). Switching to an LGPL-licensed Qt binding (e.g. PySide6) may be evaluated as a separate code change rather than silently changing this validated GUI.
2. Exact Qt, imageio-ffmpeg and FFmpeg binaries are inventoried from the built distribution, with their versions, build flags and licensing verified.
3. Appropriate complete license texts, copyright notices, offer/source access where required, and attribution are included with the distributed installation.
4. A public release review confirms that no component was built using a non-redistributable configuration (e.g. an FFmpeg build with --enable-nonfree).
5. Manual Windows installation, conversion, upgrade and uninstall tests pass, and release artifacts have verifiable SHA256 hashes.

For the FFmpeg build configuration, run the packaged executable in the preview distribution with the -version flag and preserve its output in the release audit. For PyQt5 licensing, consult the official Riverbank Computing FAQ rather than assuming PyQt5 uses Qt's LGPL license.

The full distribution plan is **not yet approved**. Original Apache portions have not been relicensed; any new GPL-covered contributions must retain contributor attribution and appropriate license notices. No legal conclusion is implied by these notes.
