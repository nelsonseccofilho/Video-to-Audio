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

## Release gate

**Local preview builds are permitted for functional testing, but do not publish the installer to GitHub Releases until:**

1. The implications of packaging the **GPL v3 version of PyQt5** with this Apache-licensed upstream project are assessed and the chosen licensing/distribution model is documented. Switching to an LGPL-licensed Qt binding (e.g. PySide6) may be evaluated as a separate code change rather than silently changing this validated GUI.
2. Exact Qt, imageio-ffmpeg and FFmpeg binaries are inventoried from the built distribution, with their versions, build flags and licensing verified.
3. Appropriate complete license texts, copyright notices, offer/source access where required, and attribution are included with the distributed installation.
4. A public release review confirms that no component was built using a non-redistributable configuration (e.g. an FFmpeg build with --enable-nonfree).
5. Manual Windows installation, conversion, upgrade and uninstall tests pass, and release artifacts have verifiable SHA256 hashes.

For the FFmpeg build configuration, run the packaged executable in the preview distribution with the -version flag and preserve its output in the release audit. For PyQt5 licensing, consult the official Riverbank Computing FAQ rather than assuming PyQt5 uses Qt's LGPL license.

The application itself has not been relicensed and no legal conclusion is implied by these notes.
