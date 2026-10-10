# Release readiness audit — Video-to-Audio 0.3.1

Date: 2026-10-10. Scope: PR #1 (conversion/UX) and dependent PR #2 (Windows installer/i18n). This is an evidence-based audit, not an authorization to merge or distribute executables.

## Executive decision

- **Windows functionality: conditional PASS.** Installer and MP3 conversion/playback were evidenced in prior QA. The user explicitly confirmed the six 0.3.1 manual acceptance tasks, including installer localization, English/Portuguese language switching, language persistence and list clearing after success. This confirmation is user-reported rather than independently reproduced.
- **GitHub Actions: BLOCKED.** Most recent Windows and Ubuntu checks are marked failure. Both jobs report zero executed steps; downloadable logs returned 404. Runner, account/billing, repository policy and workflow configuration remain possible explanations. Do not claim a Python test failure or an infrastructure root cause without further evidence.
- **Public redistribution: BLOCKED.** The installer currently includes the Apache license original, an unofficial pt-BR translation and a preliminary third-party-notices file. These are not yet the complete compliance package for PyQt5, Qt, imageio-ffmpeg and the bundled FFmpeg executable.
- **Merge: HOLD.** Resolve CI and obtain relevant technical review; PR #1 must precede dependent PR #2. Do not publish a GitHub Release until the third-party licensing audit and final artifact validation are complete.

## Evidence matrix

| Item | Status | Evidence / limitations |
| --- | --- | --- |
| PR separation | Confirmed | PR #1 open against main; PR #2 open against PR #1 branch. Both unmerged during audit. |
| Windows syntax/automated tests | Conditional pass | User screenshot shows local 0.3.1 build completed successfully; build script blocks packaging if syntax/tests fail. Screenshot does not expose the full individual 35-test run. |
| Installed GUI and MP3 | Pass for observed example | Prior capture shows media converted to MP3 beside video, and user confirmed audible VLC playback. |
| Six 0.3.1 manual QA scenarios | User-reported pass | User explicitly confirmed installation, both installer language paths, live in-app language switching, conversion/list clearing, and preference persistence. |
| Uninstall and external media | Pass for observed files | Screenshots show application removed and MKV/MP3 files retained in their work folder. |
| Installed-app multi-folder/cancel/error and other formats | Partial | Automated tests exist, but complete end-user manual evidence for all combinations not established. |
| GitHub CI Windows + Ubuntu | Blocked | Recent Actions jobs failed with steps=[] and missing logs; root cause undetermined. |
| Apache translation | Documentation present, review pending | Full informational pt-BR text plus original authoritative English. Translation not legally reviewed. |
| Third-party obligations | Blocked | Preliminary notice is not the complete shipped license/source compliance package. |
| Versioned/reproducible build | Improvement needed | Requirement files use dependency version ranges; exact shipped binary versions, hashes and provenance not recorded in a reproducible release manifest. |
| Public installer verification | Pending | Locally built installer and printed SHA256 exist; release download integrity, signing/SmartScreen and final redistributable artifact QA pending. |

## Third-party license inventory

| Component | License implications and requirements |
| --- | --- |
| Original source and icons | Apache-2.0; retain authoritative English license, original author attributions, changes and any applicable upstream NOTICE. |
| PyQt5 | GPLv3 or commercial license. **Highest-priority licensing decision.** A redistributable combined application must meet GPL obligations if using the GPL binding, or use appropriately purchased commercial terms, or adopt another binding with its own compliance analysis. Do not assume Apache-2.0 alone is sufficient for the combined EXE. |
| Qt libraries/plugins from PyQt5 wheels | Inspect exact DLL/module inventory and applicable LGPL/GPL terms. Supply required license texts, notices, source access and relinking provisions where applicable. |
| imageio-ffmpeg Python wrapper | BSD-2-Clause. Reproduce required copyright, license and disclaimer when distributing binaries. |
| Bundled FFmpeg | Exact license depends on binary configure flags and included components. Inventory version, configuration, SHA256, source and potential GPL/nonfree features before distribution. |
| PyInstaller | GPL with bootloader exception allowing bundling and distribution subject to the application's dependencies. Not the primary licensing blocker. |
| Portuguese Apache translation | Informational, not legally binding; retain complete authoritative English original. Obtain independent translation/legal accuracy review before publicly treating it as complete. |

### Distribution strategy choices

A. Preserve PyQt5 under a documented GPLv3-compliant distribution model with corresponding source, notices and appropriate license terms for the combined work.
B. Investigate migration to PySide6 (LGPLv3/GPL/commercial options) in a **separate** engineering workstream with UI regression tests, plus LGPL compliance.
C. Obtain suitable commercial rights for the current stack, if a proprietary distribution is intended.

