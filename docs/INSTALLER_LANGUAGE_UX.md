# UX decision — installer language and license (0.3.1 preview)

## Problem and evidence

The user tested the 0.3.0 installer after earlier Portuguese-language installations and reported confusing English/Portuguese language-picker behavior. Subsequent screenshots confirm that the wizard and license summary appear in pt-BR after choosing Portuguese, but the original English Apache 2.0 text appears immediately after the Portuguese summary. The desired outcome is predictable English-first behavior, easily changing to Portuguese, and Portuguese license content when Portuguese is chosen.

## Decision

1. **Language selection** — English is first and the default for each new installer launch (regardless of OS locale or previous installed language). Brazilian Portuguese is second. The initial Inno Setup language picker is **bilingual** so the language change is understandable before confirmation. The selected language applies to wizard pages as soon as **OK** is pressed. The stock Inno Setup language picker does **not** automatically translate all its own controls while the dropdown is open. Do **not** promise live reload of that specific native dialog or introduce an untested custom control merely for this effect.
2. **Desktop app** — English is the first-launch default when no explicit preference exists; Portuguese can be selected from the language control and the GUI re-renders immediately in both directions. A user-selected preference is persisted across launches. The installer and app language preferences are currently **independent**; installing in Portuguese does not silently overwrite a previously selected app language.
3. **License presentation** — the English installer shows the original Apache 2.0. The Portuguese installer shows a *complete independent informational translation*, with all nine numbered terms and the appendix, followed by the **unaltered complete English original**. A prominent disclaimer identifies English as the only authoritative text. Both license files are installed.
4. **Third-party licensing** — Apache 2.0 applies to the relevant project code; bundled PyQt5, Qt and FFmpeg may be subject to other obligations. The package also ships THIRD_PARTY_NOTICES.md. **Public binary distribution remains blocked** until full third-party redistribution review and verification of the Portuguese legal translation.

## Acceptance criteria

- [ ] Setup language picker opens with **English** selected even when 0.2.0/0.3.0 was installed in Portuguese.
- [ ] Initial picker provides bilingual guidance; choosing Portuguese and pressing OK translates subsequent wizard pages and prompts.
- [ ] Portuguese license page begins in Portuguese, contains sections 1–9 and the appendix, warns it is unofficial, and retains the English original in the same document.
- [ ] English license page begins directly with the official English Apache 2.0.
- [ ] App initially starts in English when there is no previously saved preference; manually switching English ↔ Portuguese immediately retranslates all custom GUI texts and retains selection after reopening.
- [ ] All user-selected videos, destination folders and conversion state survive a language change.
- [ ] Updated installer upgrades 0.3.0, preserving files and the existing program identity.
- [ ] Automated suite succeeds; Windows manual visual and audio QA succeeds.
- [ ] The translated license has been reviewed by a qualified professional before a public release, and all third-party notices/obligations have been resolved.

## Official sources

- [Inno Setup — LanguageDetectionMethod](https://jrsoftware.org/ishelp/topic_setup_languagedetectionmethod.htm): none selects the first listed language.
- [Inno Setup — UsePreviousLanguage](https://jrsoftware.org/ishelp/topic_setup_usepreviouslanguage.htm): previous installer choice otherwise may override the default.
- [Inno Setup — Languages section](https://jrsoftware.org/ishelp/topic_languagessection.htm): per-language wizard messages and license files.
- [Inno Setup — ShowLanguageDialog](https://jrsoftware.org/ishelp/topic_setup_showlanguagedialog.htm): initial choice and confirmation.
- [Apache Software Foundation — License FAQ](https://www.apache.org/foundation/license-faq.html): translations can be distributed for comprehension, but the English original is legally authoritative and must be retained with the package.

This is a documented design rationale, **not a claim that the revised 0.3.1 executable has been built or validated**.
