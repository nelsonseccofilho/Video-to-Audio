# Open-source distribution policy — GPLv3 path

Date: 2026-10-10. Scope: Video-to-Audio 0.3.1 preview. **Not yet an approved public binary release.**

## Decision and ownership

The project will remain **free of charge** and provide its corresponding source code, using the open-source GPLv3 version of PyQt5 instead of purchasing Riverbank commercial licenses.

- **Original upstream:** source originally distributed by Nasir Shahbaz/NSTechBytes retains its Apache-2.0 copyright and license. The repository root LICENSE remains the full original Apache-2.0 text. Preserve attribution, notices, and modification records.
- **New contributions:** the authors of contributions made to this fork intend to license their **own copyrightable new contributions** under **GPL-3.0-only**. This does not claim ownership of, or rewrite the terms of, upstream contributions and third-party components. Confirm contributor rights and the source-file notices before finalizing this policy.
- **Combined distributed application:** must comply with GPLv3 conditions applicable to the combined GPL-covered work, while honoring separate Apache-2.0 notices and each third-party component's licensing conditions. Apache-2.0 is compatible with GPLv3 in this direction, not a blanket relicensing of other authors' works.
- **Full texts:** GNU GPLv3 at LICENSES/GPL-3.0-only.txt, original Apache-2.0 at LICENSE, imageio-ffmpeg BSD-2-Clause notice at LICENSES/BSD-2-Clause-imageio-ffmpeg.txt.
- The **FFmpeg binary itself** is separate from the BSD-licensed imageio-ffmpeg Python wrapper and may have LGPL, GPL and other optional dependency obligations.

GPLv3 allows commercial use and redistribution under its terms; "free" here means no fee for obtaining this application, **not** a prohibition on commercial activities.

## Conditions before publishing a Windows EXE

1. **Corresponding source:** offer machine-readable corresponding source of the exact shipped version, including build/installation scripts, and required library source or offers. Prefer an immutable release tag, a matching source archive and dependency materials. A moving main branch alone is insufficient.
2. **PyQt5 and Qt:** inventory the exact installed version, Qt binaries/modules/plugins, and all required GPL/LGPL notices, copyright, source/relinking and installation information obligations where relevant. A GPL main program does not automatically waive separate LGPL library obligations.
3. **FFmpeg and codecs:** record SHA256 and full '-version' and '-buildconf' output for the executable physically bundled in the installer. Check '--enable-gpl', '--enable-version3', '--enable-nonfree' and third-party codecs. Do **not** distribute nonredistributable builds. Match source and license obligations to the actual build.
4. **Other third parties:** include complete copyright/license/disclaimer texts for imageio-ffmpeg and other shipped tools/assets, including original icons and the PyInstaller bootloader as appropriate.
5. **UI notices:** make no-warranty, copyright, applicable GPL terms and exact source location easy to find. Evaluate an About/Licenses dialog and its interactive-interface notice obligations. A screen displaying only Apache does not explain all licenses in a combined GPL application.
6. **Reproducible build:** record exact package versions, revision, binaries/hashes, build script, final installer checksum, and acceptance-test evidence without exposing personal file paths or data.
7. **Third-party + translation review:** independently check the translated pt-BR informational Apache text and all licensing obligations. Preserve the authoritative English original.

No binary may be made publicly downloadable until the checks above are completed. No legal compliance certification is implied by this policy.

## CI exception — local QA

The user reports a GitHub billing balance restricting Actions. GitHub Windows and Ubuntu checks are red with empty steps and unavailable logs. This does NOT establish a source-test failure. Local QA can support a release, provided that exact test commands, results, source revision and binary hashes are recorded honestly. There must be **no fabricated green CI status**.

Run scripts/audit_windows_distribution.ps1 after building on the existing Windows machine. It writes files into ignored dist/audit/. Sanitize personal directory names before uploading any audit logs.

## Official references

- Apache License 2.0 / GPLv3 compatibility: https://www.apache.org/licenses/GPL-compatibility.html
- Full GPLv3: https://www.gnu.org/licenses/gpl-3.0.html
- GPLv3 source obligations: https://www.gnu.org/licenses/gpl-faq.en.html
- PyQt license: https://en.riverbankcomputing.com/software/pyqt
- Qt obligations: https://www.qt.io/development/open-source-lgpl-obligations
- FFmpeg license: https://ffmpeg.org/legal.html
- imageio-ffmpeg copyright/license: https://github.com/imageio/imageio-ffmpeg/blob/main/LICENSE

**Status: policy and evidence collection staged; merge/release still on hold. Not legal advice.**