The Apache-2.0 original source is compatible with GPLv3 in relevant respects, but that does not make the GPL dependencies disappear. Have the chosen distribution strategy reviewed.

## Required next actions

1. Inspect failed GitHub check annotations and repository Actions/runner/billing settings. Resolve why both jobs have no executed steps, rerun and require passing Windows and Linux checks, or explicitly approve a documented alternative validation route.
2. Record a binding decision for PyQt5: GPLv3 compliance, alternate Qt binding, or commercial license.
3. Generate a software bill of materials for the actual Windows package. Capture exact installed dependency versions, Qt DLL and plugin inventory, FFmpeg version/configuration/hash and provenance.
4. Include complete applicable third-party license texts, attributions, source availability or offers and notices in the distributable installer. The existing THIRD_PARTY_NOTICES.md is currently a review checklist, not a compliance certificate.
5. Review the independent pt-BR legal translation and record that the English text remains authoritative.
6. Confirm remaining edge cases on final build: multi-folder destinations, errors/cancel, filename collisions, upgrade, uninstall and output playback.
7. Review and merge PR #1 before PR #2 **only when approved**. Retarget/rebase PR #2 onto main afterward. Conventional Commits remain mandatory.
8. Publish a versioned release only after these gates, with checksum, release notes and any unsigned-installer/SmartScreen disclosure.

## Windows evidence collection (run locally, no changes to WhisperX)

~~~powershell
cd D:\git\Video-to-Audio
.\.venv-build\Scripts\python.exe -m pip freeze
Get-ChildItem .\dist\Video-to-Audio -Filter "*ffmpeg*.exe" -Recurse | Select-Object FullName,Length
Get-ChildItem .\dist\Video-to-Audio -Filter "*ffmpeg*.exe" -Recurse | ForEach-Object { & $_.FullName -version | Select-Object -First 18 }
Get-FileHash .\dist\installer\Video-to-Audio-Setup-0.3.1.exe -Algorithm SHA256
~~~

## Primary references

- https://www.apache.org/foundation/license-faq.html
- https://riverbankcomputing.com/software
- https://en.riverbankcomputing.com/commercial/license-faq
- https://www.qt.io/development/open-source-lgpl-obligations
- https://github.com/imageio/imageio-ffmpeg/blob/main/LICENSE
- https://ffmpeg.org/legal.html
- https://pyinstaller.org/en/stable/license.html
- https://doc.qt.io/qtforpython-6/licenses.html

This is a technical evidence assessment, not legal advice or certification.

## Update — GPLv3 preparation approved (2026-10-10)

The project owner requested a **free and open-source** distribution and explicitly authorized pursuing the GPLv3 route with the existing PyQt5 dependency. The owner also reported a **US$20 GitHub balance** preventing hosted GitHub Actions use. Accordingly, the red remote check results are not treated as evidence of Python code failure; an accurately documented **local QA evidence path** is accepted for this workstream, subject to review of the actual records.

**Staged on PR #2:**
- Full GPLv3 text (LICENSES/GPL-3.0-only.txt) and imageio-ffmpeg BSD-2-Clause notice, preserving the upstream Apache-2.0 LICENSE unchanged.
- Proposed copyright/license boundaries in docs/OPEN_SOURCE_DISTRIBUTION_POLICY.md. This applies only to contributions under the respective contributors' control and does not unilaterally relicense other authors' works.
- Installer rules now copy the GPLv3 and BSD notice texts in addition to the existing Apache original, informational translation and preliminary notices.
- scripts/audit_windows_distribution.ps1 collects the actual package files and SHA256 values, FFmpeg version/buildconf/license output, exact Python build dependency versions and local tests into ignored dist/audit/.
- An additional static packaging test checks the presence of these materials.

**Remaining hard blockers for public EXE:** obtain the generated local audit report and independently inspect FFmpeg configure flags/source license, Qt/PyQt library notices and compliance, appropriate corresponding source delivery, contributor/license headers and UI licensing notices. Existing setup license page still represents Apache-2.0 and needs adjustment to describe the combined GPLv3 distribution accurately. The unofficial Portuguese translation remains subject to independent review.

**Decision:** GPLv3 strategy approved in principle; **public binary distribution NOT approved**. Keep both PRs open until final compliance, provenance and technical review. Local QA is a documented alternative while hosted runners are unavailable; it does not turn failed GitHub Actions checks green.
